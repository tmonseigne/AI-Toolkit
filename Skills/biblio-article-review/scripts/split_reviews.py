"""Extrait les fiches numérotées du recueil Synesthesia, sans modifier la source."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

REVIEW_HEADING = re.compile(r"^### Fiche (\d+) : (.+)$")
NEXT_SECTION = re.compile(r"^(?:## |### Fiche \d+ : |### Références complémentaires)")
DOI = re.compile(r"10\.\d{4,9}/[^\s)\]>]+", flags=re.IGNORECASE)


# --------------------------------------------------
def slugify(value: str) -> str:
	"""Produit un nom ASCII stable à partir d'un titre de fiche."""
	plain = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
	plain = plain.replace(r"\)", ")")
	slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
	return slug[:85].rstrip("-")


# --------------------------------------------------
def clean_body(lines: list[str]) -> str:
	"""Retire seulement les séparateurs de recueil en fin de fiche."""
	body = lines.copy()
	while body and not body[0].strip():
		body.pop(0)
	while body and not body[-1].strip():
		body.pop()
	while body and body[-1].strip() == "---":
		body.pop()
		while body and not body[-1].strip():
			body.pop()
	return "\n".join(body).rstrip() + "\n"


# --------------------------------------------------
def main(source: Path, destination: Path):
	"""Écrit une fiche par section numérotée et un index de correspondance."""
	lines = source.read_text(encoding="utf-8-sig").splitlines()
	reviews: list[tuple[int, str, list[str]]] = []
	number: int | None = None
	title = ""
	body: list[str] = []

	for line in lines:
		match = REVIEW_HEADING.match(line)
		if match:
			if number is not None: reviews.append((number, title, body))
			number = int(match.group(1))
			title = match.group(2).replace(r"\)", ")")
			body = []
			continue
		if number is not None and NEXT_SECTION.match(line):
			reviews.append((number, title, body))
			number = None
			body = []
			continue
		if number is not None: body.append(line)

	if number is not None: reviews.append((number, title, body))
	numbers = [item[0] for item in reviews]
	if not numbers or numbers != sorted(set(numbers)):
		raise ValueError("Missing, duplicated or unordered review sections.")
	filenames = [f"{number:02d}-{slugify(title)}-fiche.md" for number, title, _ in reviews]
	if any((destination / name).exists() for name in filenames + ["_index.md"]):
		raise FileExistsError("Existing reviews or index would be overwritten.")

	destination.mkdir(parents=True, exist_ok=True)
	index = [
		"# Fiches de lecture — fichiers individuels",
		"",
		f"Extraction de {len(reviews)} fiches depuis le recueil source.",
		"Le contenu scientifique est conservé ; seuls les niveaux de titre et les séparateurs sont adaptés.",
		"",
		"| N° | Fichier | DOI de la référence principale |",
		"| :-- | :-- | :-- |",
	]
	for number, title, raw_body in reviews:
		filename = f"{number:02d}-{slugify(title)}-fiche.md"
		body_text = clean_body(raw_body)
		body_text = re.sub(r"(?m)^#### (.+)$", r"## \1", body_text)
		content = f"# Fiche {number} — {title}\n\n*Extrait du recueil {source.name}.*\n\n" + body_text
		(destination / filename).write_text(content, encoding="utf-8", newline="\n")
		reference_line = next(
			(line for line in body_text.splitlines() if line.startswith("- **DOI / Lien :**")),
			"",
		)
		dois = list(dict.fromkeys(DOI.findall(reference_line)))
		doi_cell = ", ".join(dois) if dois else "Non indiqué"
		index.append(f"| {number} | [{title}]({filename}) | {doi_cell} |")
	(destination / "_index.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
	print(f"Created {len(reviews)} reviews and one index in {destination}")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Split numbered French review sections without modifying the source.")
	parser.add_argument("--source", type=Path, required=True)
	parser.add_argument("--output", type=Path, required=True)
	arguments = parser.parse_args()
	main(arguments.source, arguments.output)
