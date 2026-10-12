"""Inventorie les PDF et leurs flux embarqués sans modifier les sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.generic import IndirectObject


# --------------------------------------------------
def object_ids(reader: PdfReader) -> list[tuple[int, int]]:
	"""
	Énumère les objets ordinaires et ceux des flux compactés.

	:param reader: Lecteur du document PDF.
	:return: Couples génération, numéro d'objet.
	"""
	identifiers = {(generation, number) for generation, entries in reader.xref.items() for number in entries if number > 0 and generation != 65535}
	identifiers.update((0, number) for number in reader.xref_objStm)
	return sorted(identifiers)


# --------------------------------------------------
def sha256(path: Path) -> str:
	"""
	Calcule une empreinte sans charger le fichier complet en mémoire.

	:param path: Fichier à lire.
	:return: Empreinte SHA-256 hexadécimale.
	"""
	with path.open("rb") as stream: return hashlib.file_digest(stream, "sha256").hexdigest()


# --------------------------------------------------
def inspect_pdf(path: Path) -> dict[str, Any]:
	"""
	Mesure les flux physiques ; leur présence ne prouve pas leur affichage.

	:param path: PDF source.
	:return: Inventaire sérialisable, avec erreur éventuelle par document.
	"""
	result = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
	try:
		reader = PdfReader(path)
		result["encrypted"] = reader.is_encrypted
		if reader.is_encrypted:
			raise ValueError("Encrypted PDF is not supported")
		result["pages"] = len(reader.pages)
		streams = []
		for generation, number in object_ids(reader):
			obj = IndirectObject(number, generation, reader).get_object()
			if not hasattr(obj, "get_data"): continue
			streams.append(
				{
					"object": number,
					"generation": generation,
					"type": str(obj.get("/Type", "")),
					"subtype": str(obj.get("/Subtype", "")),
					"compressed_bytes": len(obj._data),
					"filter": str(obj.get("/Filter", "")),
					"width": int(obj.get("/Width", 0)),
					"height": int(obj.get("/Height", 0)),
					"bits": int(obj.get("/BitsPerComponent", 0)),
					"color_space": str(obj.get("/ColorSpace", "")),
				}
			)
		result["streams"] = sorted(streams, key=lambda entry: entry["compressed_bytes"], reverse=True)
		result["image_bytes"] = sum(entry["compressed_bytes"] for entry in streams if entry["subtype"] == "/Image")
		result["stream_bytes"] = sum(entry["compressed_bytes"] for entry in streams)
	except Exception as error:
		result["error"] = str(error)
	return result


# --------------------------------------------------
def main():
	"""Écrit l'inventaire de fichiers ou de répertoires explicitement désignés."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("inputs", nargs="+", type=Path)
	parser.add_argument("--output", required=True, type=Path)
	args = parser.parse_args()
	paths = set()
	for source in args.inputs:
		if source.is_dir():
			paths.update(path.resolve() for path in source.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf")
		elif source.is_file():
			paths.add(source.resolve())
		else:
			parser.error(f"Input does not exist: {source}")
	if args.output.resolve() in paths: parser.error("Output must not overwrite an input")
	rows = [inspect_pdf(path) for path in sorted(paths)]
	groups = {}
	for row in rows: groups.setdefault(row["sha256"], []).append(row["path"])
	result = {"files": rows, "pdf_bytes": sum(row["bytes"] for row in rows), "exact_duplicates": [group for group in groups.values() if len(group) > 1]}
	args.output.parent.mkdir(parents=True, exist_ok=True)
	with args.output.open("x", encoding="utf-8", newline="\n") as stream: stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__": main()
