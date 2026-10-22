"""Conserve les microtests et calcule leur progression sans dépendance externe."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

DOMAINS = ("logic", "algorithms", "architecture", "knowledge")
IMMUTABLE_FIELDS = (
	"schema_version", "id", "created_at", "domain", "concept", "format",
	"level", "question", "expected_answer", "rubric",
)


# --------------------------------------------------
def validate(record: dict) -> None:
	"""
	Vérifie le contrat d’une séance avant de l’utiliser.

	:param record: Séance décodée depuis JSON.
	:raises ValueError: Si une valeur manque ou contredit le statut.
	"""
	if not isinstance(record, dict) or type(record.get("schema_version")) is not int or record["schema_version"] != 1:
		raise ValueError("Unsupported session schema")
	for key in (*IMMUTABLE_FIELDS, "status", "answer", "score", "assisted", "hints", "feedback", "skip_reason", "duration_seconds"):
		if key not in record:
			raise ValueError(f"Missing required field: {key}")
	if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", str(record.get("id", ""))):
		raise ValueError("Invalid session id")
	timestamp = datetime.fromisoformat(record["created_at"])
	if timestamp.tzinfo is None:
		raise ValueError("created_at must include a timezone")
	if record.get("domain") not in DOMAINS:
		raise ValueError("Invalid domain")
	if type(record.get("level")) is not int or not 1 <= record["level"] <= 5:
		raise ValueError("level must be an integer between 1 and 5")
	for key in ("concept", "format", "question", "expected_answer"):
		if not isinstance(record.get(key), str) or not record[key].strip():
			raise ValueError(f"{key} must be a nonempty string")
	rubric = record.get("rubric")
	if not isinstance(rubric, list) or len(rubric) != 3 or any(
		not isinstance(item, str) or not item.strip() for item in rubric
	):
		raise ValueError("rubric must contain three nonempty criteria")
	if type(record.get("assisted")) is not bool:
		raise ValueError("assisted must be a boolean")
	hints = record.get("hints")
	if not isinstance(hints, list) or any(not isinstance(item, str) for item in hints):
		raise ValueError("hints must be a list of strings")
	if hints and not record["assisted"]:
		raise ValueError("Hints require assisted=true")
	for key in ("answer", "feedback", "skip_reason"):
		if key not in record or (record[key] is not None and not isinstance(record[key], str)):
			raise ValueError(f"{key} must be a string or null")
	score = record.get("score")
	if score is not None and (type(score) is not int or score not in (0, 1, 2)):
		raise ValueError("score must be 0, 1, 2 or null")
	duration = record.get("duration_seconds")
	if duration is not None and (type(duration) is not int or duration < 0):
		raise ValueError("duration_seconds must be a nonnegative integer or null")
	status = record.get("status")
	if status not in ("pending", "completed", "skipped"):
		raise ValueError("Invalid session status")
	if status != "completed" and score is not None:
		raise ValueError("Only completed sessions can have a score")
	if status == "completed" and not (record.get("feedback") or "").strip():
		raise ValueError("Completed sessions require feedback")
	if score is not None and not (record.get("answer") or "").strip():
		raise ValueError("Scored sessions require an answer")
	if status == "skipped" and not (record.get("skip_reason") or "").strip():
		raise ValueError("Skipped sessions require a reason")


# --------------------------------------------------
def read_records(root: Path) -> list[dict]:
	"""
	Charge toutes les archives valides dans leur ordre chronologique.

	:param root: Racine stable de l’historique.
	:return: Séances triées par instant de création et identifiant.
	"""
	records = []
	for path in sorted((root / "_artifacts/daily-dev-test/sessions").glob("*.json")):
		try:
			record = json.loads(path.read_text(encoding="utf-8"))
			validate(record)
			if path.stem != record["id"]:
				raise ValueError("Session id differs from filename")
			records.append(record)
		except (ValueError, KeyError, TypeError) as error:
			raise ValueError(f"Invalid archive {path}: {error}") from error
	return sorted(records, key=lambda item: (datetime.fromisoformat(item["created_at"]), item["id"]))


# --------------------------------------------------
def build_context(records: list[dict]) -> dict:
	"""
	Rejoue les résultats pour proposer les niveaux et la rotation.

	:param records: Séances classées chronologiquement.
	:return: Contexte sans les solutions préparées.
	"""
	levels = dict.fromkeys(DOMAINS, 3)
	streaks = {domain: [0, 0] for domain in DOMAINS}
	last_seen = dict.fromkeys(DOMAINS, -1)
	for index, record in enumerate(records):
		domain = record["domain"]
		last_seen[domain] = index
		if record["status"] != "completed":
			continue
		streak = streaks[domain]
		score = record["score"]
		if record["assisted"] or score is None or record["level"] != levels[domain]:
			streak[:] = [0, 0]
			continue
		streak[0] = streak[0] + 1 if score == 2 else 0
		streak[1] = streak[1] + 1 if score < 2 else 0
		if streak[0] >= 3 or streak[1] >= 2:
			levels[domain] = max(1, min(5, levels[domain] + (1 if score == 2 else -1)))
			streak[:] = [0, 0]
	summary_keys = ("id", "created_at", "domain", "concept", "format", "level", "status", "score", "assisted")
	return {
		"session_count": len(records),
		"levels": levels,
		"suggested_domain": min(DOMAINS, key=lambda domain: last_seen[domain]),
		"recent": [{key: record[key] for key in summary_keys} for record in records[-30:]],
		"pending": [{key: record[key] for key in (*summary_keys, "question")} for record in records if record["status"] == "pending"],
	}


# --------------------------------------------------
def render_record(record: dict) -> str:
	"""
	Produit une fiche, en cachant la solution tant que la séance attend.

	:param record: Séance validée.
	:return: Markdown pédagogique avec saut de ligne final.
	"""
	lines = [
		f"# Microtest {record['id']}", "",
		f"Domaine : {record['domain']} · Niveau : {record['level']}/5 · Budget : 5 minutes maximum.",
		"", record["question"], "",
	]
	if record["status"] == "completed":
		score = "Non noté" if record["score"] is None else f"{record['score']}/2"
		lines += ["## Réponse", "", record["answer"] or "Aucune tentative fournie.", ""]
		if record["hints"]:
			lines += ["## Aides fournies", "", *record["hints"], ""]
		lines += ["## Correction", "", f"Résultat : {score}. Aide : {'oui' if record['assisted'] else 'non'}.", "", record["feedback"], ""]
	elif record["status"] == "skipped":
		lines += ["Séance passée sans notation.", "", record["skip_reason"], ""]
	else:
		lines += ["En attente de réponse ; correction disponible après la tentative.", ""]
	return "\n".join(lines)


# --------------------------------------------------
def atomic_write(path: Path, content: str) -> None:
	"""
	Remplace un fichier via un fichier temporaire voisin.

	:param path: Destination dans les dossiers d’artefacts.
	:param content: Contenu UTF-8 avec fins de ligne LF.
	"""
	path.parent.mkdir(parents=True, exist_ok=True)
	temporary = path.with_suffix(path.suffix + ".tmp")
	temporary.write_text(content, encoding="utf-8", newline="\n")
	temporary.replace(path)


# --------------------------------------------------
def save_record(root: Path, source: Path, records: list[dict]) -> dict:
	"""
	Archive une séance et génère sa fiche sans réécrire une séance close.

	:param root: Racine de l’historique.
	:param source: Fichier d’entrée préparé par l’agent.
	:param records: Archives existantes validées.
	:return: Chemins écrits et progression recalculée.
	"""
	record = json.loads(source.read_text(encoding="utf-8"))
	validate(record)
	previous = next((item for item in records if item["id"] == record["id"]), None)
	if previous is not None:
		if previous["status"] != "pending" and previous != record:
			raise ValueError("Closed sessions cannot be overwritten")
		if any(previous[key] != record[key] for key in IMMUTABLE_FIELDS):
			raise ValueError("The original exercise cannot be changed")
	if record["status"] == "pending" and any(
		item["status"] == "pending" and item["id"] != record["id"] for item in records
	):
		raise ValueError("Resume or skip the existing pending session first")
	archive = root / "_artifacts/daily-dev-test/sessions" / f"{record['id']}.json"
	output = root / "_output/daily-dev-test" / f"{record['id']}.md"
	atomic_write(archive, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
	atomic_write(output, render_record(record))
	return {"archive": str(archive), "output": str(output), "context": build_context(read_records(root))}


# --------------------------------------------------
def main() -> int:
	"""
	Exécute la consultation ou la sauvegarde demandée.

	:return: Code de sortie nul en cas de réussite.
	"""
	parser = argparse.ArgumentParser(description="Manage daily development practice history")
	parser.add_argument("command", choices=("context", "save"))
	parser.add_argument("--root", required=True, type=Path)
	parser.add_argument("--input", type=Path)
	args = parser.parse_args()
	try:
		root = args.root.resolve()
		records = read_records(root)
		if args.command == "save":
			if args.input is None:
				parser.error("save requires --input")
			result = save_record(root, args.input, records)
		else:
			result = build_context(records)
		print(json.dumps(result, ensure_ascii=False, indent=2))
	except (OSError, ValueError, KeyError, TypeError) as error:
		print(f"History error: {error}", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
