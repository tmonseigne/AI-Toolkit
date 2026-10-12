"""Prépare un candidat PDF avec recompression réversible des images Flate."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, IndirectObject, NameObject, NumberObject

from pdf_inventory import object_ids, sha256


# --------------------------------------------------
def canonical(value: Any) -> str | tuple[Any, ...]:
	"""
	Normalise des attributs d'image indépendamment des numéros d'objets.

	:param value: Valeur PDF sans référence cyclique.
	:return: Représentation comparable du contenu décodé.
	"""
	if isinstance(value, IndirectObject): value = value.get_object()
	if isinstance(value, list): return tuple(canonical(item) for item in value)
	if isinstance(value, dict):
		attributes = tuple(sorted((str(key), canonical(item)) for key, item in value.items() if key not in {"/Length", "/Filter", "/DecodeParms"}))
		if hasattr(value, "get_data"): return attributes, hashlib.sha256(value.get_data()).hexdigest()
		return attributes
	return str(value)


# --------------------------------------------------
def signatures(reader: PdfReader) -> tuple[list[str], list[tuple[str | tuple[Any, ...], str, int]]]:
	"""
	Contrôle images, masques, couleurs, géométrie et contenu des pages.

	:param reader: Document à contrôler.
	:return: Signatures des images et des pages.
	"""
	images = []
	for generation, number in object_ids(reader):
		obj = IndirectObject(number, generation, reader).get_object()
		if isinstance(obj, dict) and obj.get("/Subtype") == "/Image": images.append(repr(canonical(obj)))
	pages = []
	for page in reader.pages:
		content = page.get_contents()
		pages.append(
			(
				canonical([page.mediabox, page.cropbox, page.get("/Rotate", 0)]),
				hashlib.sha256(content.get_data() if content else b"").hexdigest(),
				len(page["/Annots"]) if "/Annots" in page else 0,
			)
		)
	return sorted(images), pages


# --------------------------------------------------
def png_payload(data: bytes) -> bytes:
	"""
	Extrait les blocs IDAT d'un PNG produit par Pillow.

	:param data: PNG valide encodé par le programme.
	:return: Flux Flate utilisant le prédicteur PNG.
	"""
	offset = 8
	parts = []
	while offset < len(data):
		size = struct.unpack(">I", data[offset : offset + 4])[0]
		if data[offset + 4 : offset + 8] == b"IDAT": parts.append(data[offset + 8 : offset + 8 + size])
		offset += size + 12
	return b"".join(parts)


# --------------------------------------------------
def optimize(source: Path, output: Path, max_image_bytes: int) -> dict[str, Any]:
	"""
	Réencode uniquement les images RGB/gris 8 bits sans perte.

	:param source: Original à préserver.
	:param output: Nouveau PDF ; le chemin doit être libre.
	:param max_image_bytes: Taille décodée maximale d'une image traitée.
	:return: Mesures et preuves mécaniques, sans verdict visuel.
	"""
	source_hash = sha256(source)
	reader = PdfReader(source)
	if reader.is_encrypted:
		raise ValueError("Encrypted PDF is not supported")
	for generation, number in object_ids(reader):
		obj = IndirectObject(number, generation, reader).get_object()
		if isinstance(obj, dict) and (obj.get("/Type") == "/Sig" or "/ByteRange" in obj):
			raise ValueError("Signed PDF must not be rewritten")
	before = signatures(reader)
	changes = []
	for generation, number in object_ids(reader):
		obj = IndirectObject(number, generation, reader).get_object()
		if not isinstance(obj, dict) or obj.get("/Subtype") != "/Image": continue
		channels = {"/DeviceRGB": 3, "/DeviceGray": 1}.get(str(obj.get("/ColorSpace")))
		if obj.get("/Filter") != "/FlateDecode" or not channels or obj.get("/BitsPerComponent") != 8: continue
		width, height = int(obj["/Width"]), int(obj["/Height"])
		if not 0 < width * height * channels <= max_image_bytes: continue
		pixels = obj.get_data()
		if len(pixels) != width * height * channels: continue
		buffer = BytesIO()
		with Image.frombytes("RGB" if channels == 3 else "L", (width, height), pixels) as image:
			image.save(buffer, format="PNG", optimize=True, compress_level=9)
		plain, predicted = zlib.compress(pixels, 9), png_payload(buffer.getvalue())
		predictor, encoded = (15, predicted) if len(predicted) < len(plain) else (1, plain)
		old_size = len(obj._data)
		if len(encoded) >= old_size: continue
		obj._data = encoded
		obj[NameObject("/DecodeParms")] = DictionaryObject(
			{
				NameObject("/Predictor"): NumberObject(predictor),
				NameObject("/Colors"): NumberObject(channels),
				NameObject("/BitsPerComponent"): NumberObject(8),
				NameObject("/Columns"): NumberObject(width),
			}
		)
		obj.decoded_self = None
		if obj.get_data() != pixels:
			raise ValueError("Decoded image pixels changed")
		changes.append(
			{
				"object": number,
				"generation": generation,
				"before_bytes": old_size,
				"after_bytes": len(encoded),
				"pixel_sha256": hashlib.sha256(pixels).hexdigest(),
				"predictor": predictor,
			}
		)
	writer = PdfWriter()
	writer.clone_document_from_reader(reader)
	buffer = BytesIO()
	writer.write(buffer)
	candidate = buffer.getvalue()
	reopened = PdfReader(BytesIO(candidate))
	if signatures(reopened) != before:
		raise ValueError("Image or page invariants changed")
	if sha256(source) != source_hash:
		raise ValueError("Source changed during processing")
	gain = source.stat().st_size - len(candidate)
	result = {
		"source": str(source),
		"source_sha256": source_hash,
		"before_bytes": source.stat().st_size,
		"after_bytes": len(candidate),
		"gain_bytes": gain,
		"changes": changes,
		"pages": len(reopened.pages),
		"image_and_page_checks_passed": True,
		"visual_review": "pending",
		"status": "candidate" if gain > 0 else "rejected_no_gain",
	}
	if gain > 0:
		with output.open("xb") as stream: stream.write(candidate)
		result.update(output=str(output), output_sha256=sha256(output))
	return result


# --------------------------------------------------
def main():
	"""Prépare un candidat séparé ; aucun remplacement n'est effectué."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("source", type=Path)
	parser.add_argument("--output", required=True, type=Path)
	parser.add_argument("--manifest", required=True, type=Path)
	parser.add_argument("--max-image-bytes", type=int, default=90_000_000)
	args = parser.parse_args()
	paths = [path.resolve() for path in (args.source, args.output, args.manifest)]
	if len(set(paths)) != 3 or args.output.exists() or args.manifest.exists():
		parser.error("Source, output and manifest must be distinct; outputs must not exist")
	if args.max_image_bytes <= 0: parser.error("Maximum decoded image size must be positive")
	args.output.parent.mkdir(parents=True, exist_ok=True)
	args.manifest.parent.mkdir(parents=True, exist_ok=True)
	result = optimize(paths[0], paths[1], args.max_image_bytes)
	with args.manifest.open("x", encoding="utf-8", newline="\n") as stream: stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__": main()
