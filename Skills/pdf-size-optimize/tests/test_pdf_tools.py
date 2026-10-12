"""Vérifie les invariants des helpers PDF sur des documents synthétiques."""

import json
import shutil
import sys
import tempfile
import unittest
import zlib
from io import BytesIO
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

SKILL_ROOT = Path(__file__).resolve().parents[1]
poppler_path = None
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
sys.path.insert(0, str(SKILL_ROOT.parent / "pdf-scan-restore" / "scripts"))

from compare_pdf import build_report
from compose_article import compose
from optimize_lossless import optimize, signatures
from pdf_inventory import inspect_pdf, object_ids, sha256


class PdfToolsTest(unittest.TestCase):
	"""Teste les transformations observables sans pièce jointe réelle."""

	# ==================================================
	# region Préparation
	# ==================================================
	def setUp(self):
		"""Prépare un original avec image, texte et annotation."""
		artifact_root = SKILL_ROOT.parents[1] / "_output"
		artifact_root.mkdir(exist_ok=True)
		self.temporary = tempfile.TemporaryDirectory(dir=artifact_root)
		self.folder = Path(self.temporary.name)
		self.source = self.folder / "source.pdf"
		buffer = BytesIO()
		document = canvas.Canvas(buffer, pagesize=(300, 400))
		document.drawString(20, 380, "Original 0.72")
		with Image.new("RGB", (200, 200), "#f0e0d0") as image: document.drawImage(ImageReader(image), 20, 100, width=200, height=200)
		document.linkURL("https://example.org", (20, 370, 120, 390))
		document.save()
		reader = PdfReader(BytesIO(buffer.getvalue()))
		for generation, number in object_ids(reader):
			obj = reader.get_object(number) if generation == 0 else None
			if isinstance(obj, dict) and obj.get("/Subtype") == "/Image":
				raw = obj.get_data()
				obj._data = zlib.compress(raw, 0)
				obj[NameObject("/Filter")] = NameObject("/FlateDecode")
				obj.pop("/DecodeParms", None)
				obj.decoded_self = None
		writer = PdfWriter()
		writer.clone_document_from_reader(reader)
		writer.write(self.source)
		self.source_hash = sha256(self.source)

	# --------------------------------------------------
	def tearDown(self):
		"""Supprime uniquement le dossier temporaire propre à ce test."""
		self.temporary.cleanup()

	# ==================================================
	# endregion Préparation
	# ==================================================

	# ==================================================
	# region Inventaire et optimisation
	# ==================================================
	def test_inventory_and_lossless_roundtrip(self):
		"""Vérifie gain réel, pixels, contenu, annotation et original inchangé."""
		inventory = inspect_pdf(self.source)
		self.assertNotIn("error", inventory)
		self.assertGreater(inventory["image_bytes"], 100_000)
		candidate = self.folder / "candidate.pdf"
		result = optimize(self.source, candidate, 90_000_000)
		self.assertEqual(result["status"], "candidate")
		self.assertGreater(result["gain_bytes"], 100_000)
		self.assertEqual(signatures(PdfReader(self.source)), signatures(PdfReader(candidate)))
		self.assertEqual(sha256(self.source), self.source_hash)
		with self.assertRaises(FileExistsError): optimize(self.source, candidate, 90_000_000)

	# --------------------------------------------------
	def test_encrypted_pdf_is_rejected(self):
		"""Refuse une transformation dont le chiffrement ne serait pas préservé."""
		encrypted = self.folder / "encrypted.pdf"
		writer = PdfWriter(clone_from=self.source)
		writer.encrypt("test-password")
		writer.write(encrypted)
		candidate = self.folder / "candidate.pdf"
		with self.assertRaisesRegex(ValueError, "Encrypted"): optimize(encrypted, candidate, 90_000_000)
		self.assertFalse(candidate.exists())

	# ==================================================
	# endregion Inventaire et optimisation
	# ==================================================

	# ==================================================
	# region Composition
	# ==================================================
	def test_vector_composition_preserves_text(self):
		"""Vérifie que la figure reste du contenu PDF extractible."""
		figure = self.folder / "figure.pdf"
		graphic = canvas.Canvas(str(figure), pagesize=(100, 60))
		graphic.drawString(3, 20, "Vector label")
		graphic.line(5, 5, 90, 50)
		graphic.save()
		data = {
			"title": "Test",
			"expected_text": ["Vector label", "0.72"],
			"blocks": [{"kind": "paragraph", "text": "Value 0.72"}, {"kind": "figure", "path": "figure.pdf", "caption": "Figure 1"}],
		}
		result = PdfReader(BytesIO(compose(data, self.folder)))
		self.assertIn("Vector label", result.pages[0].extract_text())
		self.assertEqual(len(result.pages[0].images), 0)
		self.assertEqual(sha256(self.source), self.source_hash)

	# --------------------------------------------------
	def test_missing_scientific_font_is_rejected(self):
		"""Refuse un caractère Unicode nécessitant une police explicite."""
		with self.assertRaisesRegex(ValueError, "scientific-font"): compose({"title": "Test", "blocks": [{"kind": "paragraph", "text": "α"}]}, self.folder)

	# ==================================================
	# endregion Composition
	# ==================================================

	# ==================================================
	# region Comparaison
	# ==================================================
	def test_repagination_requires_mapping(self):
		"""Refuse un alignement implicite et accepte une correspondance explicite."""
		poppler = shutil.which("pdftoppm") or poppler_path
		if not poppler: self.skipTest("pdftoppm was not found")
		candidate = self.folder / "two-pages.pdf"
		writer = PdfWriter(clone_from=self.source)
		writer.add_page(PdfReader(self.source).pages[0])
		writer.write(candidate)
		document = {"before": "source.pdf", "after": "two-pages.pdf"}
		manifest = self.folder / "mapping.json"
		manifest.write_text(json.dumps({"documents": [document]}), encoding="utf-8")
		folder = self.folder / "mapping"
		folder.mkdir()
		with self.assertRaisesRegex(ValueError, "pagination"): build_report(manifest, folder, poppler, 90)
		document["pages"] = [[1, 2]]
		manifest.write_text(json.dumps({"documents": [document]}), encoding="utf-8")
		build_report(manifest, folder, poppler, 90)
		checks = json.loads((folder / "checks.json").read_text(encoding="utf-8"))
		self.assertEqual(checks["checks"][0]["after_page"], 2)

	# --------------------------------------------------
	def test_report_is_portable_and_pixels_identical(self):
		"""Vérifie un rendu identique et un dossier HTML autonome."""
		poppler = shutil.which("pdftoppm") or poppler_path
		if not poppler: self.skipTest("pdftoppm was not found")
		candidate = self.folder / "candidate.pdf"
		optimize(self.source, candidate, 90_000_000)
		manifest = self.folder / "comparison.json"
		manifest.write_text(json.dumps({"documents": [{"title": "A < B", "before": "source.pdf", "after": "candidate.pdf"}]}), encoding="utf-8")
		report_folder = self.folder / "review"
		report_folder.mkdir()
		report = build_report(manifest, report_folder, poppler, 90)
		checks = json.loads((report_folder / "checks.json").read_text(encoding="utf-8"))
		self.assertTrue(checks["checks"][0]["render_pixels_identical"])
		html = report.read_text(encoding="utf-8")
		self.assertIn("A &lt; B", html)
		self.assertNotIn("@@TITLE@@", html)
		self.assertEqual(len(list(report_folder.glob("*.pdf"))), 2)
		self.assertEqual(len(list(report_folder.glob("*.png"))), 2)
		self.assertEqual(sha256(self.source), self.source_hash)

	# ==================================================
	# endregion Comparaison
	# ==================================================



if __name__ == "__main__":
	# Un chemin explicite permet de tester le runtime fourni sans modifier PATH.
	poppler_path = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
	unittest.main()
