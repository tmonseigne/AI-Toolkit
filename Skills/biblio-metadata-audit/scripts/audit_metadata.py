"""Inventorier les métadonnées Zotero sans modifier la bibliothèque."""

from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


# --------------------------------------------------
def inventory(database: Path, library_id: int | None = None) -> list[dict[str, Any]]:
	"""Lire un instantané cohérent des notices actives en lecture seule."""
	connection = sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True)
	connection.execute("PRAGMA query_only=ON")
	connection.execute("BEGIN")
	items = {}
	for item_id, key, library, kind in connection.execute(
		"SELECT itemID,key,libraryID,typeName FROM items "
		"JOIN itemTypes USING(itemTypeID) "
		"WHERE itemID NOT IN (SELECT itemID FROM deletedItems) "
		"AND typeName NOT IN ('attachment','note','annotation')"
	):
		items[item_id] = {
			"key": key,
			"library": library,
			"type": kind,
			"fields": {},
			"creators": [],
		}
	for item_id, field, value in connection.execute(
		"SELECT itemID,fieldName,value FROM itemData JOIN fields USING(fieldID) JOIN itemDataValues USING(valueID)"
	):
		if item_id in items: items[item_id]["fields"][field] = value
	for item_id, first, last, mode, role in connection.execute(
		"SELECT itemID,firstName,lastName,fieldMode,creatorType "
		"FROM itemCreators JOIN creators USING(creatorID) "
		"JOIN creatorTypes USING(creatorTypeID) ORDER BY itemID,orderIndex"
	):
		if item_id in items:
			items[item_id]["creators"].append(
				{
					"firstName": first,
					"lastName": last,
					"fieldMode": mode,
					"role": role,
				}
			)
	connection.rollback()
	connection.close()
	return [item for item in items.values() if library_id is None or item["library"] == library_id]


# --------------------------------------------------
def normalized(value: str) -> str:
	"""Normaliser un texte pour comparer les métadonnées, sans changer sa valeur."""
	value = unicodedata.normalize("NFKD", value).casefold()
	return "".join(c for c in value if c.isalnum() and not unicodedata.combining(c))


# --------------------------------------------------
def initials(value: str) -> bool:
	"""
	Détecter une initiale en tête du prénom.

	Un prénom complet suivi d'initiales intermédiaires est accepté, conformément
	à la préférence de l'utilisateur ; « Paul A. » ne nécessite pas de correction.

	:param value: Prénom tel qu'il est renseigné dans Zotero.
	:return: ``True`` si la première composante est une initiale.
	"""
	parts = re.findall(r"[^\W\d_]+", value, re.UNICODE)
	return bool(parts and len(parts[0]) == 1)


# --------------------------------------------------
def request_json(url: str) -> dict[str, Any]:
	"""Lire les métadonnées publiques avec un délai réseau borné."""
	request = urllib.request.Request(url, headers={"User-Agent": "ZoteroMetadataAudit/1.0"})
	with urllib.request.urlopen(request, timeout=20) as response: return json.load(response)


# --------------------------------------------------
def resolve(item: dict[str, Any]) -> dict[str, Any]:
	"""Chercher une notice externe, sans supposer que le titre suffit à l'identifier."""
	fields = item["fields"]
	doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", fields.get("DOI", "").strip(), flags=re.I)
	url = (
		"https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
		if doi
		else (
			"https://api.crossref.org/works?"
			+ urllib.parse.urlencode(
				{
					"query.title": fields.get("title", ""),
					"rows": 3,
				}
			)
		)
	)
	try:
		result = request_json(url)["message"]
		candidates = [result] if doi else result.get("items", [])
		match = max(
			candidates, key=lambda m: SequenceMatcher(None, normalized(fields.get("title", "")), normalized((m.get("title") or [""])[0])).ratio(), default={}
		)
		score = SequenceMatcher(None, normalized(fields.get("title", "")), normalized((match.get("title") or [""])[0])).ratio()
		local = [c for c in item["creators"] if c["role"] == "author"]
		remote = match.get("author", [])
		author_match = bool(local and remote and normalized(local[0]["lastName"]) == normalized(remote[0].get("family", "")))
		return {
			"url": url,
			"metadata": match,
			"score": round(score, 4),
			"identity": "doi_title" if doi and score >= 0.90 else ("title_author_candidate" if not doi and score >= 0.96 and author_match else "uncertain"),
			"error": "",
		}
	except Exception as error:
		# DataCite peut porter des DOI absents de Crossref.
		if doi:
			dc_url = "https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="")
			try:
				data = request_json(dc_url)["data"]["attributes"]
				return {"url": dc_url, "datacite": data, "identity": "datacite_review", "error": ""}
			except Exception:
				pass
		return {"url": url, "identity": "unavailable", "error": str(error)}


# --------------------------------------------------
def prepare(output: Path, database: Path | None = None, library_id: int | None = None, offline: bool = False, retry_unavailable: bool = False):
	"""
	Enregistrer l'inventaire et les propositions dans le dossier de travail.

	:param output: Dossier de sortie, extérieur au dossier Zotero.
	"""
	if database is not None and output.resolve().is_relative_to(Path(database).resolve().parent):
		raise ValueError("Output must be outside the Zotero data directory.")
	output.mkdir(parents=True, exist_ok=True)
	snapshot = output / "inventaire.json"
	if database is not None:
		records = inventory(database, library_id)
		snapshot.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
	else:
		records = json.loads(snapshot.read_text(encoding="utf-8"))
		if library_id is not None: records = [record for record in records if record["library"] == library_id]
	if len({record["library"] for record in records}) > 1:
		raise ValueError("Select one library with --library-id to avoid ambiguous item keys.")
	articles = [r for r in records if r["type"] == "journalArticle"]
	cache_path = output / "sources.json"
	sources = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
	signatures = {
		r["key"]: json.dumps(
			{"fields": {name: r["fields"].get(name, "") for name in ("title", "DOI", "date")}, "creators": r["creators"]}, sort_keys=True, ensure_ascii=False
		)
		for r in articles
	}
	sources = {key: value for key, value in sources.items() if key in signatures and value.get("input_signature") == signatures[key]}
	pending = [r for r in articles if r["key"] not in sources or (retry_unavailable and sources[r["key"]]["identity"] == "unavailable")] if not offline else []

	# --------------------------------------------------
	def paced_resolve(item: dict[str, Any]) -> dict[str, Any]:
		"""Espacer les reprises après une limitation du service bibliographique."""
		if retry_unavailable: time.sleep(1)
		return resolve(item)

	with ThreadPoolExecutor(max_workers=1 if retry_unavailable else 2) as pool:
		for item, source in zip(pending, pool.map(paced_resolve, pending)):
			source["input_signature"] = signatures[item["key"]]
			sources[item["key"]] = source
	if not offline: cache_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
	issues = []
	full_names = {}
	for record in records:
		for creator in record["creators"]:
			first = creator["firstName"]
			if (
				creator["role"] in {"author", "presenter"}
				and creator["fieldMode"] == 0
				and first
				and not initials(first)
				and not any(c in first for c in ["Ã", "Â", "�"])
			):
				full_names.setdefault(normalized(creator["lastName"]), {}).setdefault(first, record["key"])

	# --------------------------------------------------
	def add(item: dict[str, Any], field: str, old: Any, new: Any, status: str, reason: str, source: str = ""):
		"""Ajouter une ligne traçable au plan de correction."""
		issues.append(
			{
				"key": item["key"],
				"title": item["fields"].get("title", ""),
				"field": field,
				"before": old,
				"after": new,
				"status": status,
				"reason": reason,
				"source": source,
			}
		)

	for item in articles:
		fields = item["fields"]
		source = sources.get(item["key"], {"identity": "local_only", "url": "", "error": "Vérification externe non exécutée."})
		metadata = source.get("metadata", {})
		if source.get("datacite"):
			dc = source["datacite"]
			if normalized(dc["titles"][0]["title"]) == normalized(fields.get("title", "")):
				metadata = {
					"DOI": dc["doi"],
					"title": [dc["titles"][0]["title"]],
					"issued": {"date-parts": [[dc["publicationYear"]]]},
					"author": [{"given": c.get("givenName", "").strip(), "family": c.get("familyName", "").strip()} for c in dc.get("creators", [])],
				}
		trusted = source["identity"] in {"doi_title", "verified_manual"} or bool(source.get("datacite") and metadata)
		url = source["url"]
		if not trusted:
			add(
				item,
				"identification",
				fields.get("DOI", ""),
				metadata.get("DOI", "") if source["identity"] == "title_author_candidate" else "",
				"à vérifier",
				"Correspondance à confirmer ; score du titre : " + str(source.get("score", "indisponible")) + ". " + source.get("error", ""),
				url,
			)
		if metadata.get("type") and metadata["type"] != "journal-article" and source["identity"] in {"doi_title", "title_author_candidate"}:
			add(
				item,
				"itemType",
				item["type"],
				{"proceedings-article": "conferencePaper", "posted-content": "preprint"}.get(metadata["type"], metadata["type"]),
				"proposition",
				"La source décrit un autre type de document : " + metadata["type"] + ". Contrôler la version avant changement.",
				url,
			)
		doi = fields.get("DOI", "")
		if doi.startswith("http") and trusted: add(item, "DOI", doi, metadata["DOI"], "proposition", "Retirer le préfixe URL du DOI.", url)
		external = {
			"publicationTitle": html.unescape((metadata.get("container-title") or [""])[0]),
			"volume": metadata.get("volume", ""),
			"issue": metadata.get("issue", ""),
			"pages": metadata.get("page", "") or metadata.get("article-number", ""),
			"ISSN": ", ".join(dict.fromkeys(metadata.get("ISSN", []))),
			"url": "https://doi.org/" + metadata.get("DOI", "") if metadata.get("DOI") else "",
			"journalAbbreviation": (metadata.get("short-container-title") or [""])[0],
			"abstractNote": html.unescape(re.sub(r"<[^>]*>", "", metadata.get("abstract", ""))).strip(),
		}
		parts = metadata.get("issued", {}).get("date-parts", [[]])[0]
		if parts: external["date"] = "-".join(str(v).zfill(4 if n == 0 else 2) for n, v in enumerate(parts))
		for field in ["title", "date", "publicationTitle", "DOI", "volume", "issue", "pages", "ISSN", "abstractNote", "language", "url", "journalAbbreviation"]:
			if not fields.get(field):
				candidate = source["identity"] == "title_author_candidate"
				value = external.get(field, "") if trusted or candidate else ""
				if field == "DOI" and candidate: value = metadata.get("DOI", "")
				add(
					item,
					field,
					"",
					value,
					("proposition") if value else "manquant",
					(
						"Valeur fournie par le dépôt DOI."
						if trusted
						else "Valeur de la notice candidate : confirmer version, année et identité avant application."
					)
					if value
					else "Non renseigné ; disponibilité et pertinence à confirmer (numéro, pages ou DOI parfois inexistants).",
					url if value else "",
				)
		journal = external["publicationTitle"]
		if trusted and journal and fields.get("publicationTitle") and fields["publicationTitle"] != journal:
			add(
				item,
				"publicationTitle",
				fields["publicationTitle"],
				journal,
				"proposition",
				"Titre du dépôt Crossref ; valider le nom officiel et historique chez l'éditeur.",
				url,
			)
		local_authors = [c for c in item["creators"] if c["role"] == "author"]
		remote_authors = metadata.get("author", [])
		truncated = any(normalized(c["lastName"]) in {"others", "etal"} for c in local_authors)
		if truncated:
			replacement = [{"firstName": a.get("given", ""), "lastName": a.get("family", a.get("name", ""))} for a in remote_authors]
			add(
				item,
				"authors",
				local_authors,
				replacement if trusted else [],
				"proposition" if trusted else "à vérifier",
				"Liste tronquée par un faux auteur « others/et al. » ; rétablir l'ordre complet et conserver les autres rôles.",
				url,
			)
		if not local_authors: add(item, "authors", [], [], "manquant", "Aucun auteur renseigné.")
		for position, author in enumerate(local_authors):
			if author["fieldMode"] == 1 or normalized(author["lastName"]) in {"others", "etal"}: continue
			first = author["firstName"]
			needs = initials(first) or not first or any(c in first + author["lastName"] for c in ["Ã", "Â", "�"])
			remote = next((a for a in remote_authors if normalized(a.get("family", "")) == normalized(author["lastName"])), {}) if trusted else {}
			new_first = remote.get("given", "")
			# Une différence d'initiale ou de prénom n'est jamais développée automatiquement.
			compatible = bool(new_first and normalized(first)[:1] == normalized(new_first)[:1])
			if needs:
				proposed = new_first if compatible and new_first != first and not initials(new_first) else ""
				local_source = ""
				if not proposed and first and not any(c in first for c in ["Ã", "Â", "�"]):
					parts = re.findall(r"[^\W\d_]+", first, re.UNICODE)
					matches = []
					for name, key in full_names.get(normalized(author["lastName"]), {}).items():
						full_parts = re.findall(r"[^\W\d_]+", name, re.UNICODE)
						if len(parts) == len(full_parts) and all(
							normalized(a) == normalized(b) if len(a) > 1 else normalized(a) == normalized(b)[:1] for a, b in zip(parts, full_parts)
						):
							matches.append((name, key))
					if len(matches) == 1: proposed, local_source = matches[0]
				add(
					item,
					"author[" + str(position + 1) + "].firstName",
					first,
					proposed,
					"proposition" if proposed else "à vérifier",
					"Auteur : "
					+ author["lastName"]
					+ ". "
					+ (
						("Prénom complet compatible dans la notice locale " + local_source + "; confirmer qu'il s'agit de la même personne avant application.")
						if local_source
						else "Prénom abrégé, absent ou mal encodé ; conserver les initiales non résolues sans inventer de prénom."
					),
					"inventaire.json" if local_source else url,
				)
		for field, value in fields.items():
			if field == "abstractNote": continue
			if "zotero" in value.casefold():
				add(
					item,
					field,
					value,
					value,
					"information",
					"Zotero dans le catalogue décrit la provenance, pas la revue ou le DOI."
					if field == "libraryCatalog"
					else "Valeur Zotero à contrôler dans ce champ.",
				)
			if field == "publicationTitle" and re.search(r"arxiv:|https?://|\.pdf$", value, re.I):
				add(
					item,
					field,
					value,
					"",
					"à vérifier",
					"Ce champ ressemble à un dépôt/identifiant plutôt qu'à une revue ; contrôler le type de document.",
					fields.get("url", ""),
				)
			if field in {"ISSN", "ISBN"}:
				tokens = re.findall(r"\d{4}-?\d{3}[\dXx]", value) if field == "ISSN" else []
				if len(tokens) != len(set(tokens)):
					add(item, field, value, ", ".join(dict.fromkeys(tokens)), "proposition", "Identifiant répété à dédupliquer.")
		if not fields.get("publicationTitle") and fields.get("pages", "").isdigit():
			add(
				item,
				"pages",
				fields["pages"],
				"",
				"à vérifier",
				"Le nombre isolé peut être un nombre total de pages plutôt qu'une pagination ou un numéro d'article ; consulter le document.",
			)
	journal_groups = {}
	for item in articles:
		journal = item["fields"].get("publicationTitle", "")
		group = normalized(re.sub(r"^the\s+", "", journal, flags=re.I))
		if journal: journal_groups.setdefault(group, {}).setdefault(journal, []).append(item)
	for variants in journal_groups.values():
		if len(variants) > 1:
			choices = " / ".join(variants)
			for journal, notices in variants.items():
				for item in notices:
					add(
						item,
						"publicationTitle (variantes locales)",
						journal,
						choices,
						"à vérifier",
						"Variantes de casse/ponctuation/article initial présentes ; sélectionner le titre officiel après contrôle de l'éditeur.",
					)
	titles = {}
	for item in records: titles.setdefault(normalized(item["fields"].get("title", "")), []).append(item)
	for duplicates in titles.values():
		if len(duplicates) > 1:
			for item in duplicates:
				add(
					item,
					"doublon potentiel",
					item["key"],
					", ".join(d["key"] for d in duplicates if d != item),
					"à vérifier",
					"Même titre ; vérifier version, année et pièces jointes avant toute fusion.",
				)
	applied_path = output / "modifications-appliquees.json"
	applied = json.loads(applied_path.read_text(encoding="utf-8")) if applied_path.exists() else {}
	if applied.get("phase") == "committed":
		notices = {r["key"]: r for r in records}
		resolved = set()
		latest_changes = {(change["key"], change["field"]): change for change in applied["changes"]}
		for change in latest_changes.values():
			record = notices.get(change["key"])
			if not record: continue
			field = change["field"]
			if field == "itemType":
				value = record["type"]
			elif field == "authors":
				value = [{"firstName": c["firstName"], "lastName": c["lastName"]} for c in record["creators"] if c["role"] == "author"]
				expected_authors = [{"firstName": c["firstName"], "lastName": c["lastName"]} for c in change["after"]]
				if value == expected_authors: resolved.add((change["key"], field))
				continue
			elif field.startswith("author["):
				position = int(re.fullmatch(r"author\[(\d+)\]\.firstName", field)[1]) - 1
				authors = [c for c in record["creators"] if c["role"] == "author"]
				value = authors[position]["firstName"] if position < len(authors) else None
			else:
				value = record["fields"].get(field, "")
				if field == "date": value = value.split(" ", 1)[-1]
			if value == change["after"]: resolved.add((change["key"], field))
		issues = [i for i in issues if (i["key"], i["field"]) not in resolved]
	# Les indices externes enrichissent le motif sans devenir des corrections applicables.
	hints_path = output / "auteurs-reference.json"
	hints = json.loads(hints_path.read_text(encoding="utf-8")).get("hints", {}) if hints_path.exists() else {}
	for issue in issues:
		hint = hints.get(issue["key"] + "|" + issue["field"])
		if hint and hint.get("before") == issue["before"]:
			candidate = hint.get("candidate", "")
			issue["name_hint"] = hint
			if hint["confidence"] == "prénom dans l’article" and hint.get("reviewed") is True:
				issue["after"] = candidate
				issue["status"] = "vérifié"
			author_label = issue["reason"].split(". ", 1)[0] + ". "
			issue["reason"] = (
				author_label
				+ (("Piste : " + candidate + ". ") if candidate else "")
				+ "Niveau : "
				+ hint["confidence"]
				+ ". "
				+ hint["evidence"]
				+ " Aucun changement automatique sur cette base."
			)
			if hint.get("source"):
				issue["metadata_source"] = issue["source"]
				issue["source"] = hint["source"]
	# Une forme déjà conforme au texte de l'article ne nécessite aucune correction.
	issues = [
		issue
		for issue in issues
		if not (
			issue.get("name_hint", {}).get("confidence") in {"forme publiée", "prénom composé publié", "forme d’usage officielle"}
			and issue["name_hint"]["candidate"].removesuffix(" (à conserver)") == issue["before"]
		)
	]
	# PubMed complète les preuves et distingue les synthèses des résumés originaux.
	pubmed_path = output / "sources-pubmed.json"
	pubmed = json.loads(pubmed_path.read_text(encoding="utf-8")) if pubmed_path.exists() else {}
	summary_path = output / "syntheses-fr.json"
	summaries = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
	for issue in issues:
		match = pubmed.get(issue["key"], {})
		if match.get("identity") != "verified":
			if match.get("identity") == "candidate" and match.get("manual_identity_reason"):
				issue["reason"] += " " + match["manual_identity_reason"]
				issue["source"] = match.get("source", issue["source"])
			if match.get("identity") == "not_found" and issue["status"] == "manquant" and sources.get(issue["key"], {}).get("identity") != "verified_manual":
				issue["reason"] += " Recherche PubMed effectuée : aucune correspondance sûre trouvée."
			continue
		metadata = match["metadata"]["fields"]
		if issue["field"] == "abstractNote" and not issue["before"]:
			issue["source"] = match["source"]
			if summaries.get(issue["key"]):
				issue["after"] = summaries[issue["key"]]
				issue["status"] = "proposition"
				issue["reason"] = "Résumé original disponible dans PubMed ; synthèse française proposée, sans application automatique."
			else:
				issue["reason"] += " Aucun résumé exploitable dans la notice PubMed contrôlée."
		elif issue["status"] == "manquant" and not metadata.get(issue["field"]):
			issue["reason"] += " Ce champ n’est pas renseigné dans la notice PubMed concordante."
			issue["source"] = match["source"]
	issues = [issue for issue in issues if not (issue["field"] == "identification" and pubmed.get(issue["key"], {}).get("identity") == "verified")]
	# Les champs vides explicitement contrôlés ne sont pas des erreurs à corriger.
	accepted_empty_path = output / "champs-valides-sans-valeur.json"
	if accepted_empty_path.exists():
		accepted_empty = json.loads(accepted_empty_path.read_text(encoding="utf-8"))
		accepted_pairs = {(entry["key"], entry["field"]) for entry in accepted_empty if entry["before"] == "" and entry.get("recheck_due") is None}
		issues = [issue for issue in issues if not ((issue["key"], issue["field"]) in accepted_pairs and issue["before"] == "" and issue["after"] == "")]
	# Conserver les particularités vérifiées sans recréer des erreurs résolues.
	annotations_path = output / "annotations-verification.json"
	if annotations_path.exists():
		active_keys = {record["key"] for record in records}
		issues.extend(annotation for annotation in json.loads(annotations_path.read_text(encoding="utf-8")) if annotation["key"] in active_keys)
	plan = {
		"scope": str(len(articles)) + " articles actifs ; autres types inventoriés et doublons de titres signalés",
		"counts": dict(Counter(r["type"] for r in records)),
		"statuses": dict(Counter(i["status"] for i in issues)),
		"source_identities": dict(Counter(s["identity"] for s in sources.values())),
		"pubmed_identities": dict(Counter(s["identity"] for s in pubmed.values())),
		"issues": issues,
	}
	if applied:
		plan["applied_changes"] = applied["count"]
		plan["application_journal"] = "modifications-appliquees.json"
	plan["authors"] = {
		"notices_with_initials_or_encoding": len({i["key"] for i in issues if i["field"].startswith("author[")}),
		"proposed_expansions": sum(i["field"].startswith("author[") and bool(i["after"]) for i in issues),
		"unresolved_names": sum(i["field"].startswith("author[") and not i["after"] for i in issues),
		"truncated_lists": sum(i["field"] == "authors" and "tronquée" in i["reason"] for i in issues),
	}
	(output / "corrections.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
	rows = []
	for issue in issues:
		# --------------------------------------------------
		def display(value: Any) -> str:
			"""Échapper une valeur pour son affichage dans le rapport HTML."""
			return html.escape(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))

		parsed = urllib.parse.urlsplit(issue["source"])
		safe_source = (
			issue["source"]
			if parsed.scheme in {"http", "https"}
			or (not parsed.scheme and not parsed.netloc and not issue["source"].startswith(("/", "\\\\")) and ".." not in Path(issue["source"]).parts)
			else ""
		)
		source_cell = '<a href="' + html.escape(safe_source, quote=True) + '">Source</a>' if safe_source else "—"
		rows.append(
			"<tr>"
			+ "".join("<td>" + display(issue[k]) + "</td>" for k in ["key", "title", "field", "before", "after", "status", "reason"])
			+ '<td>'
			+ source_cell
			+ '</td></tr>'
		)
	missing = {
		f: sum(not r["fields"].get(f) for r in articles)
		for f in ["date", "publicationTitle", "DOI", "volume", "issue", "pages", "ISSN", "abstractNote", "language", "url", "journalAbbreviation"]
	}
	template = Path(__file__).resolve().parent.parent / "assets" / "metadata_report.html"
	report = template.read_text(encoding="utf-8")
	replacements = {
		"{{missing}}": html.escape(json.dumps(missing, ensure_ascii=False)),
		"{{rows}}": "".join(rows),
		"{{article_count}}": str(len(articles)),
		"{{other_count}}": str(len(records) - len(articles)),
		"{{application_summary}}": "Audit en lecture seule ; aucune écriture Zotero par ce script.",
	}
	for marker, value in replacements.items(): report = report.replace(marker, value)
	(output / "rapport.html").write_text(report + "\n", encoding="utf-8", newline="\n")
	print(json.dumps({k: v for k, v in plan.items() if k != "issues"}, ensure_ascii=True))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Audit Zotero metadata without modifying the library.")
	parser.add_argument("--output", type=Path, required=True)
	parser.add_argument("--database", type=Path, help="Refresh the inventory from this read-only database.")
	parser.add_argument("--library-id", type=int)
	parser.add_argument("--offline", action="store_true", help="Do not query external bibliographic services.")
	parser.add_argument("--retry-unavailable", action="store_true")
	args = parser.parse_args()
	prepare(args.output, database=args.database, library_id=args.library_id, offline=args.offline, retry_unavailable=args.retry_unavailable)
