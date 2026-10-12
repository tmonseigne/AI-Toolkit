"""Appliquer le lot de métadonnées explicitement validé, Zotero fermé."""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import shutil
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_metadata import inventory


# --------------------------------------------------
def assert_zotero_closed():
	"""Refuser une écriture lorsque le client Zotero est actif."""
	result = subprocess.run(
		["powershell.exe", "-NoProfile", "-Command", "@(Get-Process -Name zotero -ErrorAction SilentlyContinue).Count"],
		capture_output=True,
		text=True,
		check=True,
	)
	if result.stdout.strip() != "0":
		raise RuntimeError("Zotero must remain closed while applying the manifest.")


# --------------------------------------------------
def stored_date(value: str) -> str:
	"""
	Construire la date multipartite interne à partir d'une date ISO.

	:param value: Année ou date ISO validée.
	:return: Composante de tri et texte affiché dans Zotero.
	"""
	if not re.fullmatch(r"\d{4}(?:-\d{2})?(?:-\d{2})?", value):
		raise ValueError("Invalid ISO date: " + value)
	parts = value.split("-")
	return "-".join(parts + ["00"] * (3 - len(parts))) + " " + value


# --------------------------------------------------
def current_value(connection: sqlite3.Connection, item_id: int, field: str) -> str | list[dict[str, str | int]]:
	"""Lire la valeur d'un champ ou d'un auteur ciblé par le plan."""
	if field == "itemType":
		return connection.execute(
			"SELECT typeName FROM items JOIN itemTypes USING(itemTypeID) WHERE itemID=?",
			(item_id,),
		).fetchone()[0]
	if field == "authors":
		return [
			{"firstName": first, "lastName": last, "fieldMode": mode, "role": role}
			for first, last, mode, role in connection.execute(
				"SELECT firstName,lastName,fieldMode,creatorType FROM itemCreators "
				"JOIN creators USING(creatorID) JOIN creatorTypes USING(creatorTypeID) "
				"WHERE itemID=? AND creatorType='author' ORDER BY orderIndex",
				(item_id,),
			)
		]
	match = re.fullmatch(r"author\[(\d+)\]\.firstName", field)
	if match:
		rows = connection.execute(
			"SELECT firstName FROM itemCreators JOIN creators USING(creatorID) "
			"JOIN creatorTypes USING(creatorTypeID) WHERE itemID=? "
			"AND creatorType='author' ORDER BY orderIndex",
			(item_id,),
		).fetchall()
		return rows[int(match[1]) - 1][0]
	row = connection.execute(
		"SELECT value FROM itemData JOIN fields USING(fieldID) JOIN itemDataValues USING(valueID) WHERE itemID=? AND fieldName=?",
		(item_id, field),
	).fetchone()
	return row[0] if row else ""


# --------------------------------------------------
def expected_value(change: dict[str, Any]) -> str | list[dict[str, str | int]]:
	"""Construire la valeur interne attendue pour contrôler l'écriture."""
	if change["field"] == "authors":
		return [
			{"firstName": c["firstName"], "lastName": c["lastName"], "fieldMode": c.get("fieldMode", 0 if c["firstName"] else 1), "role": "author"}
			for c in change["after"]
		]
	return stored_date(change["after"]) if change["field"] == "date" else change["after"]


# --------------------------------------------------
def apply_transaction(path: Path, changes: list[dict[str, Any]], library_id: int) -> int:
	"""
	Appliquer atomiquement les seuls champs validés après précontrôle.

	:param path: Base fermée ou copie de validation.
	:param changes: Lignes de statut « vérifié » revues par l'utilisateur.
	:return: Nombre de notices modifiées.
	"""
	connection = sqlite3.connect(path, timeout=2)
	connection.execute("PRAGMA foreign_keys=ON")
	connection.execute("BEGIN EXCLUSIVE")
	try:
		items = {}
		for change in changes:
			row = connection.execute(
				"SELECT itemID,itemTypeID FROM items JOIN libraries USING(libraryID) "
				"WHERE key=? AND libraryID=? AND editable=1 AND items.itemID NOT IN "
				"(SELECT itemID FROM deletedItems)",
				(change["key"], library_id),
			).fetchone()
			if not row:
				raise ValueError("Unavailable item: " + change["key"])
			items[change["key"]] = row[0]
			if current_value(connection, row[0], change["field"]) != change["before"]:
				raise ValueError("Value conflict: " + change["key"] + " / " + change["field"])
		for change in sorted(changes, key=lambda x: 0 if x["after"] == "" else (1 if x["field"] == "itemType" else 2)):
			item_id = items[change["key"]]
			field = change["field"]
			value = change["after"]
			if value == "" and field not in {"itemType", "authors"} and not field.startswith("author["):
				field_id = connection.execute("SELECT fieldID FROM fields WHERE fieldName=?", (field,)).fetchone()[0]
				connection.execute("DELETE FROM itemData WHERE itemID=? AND fieldID=?", (item_id, field_id))
				continue
			if field == "authors":
				if (
					not isinstance(value, list)
					or not value
					or any(
						not isinstance(c.get("firstName"), str) or not isinstance(c.get("lastName"), str) or not (c["firstName"] or c["lastName"])
						for c in value
					)
				):
					raise ValueError("Invalid author list.")
				author_type = connection.execute("SELECT creatorTypeID FROM creatorTypes WHERE creatorType='author'").fetchone()[0]
				new_authors = []
				for creator in expected_value(change):
					existing = connection.execute(
						"SELECT creatorID FROM creators WHERE firstName=? AND lastName=? AND fieldMode=?",
						(creator["firstName"], creator["lastName"], creator["fieldMode"]),
					).fetchone()
					creator_id = (
						existing[0]
						if existing
						else connection.execute(
							"INSERT INTO creators(firstName,lastName,fieldMode) VALUES(?,?,?)",
							(creator["firstName"], creator["lastName"], creator["fieldMode"]),
						).lastrowid
					)
					new_authors.append((creator_id, author_type))
				original = connection.execute(
					"SELECT creatorID,creatorTypeID FROM itemCreators WHERE itemID=? ORDER BY orderIndex",
					(item_id,),
				).fetchall()
				replacement = []
				inserted = False
				for creator_id, role_id in original:
					if role_id == author_type:
						if not inserted:
							replacement.extend(new_authors)
							inserted = True
					else:
						replacement.append((creator_id, role_id))
				if not inserted: replacement = new_authors + replacement
				connection.execute("DELETE FROM itemCreators WHERE itemID=?", (item_id,))
				connection.executemany(
					"INSERT INTO itemCreators(itemID,creatorID,creatorTypeID,orderIndex) VALUES(?,?,?,?)",
					[(item_id, creator_id, role_id, index) for index, (creator_id, role_id) in enumerate(replacement)],
				)
				continue
			if not isinstance(value, str) or not value:
				raise ValueError("Reviewed value must be a nonempty string.")
			if field == "itemType":
				type_id = connection.execute(
					"SELECT itemTypeID FROM itemTypes WHERE typeName=?",
					(value,),
				).fetchone()[0]
				invalid = connection.execute(
					"SELECT fieldName FROM itemData JOIN fields USING(fieldID) "
					"WHERE itemID=? AND fieldID NOT IN "
					"(SELECT fieldID FROM itemTypeFields WHERE itemTypeID=?)",
					(item_id, type_id),
				).fetchall()
				if invalid:
					raise ValueError("Item type conversion requires field migration: " + str(invalid))
				connection.execute("UPDATE items SET itemTypeID=? WHERE itemID=?", (type_id, item_id))
				continue
			match = re.fullmatch(r"author\[(\d+)\]\.firstName", field)
			if match:
				author = connection.execute(
					"SELECT creatorID,lastName,fieldMode,creatorTypeID,orderIndex "
					"FROM itemCreators JOIN creators USING(creatorID) "
					"JOIN creatorTypes USING(creatorTypeID) WHERE itemID=? "
					"AND creatorType='author' ORDER BY orderIndex",
					(item_id,),
				).fetchall()[int(match[1]) - 1]
				existing = connection.execute(
					"SELECT creatorID FROM creators WHERE firstName=? AND lastName=? AND fieldMode=?",
					(value, author[1], author[2]),
				).fetchone()
				creator_id = (
					existing[0]
					if existing
					else connection.execute(
						"INSERT INTO creators(firstName,lastName,fieldMode) VALUES(?,?,?)",
						(value, author[1], author[2]),
					).lastrowid
				)
				# Ne jamais modifier un créateur partagé avec une autre notice.
				connection.execute(
					"UPDATE itemCreators SET creatorID=? WHERE itemID=? AND creatorID=? AND creatorTypeID=? AND orderIndex=?",
					(creator_id, item_id, author[0], author[3], author[4]),
				)
				continue
			field_id = connection.execute("SELECT fieldID FROM fields WHERE fieldName=?", (field,)).fetchone()[0]
			valid = connection.execute(
				"SELECT 1 FROM itemTypeFields WHERE itemTypeID=(SELECT itemTypeID FROM items WHERE itemID=?) AND fieldID=?",
				(item_id, field_id),
			).fetchone()
			if not valid:
				raise ValueError("Field incompatible with item type: " + field)
			if field == "date": value = stored_date(value)
			existing = connection.execute("SELECT valueID FROM itemDataValues WHERE value=?", (value,)).fetchone()
			value_id = (
				existing[0]
				if existing
				else connection.execute(
					"INSERT INTO itemDataValues(value) VALUES(?)",
					(value,),
				).lastrowid
			)
			connection.execute(
				"INSERT INTO itemData(itemID,fieldID,valueID) VALUES(?,?,?) ON CONFLICT(itemID,fieldID) DO UPDATE SET valueID=excluded.valueID",
				(item_id, field_id, value_id),
			)
		for item_id in items.values():
			connection.execute(
				"UPDATE items SET dateModified=CURRENT_TIMESTAMP, clientDateModified=CURRENT_TIMESTAMP,synced=0 WHERE itemID=?",
				(item_id,),
			)
		for change in changes:
			expected = expected_value(change)
			if current_value(connection, items[change["key"]], change["field"]) != expected:
				raise AssertionError("Stored value does not match the manifest.")
		if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
			raise AssertionError("Database integrity check failed.")
		if connection.execute("PRAGMA foreign_key_check").fetchall():
			raise AssertionError("Foreign key check failed.")
		connection.commit()
		return len(items)
	except Exception:
		connection.rollback()
		raise
	finally:
		connection.close()


# --------------------------------------------------
def read_manifest(path: Path, database: Path) -> dict[str, Any]:
	"""
	Contrôler le périmètre exact du lot et refuser les champs ambigus.

	:param path: Manifeste relu contenant les valeurs avant et après.
	:param database: Base visée explicitement par la commande.
	:return: Manifeste contrôlé, limité à une bibliothèque.
	"""
	manifest = json.loads(path.read_text(encoding="utf-8"))
	if manifest.get("reviewed") is not True:
		raise ValueError("The manifest must be explicitly reviewed.")
	if Path(manifest["database"]).resolve() != database.resolve():
		raise ValueError("Manifest database does not match --database.")
	if not isinstance(manifest.get("library_id"), int):
		raise ValueError("The manifest must identify one library.")
	changes = manifest["changes"]
	if not changes:
		raise ValueError("The manifest contains no changes.")
	pairs = set()
	for change in changes:
		pair = (change["key"], change["field"])
		if pair in pairs:
			raise ValueError("Duplicate item/field pair in the manifest.")
		pairs.add(pair)
		if not change.get("source") or not change.get("reason"):
			raise ValueError("Each change requires a source and a reason.")
		if change["field"] in {"key", "libraryID", "itemID"}:
			raise ValueError("Item identity fields cannot be changed.")
		if change["before"] == change["after"]:
			raise ValueError("The manifest contains an unchanged value.")
	return manifest


# --------------------------------------------------
def save_json(path: Path, data: Any):
	"""
	Enregistrer atomiquement le suivi en UTF-8 avec des fins de ligne LF.

	:param path: Fichier JSON destiné au suivi.
	:param data: Données sérialisables.
	"""
	temporary = path.with_suffix(path.suffix + ".tmp")
	temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
	temporary.replace(path)


# --------------------------------------------------
def main(database: Path, output: Path, manifest_path: Path, commit: bool = False):
	"""
	Valider sur copie puis appliquer seulement sur demande explicite.

	:param database: Base Zotero existante.
	:param output: Dossier de suivi, extérieur aux données Zotero.
	:param manifest_path: Lot précis relu et lié à la base.
	:param commit: Autorisation technique d'écrire dans la base source.
	"""
	database = database.resolve(strict=True)
	if output.resolve().is_relative_to(database.parent):
		raise ValueError("Output must be outside the Zotero data directory.")
	manifest = read_manifest(manifest_path, database)
	library_id = manifest["library_id"]
	changes = manifest["changes"]
	# Une validation sans application peut lire Zotero ouvert grâce à la sauvegarde SQLite.
	if not commit:
		with tempfile.TemporaryDirectory(prefix="zotero-validation-") as directory:
			validation = Path(directory) / "validation.sqlite"
			with contextlib.closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as source:
				with contextlib.closing(sqlite3.connect(validation)) as copy: source.backup(copy)
			count = apply_transaction(validation, changes, library_id)
		print(json.dumps({"phase": "validated_copy", "changes": len(changes), "notices": count}))
		return
	assert_zotero_closed()
	output.mkdir(parents=True, exist_ok=True)
	journal_path = output / "modifications-appliquees.json"
	existing = json.loads(journal_path.read_text(encoding="utf-8")) if journal_path.exists() else {}
	if existing and existing.get("phase") != "committed":
		raise RuntimeError("Unfinished journal: inspect the previous operation before retrying.")
	if existing.get("database") and (Path(existing["database"]).resolve() != database or existing.get("library_id") != library_id):
		raise ValueError("The journal belongs to another database or library.")
	timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
	history = output / "historique" / timestamp
	history.mkdir(parents=True, exist_ok=False)
	shutil.copy2(manifest_path, history / "reviewed_changes.json")
	for filename in (
		"corrections.json",
		"inventaire.json",
		"rapport.html",
		"sources.json",
		"modifications-appliquees.json",
		"syntheses-fr.json",
		"provenance-syntheses-fr.json",
	):
		original = output / filename
		if original.exists(): shutil.copy2(original, history / filename)
	backup_path = history / "zotero-before.sqlite"
	with contextlib.closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as source:
		with contextlib.closing(sqlite3.connect(backup_path)) as backup: source.backup(backup)
	validation = history / "zotero-validation.sqlite"
	shutil.copy2(backup_path, validation)
	count = apply_transaction(validation, changes, library_id)
	assert_zotero_closed()
	all_changes = existing.get("changes", []) + changes
	journal = {
		**existing,
		"database": str(database),
		"library_id": library_id,
		"phase": "prepared",
		"count": len(all_changes),
		"notices": len({c["key"] for c in all_changes}),
		"changes": all_changes,
		"batches": existing.get("batches", [])
		+ [
			{
				"applied_at_utc": timestamp,
				"backup": str(backup_path),
				"count": len(changes),
				"notices": count,
			}
		],
	}
	save_json(journal_path, journal)
	apply_transaction(database, changes, library_id)
	journal["phase"] = "committed"
	save_json(journal_path, journal)
	save_json(output / "inventaire.json", inventory(database, library_id))
	print(json.dumps({"phase": "committed", "changes": len(changes), "notices": count, "backup": str(backup_path)}))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Validate reviewed changes on a copy; commit only when explicitly requested.")
	parser.add_argument("--database", type=Path, required=True)
	parser.add_argument("--output", type=Path, required=True)
	parser.add_argument("--manifest", type=Path, required=True)
	parser.add_argument("--commit", action="store_true", help="Apply the reviewed manifest to the source database.")
	arguments = parser.parse_args()
	main(arguments.database, arguments.output, arguments.manifest, commit=arguments.commit)
