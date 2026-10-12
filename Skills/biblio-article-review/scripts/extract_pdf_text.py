"""Extraire le texte des pages d'un PDF sans modifier le document."""

import argparse
from pathlib import Path

from pypdf import PdfReader


# --------------------------------------------------
def extract(source: Path, output: Path):
	"""
	Conserver les repères de pages dans une extraction textuelle.

	:param source: PDF disponible localement.
	:param output: Nouveau fichier UTF-8, distinct de la source.
	"""
	if source.resolve() == output.resolve() or output.exists():
		raise FileExistsError("Output must be a new file distinct from the source.")
	reader = PdfReader(source)
	output.parent.mkdir(parents=True, exist_ok=True)
	with output.open("x", encoding="utf-8", newline="\n") as stream:
		for number, page in enumerate(reader.pages, 1):
			stream.write(f"\n=== PAGE {number} ===\n\n")
			stream.write((page.extract_text() or "").rstrip() + "\n")
	print(f"Extracted {len(reader.pages)} pages to {output}")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Extract local PDF text with page markers; OCR is not performed.")
	parser.add_argument("--source", type=Path, required=True)
	parser.add_argument("--output", type=Path, required=True)
	args = parser.parse_args()
	extract(args.source, args.output)
