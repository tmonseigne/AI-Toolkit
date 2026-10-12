"""Rend les pages appariées et génère un rapport HTML de relecture."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from html import escape
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageChops, ImageStat
from pypdf import PdfReader

from pdf_inventory import sha256


# --------------------------------------------------
def local_path(value: str | Path, base: Path) -> Path:
	"""
	Résout un chemin par rapport au manifeste.

	:param value: Chemin absolu ou relatif.
	:param base: Répertoire du manifeste.
	:return: Chemin absolu existant.
	"""
	path = Path(value)
	path = (path if path.is_absolute() else base / path).resolve()
	if not path.is_file():
		raise FileNotFoundError(path)
	return path


# --------------------------------------------------
def render(source: Path, output: Path, page: int, dpi: int, poppler: str | Path):
	"""
	Rend une page avec le même moteur et la même définition.

	:param source: PDF source.
	:param output: PNG de destination.
	:param page: Numéro de page, à partir de un.
	:param dpi: Définition du rendu.
	:param poppler: Exécutable pdftoppm.
	"""
	subprocess.run(
		[poppler, "-f", str(page), "-l", str(page), "-r", str(dpi), "-singlefile", "-png", str(source), str(output.with_suffix(""))],
		check=True,
		capture_output=True,
	)
	if not output.is_file():
		raise RuntimeError("Renderer did not produce a PNG")


# --------------------------------------------------
def pair_html(before: Path, after: Path, identifier: str, folder: Path) -> str:
	"""
	Construit une paire avec liens relatifs et zoom synchronisé.

	:param before: Image originale.
	:param after: Image proposée.
	:param identifier: Identifiant interne sûr.
	:param folder: Répertoire du rapport.
	:return: Fragment HTML échappé.
	"""
	parts = [f'<div class="pair" id="{identifier}">']
	for path, label in ((before, "Before"), (after, "After")):
		url = escape(quote(os.path.relpath(path, folder).replace("\\", "/"), safe="/"), quote=True)
		parts.append(
			f'<div><strong>{label}</strong><div class="viewport"><img loading="lazy" src="{url}" alt="{label}"></div>'
			f'<a href="{url}" target="_blank" rel="noopener">Full resolution</a></div>'
		)
	parts.append(
		f'</div><div class="tools"><label>Zoom <select class="zoom" data-pair="{identifier}">'
		'<option value="fit">Fit</option><option value="1">100 %</option>'
		'<option value="2">200 %</option><option value="3">300 %</option></select></label></div>'
	)
	return "\n".join(parts)


# --------------------------------------------------
def build_report(manifest: Path, folder: Path, poppler: str | Path, dpi: int) -> Path:
	"""
	Compare tous les appariements déclarés sans supposer la même pagination.

	:param manifest: Chemin du manifeste documenté dans les références.
	:param folder: Nouveau répertoire de livraison.
	:param poppler: Exécutable pdftoppm.
	:param dpi: Définition commune aux rendus.
	:return: Chemin du rapport.
	"""
	plan = json.loads(manifest.read_text(encoding="utf-8"))
	content, rows, checks = [], [], []
	for document_index, document in enumerate(plan["documents"]):
		before = local_path(document["before"], manifest.parent)
		after = local_path(document["after"], manifest.parent)
		fingerprints = [sha256(before), sha256(after)]
		before_count, after_count = len(PdfReader(before).pages), len(PdfReader(after).pages)
		pairs = document.get("pages")
		if pairs is None:
			if before_count != after_count:
				raise ValueError("Different pagination requires explicit page mappings")
			pairs = [[number, number] for number in range(1, before_count + 1)]
		if not pairs:
			raise ValueError("At least one page mapping is required")
		identifier = f"document-{document_index}"
		title = document.get("title", before.stem)
		content.append(f'<article id="{identifier}" data-search="{escape(title, quote=True)}"><h2>{escape(title)}</h2>')
		content.extend(f'<p>{escape(note)}</p>' for note in document.get("notes", []))
		for side, path, label in (("before", before, "Before PDF"), ("after", after, "After PDF")):
			destination = folder / f"{identifier}-{side}.pdf"
			shutil.copy2(path, destination)
			content.append(f'<a href="{destination.name}">{label}</a> ')
		comparisons = []
		for index, (before_page, after_page) in enumerate(pairs):
			if not (1 <= before_page <= before_count and 1 <= after_page <= after_count):
				raise ValueError("Page mapping is outside the document")
			paths = [folder / f"{identifier}-page-{index}-{side}.png" for side in ("before", "after")]
			for source, path, page in zip((before, after), paths, (before_page, after_page)): render(source, path, page, dpi, poppler)
			with Image.open(paths[0]) as first, Image.open(paths[1]) as second:
				same_size = first.size == second.size
				metric = {"same_dimensions": same_size, "render_pixels_identical": False}
				if same_size:
					difference = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
					metric.update(render_pixels_identical=difference.getbbox() is None, mean_absolute_error=sum(ImageStat.Stat(difference).mean) / 3)
			checks.append({"document": identifier, "before_page": before_page, "after_page": after_page, **metric})
			comparisons.append(("page", f"Page {before_page} → {after_page}", paths, metric))
		for image in document.get("images", []):
			kind = image.get("kind", "figure")
			if kind not in {"figure", "table", "image"}:
				raise ValueError("Unsupported comparison kind")
			paths = []
			for side in ("before", "after"):
				source = local_path(image[side], manifest.parent)
				with Image.open(source) as raster:
					destination = folder / f"{identifier}-asset-{len(comparisons)}-{side}.png"
					raster.save(destination, format="PNG")
				paths.append(destination)
			comparisons.append((kind, image["label"], paths, {}))
		for index, (kind, label, paths, metric) in enumerate(comparisons):
			pair_id = f"{identifier}-pair-{index}"
			# L'empreinte invalide les anciennes coches si le contenu évolue.
			review_id = hashlib.sha256(("|".join(fingerprints) + pair_id + label + sha256(paths[0]) + sha256(paths[1])).encode()).hexdigest()
			content.append(
				f'<section class="change" data-kind="{kind}" data-id="{review_id}"><h3>{escape(label)}</h3>'
				f'<label><input class="review" type="checkbox" data-id="{review_id}"> Reviewed</label>'
			)
			if metric: content.append(f'<p class="small">Contrôle de rendu : {escape(json.dumps(metric))}</p>')
			content.append(pair_html(*paths, pair_id, folder) + "</section>")
		content.append("</article>")
		sizes = [before.stat().st_size / 1e6, after.stat().st_size / 1e6]
		rows.append(
			f'<tr><td><a href="#{identifier}">{escape(title)}</a></td><td>{sizes[0]:.3f}</td><td>{sizes[1]:.3f}</td><td>{sizes[0] - sizes[1]:.3f}</td></tr>'
		)
		if fingerprints != [sha256(before), sha256(after)]:
			raise ValueError("PDF source changed during comparison")
	template = (Path(__file__).resolve().parent.parent / "assets" / "comparison_report.html").read_text(encoding="utf-8")
	values = {
		"TITLE": escape(plan.get("title", "Comparaison des PDF")),
		"SUMMARY": escape(plan.get("summary", "Versions proposées pour relecture.")),
		"REPORT_ID": hashlib.sha256(manifest.read_bytes()).hexdigest(),
		"ROWS": "\n".join(rows),
		"CONTENT": "\n".join(content),
	}
	report = folder / "report.html"
	report.write_text(re.sub(r"@@([A-Z_]+)@@", lambda match: values[match[1]], template), encoding="utf-8", newline="\n")
	(folder / "checks.json").write_text(
		json.dumps({"dpi": dpi, "renderer": poppler, "checks": checks, "visual_review": "pending"}, indent=2) + "\n", encoding="utf-8", newline="\n"
	)
	return report


# --------------------------------------------------
def main():
	"""Produit un dossier autonome, sans écraser une livraison existante."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("manifest", type=Path)
	parser.add_argument("--output-dir", required=True, type=Path)
	parser.add_argument("--pdftoppm", default="pdftoppm")
	parser.add_argument("--dpi", type=int, default=130)
	args = parser.parse_args()
	if args.dpi <= 0: parser.error("DPI must be positive")
	poppler = shutil.which(args.pdftoppm)
	if not poppler: parser.error("pdftoppm executable was not found")
	args.output_dir.mkdir(parents=True, exist_ok=False)
	build_report(args.manifest.resolve(), args.output_dir.resolve(), poppler, args.dpi)


if __name__ == "__main__": main()
