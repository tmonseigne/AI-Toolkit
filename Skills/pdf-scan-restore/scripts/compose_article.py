"""Recompose une transcription validée en colonnes, avec figures PDF vectorielles."""

from __future__ import annotations

import argparse
import hashlib
import json
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
	BaseDocTemplate,
	Flowable,
	Frame,
	FrameBreak,
	Image,
	KeepTogether,
	NextPageTemplate,
	PageBreak,
	PageTemplate,
	Paragraph,
	Table,
	TableStyle,
)


class VectorFigure(Flowable):
	"""Réserve l'espace d'une figure PDF et mémorise sa position absolue."""

	# --------------------------------------------------
	def __init__(self, path: Path, width: float, placements: list[tuple[int, float, float, float, Path]]):
		"""
		Calcule une taille conservant le rapport d'aspect.

		:param path: PDF d'une seule page, sans rotation.
		:param width: Largeur de composition en points.
		:param placements: Positions collectées lors de la mise en page.
		"""
		super().__init__()
		self.path = path
		self.placements = placements
		reader = PdfReader(path)
		if len(reader.pages) != 1 or reader.pages[0].get("/Rotate", 0) != 0:
			raise ValueError("Vector figure must contain one unrotated page")
		box = reader.pages[0].mediabox
		self.width = width
		self.height = width * float(box.height) / float(box.width)

	# --------------------------------------------------
	def draw(self):
		"""Consigne la position ; l'insertion vectorielle suit la composition."""
		x, y = self.canv.absolutePosition(0, 0)
		self.placements.append((self.canv.getPageNumber(), x, y, self.width, self.path))


# --------------------------------------------------
def compose(data: dict[str, Any], base: Path, scientific_font: Path | None = None) -> bytes:
	"""
	Compose les blocs validés sans correction scientifique implicite.

	:param data: Transcription et paramètres définis dans la référence du skill.
	:param base: Répertoire de résolution des ressources.
	:param scientific_font: Police Unicode TTF fournie explicitement.
	:return: Octets PDF composés.
	"""
	if scientific_font: pdfmetrics.registerFont(TTFont("Scientific", str(scientific_font)))
	settings = data.get("layout", {})
	width, height = settings.get("page_size", [595.276, 841.89])
	margin, gutter = settings.get("margin", 22), settings.get("gutter", 18)
	columns = settings.get("columns", 2)
	if columns not in (1, 2) or margin < 0 or gutter < 0 or min(width, height) <= 2 * margin:
		raise ValueError("Invalid page layout")
	column_width = (width - 2 * margin - gutter * (columns - 1)) / columns
	if column_width <= 0:
		raise ValueError("Column width must be positive")
	body = ParagraphStyle(
		"Body", fontName="Times-Roman", fontSize=12, leading=13.1, alignment=4, firstLineIndent=12, spaceAfter=4, allowWidows=0, allowOrphans=0
	)
	styles = {
		"paragraph": body,
		"heading": ParagraphStyle(
			"Heading", parent=body, fontName="Times-Bold", firstLineIndent=0, alignment=0, spaceBefore=14, spaceAfter=4, keepWithNext=True
		),
		"caption": ParagraphStyle("Caption", parent=body, fontSize=9.2, leading=10.4, firstLineIndent=0, alignment=0, spaceAfter=6),
		"reference": ParagraphStyle("Reference", parent=body, fontSize=10, leading=11.2, leftIndent=17, firstLineIndent=-17, spaceAfter=5),
	}

	# --------------------------------------------------
	def paragraph(block: dict[str, Any], kind: str = "paragraph") -> Paragraph:
		"""
		Échappe le texte ; le balisage n'est accepté que s'il est explicite.

		:param block: Texte brut ou balisage ReportLab contrôlé.
		:param kind: Style du paragraphe.
		:return: Paragraphe prêt à composer.
		"""
		if "markup" in block:
			markup = block["markup"]
		else:
			fragments = []
			for character in block["text"]:
				try:
					character.encode("cp1252")
					fragments.append(escape(character))
				except UnicodeEncodeError:
					if not scientific_font:
						raise ValueError("Unicode scientific text requires --scientific-font or explicit markup")
					fragments.append(f'<font name="Scientific">{escape(character)}</font>')
			markup = "".join(fragments).replace("\n", "<br/>")
		return Paragraph(markup, styles[kind])

	frames = [
		Frame(
			margin + index * (column_width + gutter),
			margin,
			column_width,
			height - 2 * margin,
			id=f"column-{index}",
			leftPadding=0,
			rightPadding=0,
			topPadding=0,
			bottomPadding=0,
		)
		for index in range(columns)
	]
	full_frame = Frame(margin, margin, width - 2 * margin, height - 2 * margin, id="full", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
	buffer = BytesIO()
	document = BaseDocTemplate(buffer, pagesize=(width, height), title=data["title"], author=data.get("authors", ""), pageCompression=1)
	document.addPageTemplates([PageTemplate(id="Columns", frames=frames), PageTemplate(id="Full", frames=[full_frame])])
	story, placements = [], []
	for block in data["blocks"]:
		kind = block["kind"]
		if kind in styles:
			story.append(paragraph(block, kind))
		elif kind == "frame_break":
			story.append(FrameBreak())
		elif kind == "page_break":
			story.append(PageBreak())
		elif kind == "layout":
			if block["mode"] not in {"full", "columns"}:
				raise ValueError("Unknown layout mode")
			story.extend([NextPageTemplate("Full" if block["mode"] == "full" else "Columns"), PageBreak()])
		elif kind in {"figure", "table"}:
			block_width = block.get("width", column_width)
			caption = paragraph({"text": block["caption"]}, "caption")
			if kind == "figure":
				path = (base / block["path"]).resolve()
				if path.suffix.lower() == ".pdf":
					graphic = VectorFigure(path, block_width, placements)
				else:
					graphic = Image(str(path))
					graphic.drawHeight *= block_width / graphic.drawWidth
					graphic.drawWidth = block_width
				graphic.spaceBefore = 6
				story.append(KeepTogether([graphic, caption]))
			else:
				cells = [[paragraph({"text": str(value)}, "caption") for value in row] for row in block["rows"]]
				table = Table(cells, colWidths=block.get("column_widths"), repeatRows=block.get("header_rows", 1), hAlign="LEFT")
				table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.grey)]))
				table.spaceBefore = 6
				table.spaceAfter = 6
				story.extend([caption, table])
		else:
			raise ValueError(f"Unknown block kind: {kind}")
	document.build(story)
	reader = PdfReader(BytesIO(buffer.getvalue()))
	writer = PdfWriter()
	writer.clone_document_from_reader(reader)
	for page_number, x, y, target_width, path in placements:
		graphic = PdfReader(path).pages[0]
		box = graphic.mediabox
		scale = target_width / float(box.width)
		transform = Transformation().translate(-float(box.left), -float(box.bottom)).scale(scale).translate(x, y)
		writer.pages[page_number - 1].merge_transformed_page(graphic, transform, over=True)
	output = BytesIO()
	writer.write(output)
	text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(output.getvalue())).pages)
	if "\ufffd" in text or any(value not in text for value in data.get("expected_text", [])):
		raise ValueError("Extracted text does not satisfy the transcription checks")
	return output.getvalue()


# --------------------------------------------------
def main():
	"""Écrit un nouveau PDF depuis une transcription déjà relue."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("transcription", type=Path)
	parser.add_argument("--output", required=True, type=Path)
	parser.add_argument("--scientific-font", type=Path)
	args = parser.parse_args()
	data = json.loads(args.transcription.read_text(encoding="utf-8"))
	source = (args.transcription.parent / data["source"]).resolve()
	if args.output.resolve() in {source, args.transcription.resolve()} or args.output.exists():
		parser.error("Output must be a new file distinct from source and transcription")
	with source.open("rb") as stream: source_hash = hashlib.file_digest(stream, "sha256").hexdigest()
	candidate = compose(data, args.transcription.resolve().parent, args.scientific_font)
	with source.open("rb") as stream:
		if hashlib.file_digest(stream, "sha256").hexdigest() != source_hash:
			raise ValueError("Source changed during composition")
	args.output.parent.mkdir(parents=True, exist_ok=True)
	with args.output.open("xb") as stream: stream.write(candidate)


if __name__ == "__main__": main()
