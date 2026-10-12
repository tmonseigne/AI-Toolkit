"""Vérifier les outils bibliographiques sur des données synthétiques."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

SCRIPTS_PATH = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))
import apply_verified_metadata
import audit_metadata
import pubmed_metadata

REVIEW_SCRIPTS_PATH = Path(__file__).resolve().parents[2] / "biblio-article-review/scripts"
spec = importlib.util.spec_from_file_location("split_reviews", REVIEW_SCRIPTS_PATH / "split_reviews.py")
split_reviews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(split_reviews)


class BibliographyToolsTest(unittest.TestCase):
	"""Contrôler la lecture seule, les conflits et la conservation des créateurs."""

	# ==================================================
	# region Préparation
	# ==================================================
	def setUp(self):
		"""Créer une base minimale avec deux notices partageant un créateur."""
		self.directory = tempfile.TemporaryDirectory(prefix="bibliography-tests-")
		self.addCleanup(self.directory.cleanup)
		self.root = Path(self.directory.name)
		self.database = self.root / "data" / "zotero.sqlite"
		self.database.parent.mkdir()
		self.output = self.root / "audit"
		with contextlib.closing(sqlite3.connect(self.database)) as connection:
			connection.executescript("""
                CREATE TABLE libraries(libraryID INTEGER PRIMARY KEY, editable INTEGER);
                CREATE TABLE itemTypes(itemTypeID INTEGER PRIMARY KEY, typeName TEXT);
                CREATE TABLE items(itemID INTEGER PRIMARY KEY, key TEXT, libraryID INTEGER,
                    itemTypeID INTEGER, dateModified TEXT, clientDateModified TEXT, synced INTEGER);
                CREATE TABLE deletedItems(itemID INTEGER);
                CREATE TABLE fields(fieldID INTEGER PRIMARY KEY, fieldName TEXT);
                CREATE TABLE itemDataValues(valueID INTEGER PRIMARY KEY, value TEXT);
                CREATE TABLE itemData(itemID INTEGER REFERENCES items, fieldID INTEGER REFERENCES fields,
                    valueID INTEGER REFERENCES itemDataValues, PRIMARY KEY(itemID, fieldID));
                CREATE TABLE itemTypeFields(itemTypeID INTEGER, fieldID INTEGER);
                CREATE TABLE creators(creatorID INTEGER PRIMARY KEY, firstName TEXT, lastName TEXT, fieldMode INTEGER);
                CREATE TABLE creatorTypes(creatorTypeID INTEGER PRIMARY KEY, creatorType TEXT);
                CREATE TABLE itemCreators(itemID INTEGER REFERENCES items, creatorID INTEGER REFERENCES creators,
                    creatorTypeID INTEGER REFERENCES creatorTypes, orderIndex INTEGER);
                INSERT INTO libraries VALUES(1,1),(2,1);
                INSERT INTO itemTypes VALUES(1,'journalArticle'),(2,'attachment');
                INSERT INTO items VALUES(1,'ITEM0001',1,1,'','',1),(2,'ITEM0002',1,1,'','',1),
                    (3,'PDF00001',1,2,'','',1);
                INSERT INTO fields VALUES(1,'title'),(2,'language'),(3,'publicationTitle');
                INSERT INTO itemTypeFields VALUES(1,1),(1,2),(1,3);
                INSERT INTO itemDataValues VALUES(1,'Example <script>alert(1)</script>'),(2,'en'),
                    (3,'Example Journal');
                INSERT INTO itemData VALUES(1,1,1),(1,2,2),(1,3,3),(2,1,1),(2,2,2);
                INSERT INTO creators VALUES(1,'A.','Scientist',0);
                INSERT INTO creatorTypes VALUES(1,'author');
                INSERT INTO itemCreators VALUES(1,1,1,0),(2,1,1,0);
            """)

	# --------------------------------------------------
	def change(self, field: str = "language", before: str = "en", after: str = "fr") -> dict[str, str]:
		"""Construire une correction précise avec sa provenance."""
		return {
			"key": "ITEM0001",
			"field": field,
			"before": before,
			"after": after,
			"reason": "Valeur contrôlée dans le texte synthétique.",
			"source": "https://example.org/article",
		}

	# --------------------------------------------------
	def manifest(self, changes: list[dict[str, Any]]) -> Path:
		"""Créer un manifeste relu attaché à la base synthétique."""
		path = self.root / "reviewed_changes.json"
		path.write_text(json.dumps({"database": str(self.database), "library_id": 1, "reviewed": True, "changes": changes}), encoding="utf-8")
		return path

	# ==================================================
	# endregion Préparation
	# ==================================================

	# ==================================================
	# region Audit bibliographique
	# ==================================================
	def test_fresh_inventory_and_last_journal_value(self):
		"""Le dernier changement du journal prime sur les valeurs précédentes."""
		self.output.mkdir()
		journal = {
			"phase": "committed",
			"count": 2,
			"changes": [
				self.change("publicationTitle", "Old Journal", "Intermediate Journal"),
				self.change("publicationTitle", "Intermediate Journal", "Example Journal"),
			],
		}
		(self.output / "modifications-appliquees.json").write_text(json.dumps(journal), encoding="utf-8")
		(self.output / "inventaire.json").write_text("[]", encoding="utf-8")
		with contextlib.redirect_stdout(io.StringIO()): audit_metadata.prepare(self.output, self.database, 1, offline=True)
		records = json.loads((self.output / "inventaire.json").read_text(encoding="utf-8"))
		self.assertEqual(len(records), 2)
		issues = json.loads((self.output / "corrections.json").read_text(encoding="utf-8"))["issues"]
		self.assertFalse(any(i["key"] == "ITEM0001" and i["field"] == "publicationTitle" for i in issues))

	# --------------------------------------------------
	def test_offline_audit_preserves_database_and_escapes_html(self):
		"""L'audit laisse la base inchangée et échappe les titres HTML."""
		before = hashlib.sha256(self.database.read_bytes()).hexdigest()
		with patch.object(audit_metadata, "request_json", side_effect=AssertionError("Unexpected network access")):
			with contextlib.redirect_stdout(io.StringIO()): audit_metadata.prepare(self.output, self.database, 1, offline=True)
		self.assertEqual(before, hashlib.sha256(self.database.read_bytes()).hexdigest())
		records = json.loads((self.output / "inventaire.json").read_text(encoding="utf-8"))
		self.assertEqual(len(records), 2)
		report = (self.output / "rapport.html").read_text(encoding="utf-8")
		self.assertIn("&lt;script&gt;", report)
		self.assertNotIn("{{rows}}", report)
		self.assertNotIn("alert(1)</script>", report)

	# ==================================================
	# endregion Audit bibliographique
	# ==================================================

	# ==================================================
	# region Application des métadonnées
	# ==================================================
	def test_transaction_rolls_back_all_changes_on_conflict(self):
		"""Une valeur avant incorrecte annule l'ensemble du lot."""
		with self.assertRaisesRegex(ValueError, "Value conflict"):
			apply_verified_metadata.apply_transaction(self.database, [self.change(), self.change("publicationTitle", "Wrong", "New")], 1)
		with contextlib.closing(sqlite3.connect(self.database)) as connection:
			self.assertEqual(apply_verified_metadata.current_value(connection, 1, "language"), "en")

	# --------------------------------------------------
	def test_author_update_preserves_shared_creator(self):
		"""Le développement d'un prénom ne modifie pas l'autre notice."""
		apply_verified_metadata.apply_transaction(self.database, [self.change("author[1].firstName", "A.", "Alice")], 1)
		with contextlib.closing(sqlite3.connect(self.database)) as connection:
			self.assertEqual(apply_verified_metadata.current_value(connection, 1, "author[1].firstName"), "Alice")
			self.assertEqual(apply_verified_metadata.current_value(connection, 2, "author[1].firstName"), "A.")
			self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

	# --------------------------------------------------
	def test_default_application_validates_copy_only(self):
		"""L'exécution par défaut ne change pas la base ni le suivi."""
		before = hashlib.sha256(self.database.read_bytes()).hexdigest()
		with contextlib.redirect_stdout(io.StringIO()): apply_verified_metadata.main(self.database, self.output, self.manifest([self.change()]))
		self.assertEqual(before, hashlib.sha256(self.database.read_bytes()).hexdigest())
		self.assertFalse(self.output.exists())

	# --------------------------------------------------
	def test_commit_creates_backup_and_journal(self):
		"""L'application explicite sur la base synthétique conserve un retour arrière."""
		before = hashlib.sha256(self.database.read_bytes()).hexdigest()
		with patch.object(apply_verified_metadata, "assert_zotero_closed"):
			with contextlib.redirect_stdout(io.StringIO()):
				apply_verified_metadata.main(self.database, self.output, self.manifest([self.change()]), commit=True)
		journal = json.loads((self.output / "modifications-appliquees.json").read_text(encoding="utf-8"))
		self.assertEqual(journal["phase"], "committed")
		backup = Path(journal["batches"][0]["backup"])
		with contextlib.closing(sqlite3.connect(backup)) as connection: self.assertEqual(apply_verified_metadata.current_value(connection, 1, "language"), "en")
		with contextlib.closing(sqlite3.connect(self.database)) as connection:
			self.assertEqual(apply_verified_metadata.current_value(connection, 1, "language"), "fr")
		self.assertNotEqual(before, hashlib.sha256(self.database.read_bytes()).hexdigest())

	# --------------------------------------------------
	def test_manifest_refuses_wrong_database_and_duplicate_fields(self):
		"""Les corrections ambiguës sont refusées avant l'écriture."""
		path = self.manifest([self.change(), self.change()])
		with self.assertRaisesRegex(ValueError, "Duplicate"): apply_verified_metadata.read_manifest(path, self.database)
		with self.assertRaisesRegex(ValueError, "database"): apply_verified_metadata.read_manifest(path, self.root / "other.sqlite")

	# --------------------------------------------------
	def test_library_scope_and_output_boundary(self):
		"""La bibliothèque choisie et le dossier de sortie bornent le travail."""
		with self.assertRaisesRegex(ValueError, "Unavailable item"): apply_verified_metadata.apply_transaction(self.database, [self.change()], 2)
		with self.assertRaisesRegex(ValueError, "outside"): audit_metadata.prepare(self.database.parent / "audit", self.database, offline=True)

	# ==================================================
	# endregion Application des métadonnées
	# ==================================================

	# ==================================================
	# region Fiches et extraction
	# ==================================================
	def test_split_reviews_preserves_source_and_refuses_overwrite(self):
		"""Le découpage conserve le texte et protège les fiches existantes."""
		source = self.root / "collection.md"
		content = "### Fiche 1 : First study\n\n#### Résultats\nContenu scientifique.\n\n### Fiche 2 : Second study\n\nAutre contenu.\n"
		source.write_text(content, encoding="utf-8")
		output = self.root / "reviews"
		with contextlib.redirect_stdout(io.StringIO()): split_reviews.main(source, output)
		self.assertEqual(source.read_text(encoding="utf-8"), content)
		self.assertIn("Contenu scientifique.", (output / "01-first-study-fiche.md").read_text(encoding="utf-8"))
		with self.assertRaises(FileExistsError): split_reviews.main(source, output)

	# --------------------------------------------------
	def test_pdf_extraction_preserves_pages_and_existing_output(self):
		"""Les repères de pages sont conservés sans écraser une extraction."""
		try:
			from pypdf import PdfWriter
		except ImportError:
			self.skipTest("pypdf is unavailable")
		spec = importlib.util.spec_from_file_location("extract_pdf_text", REVIEW_SCRIPTS_PATH / "extract_pdf_text.py")
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		source = self.root / "article.pdf"
		writer = PdfWriter()
		writer.add_blank_page(width=100, height=100)
		writer.add_blank_page(width=100, height=100)
		writer.write(source)
		before = source.read_bytes()
		output = self.root / "article-text.txt"
		with contextlib.redirect_stdout(io.StringIO()): module.extract(source, output)
		extracted = output.read_text(encoding="utf-8")
		self.assertIn("=== PAGE 1 ===", extracted)
		self.assertIn("=== PAGE 2 ===", extracted)
		self.assertEqual(source.read_bytes(), before)
		with self.assertRaises(FileExistsError): module.extract(source, output)

	# ==================================================
	# endregion Fiches et extraction
	# ==================================================

	# ==================================================
	# region Recherche PubMed
	# ==================================================
	def test_pubmed_parser_keeps_structured_abstract_and_doi(self):
		"""Le parseur préserve les sections du résumé et l'identifiant DOI."""
		xml = b"""<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>1</PMID>
            <Article><ArticleTitle>Example</ArticleTitle><Journal><Title>Journal</Title></Journal>
            <Abstract><AbstractText Label="RESULTS">Measured result.</AbstractText></Abstract>
            <AuthorList><Author><LastName>Scientist</LastName><ForeName>Alice</ForeName></Author></AuthorList>
            </Article></MedlineCitation><PubmedData><ArticleIdList>
            <ArticleId IdType="doi">10.1234/example</ArticleId></ArticleIdList></PubmedData>
            </PubmedArticle></PubmedArticleSet>"""
		record = pubmed_metadata.parse(xml)[0]
		self.assertEqual(record["fields"]["DOI"], "10.1234/example")
		self.assertEqual(record["fields"]["abstractNote"], "RESULTS: Measured result.")

	# ==================================================
	# endregion Recherche PubMed
	# ==================================================



if __name__ == "__main__": unittest.main()
