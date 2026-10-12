#!/usr/bin/env python3
"""Audite en lecture seule la documentation Python et les traductions du projet."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

_MAX_LENGTH = 160
_EXCLUDED = {".git", ".idea", "__pycache__", "build", "dist", "htmlcov"}
_TRIVIAL_UNDOCUMENTED_CLASSES = {"_FakeDownload"}
_USER_CALLS = {"critical", "debug", "error", "information", "info", "print", "question", "setStatusTip", "setText", "setToolTip", "setWindowTitle", "warning"}
_FRENCH = re.compile(r"[àâçéèêëîïôùûüÿœæ]|\b(?:avec|cette|dans|des|erreur|fichier|impossible|introuvable|pour|une)\b", re.IGNORECASE)
_PARAM = re.compile(r"^\s*:param(?:\s+\S+)?\s+([*]*\w+)\s*:\s*(.*)$")
_TYPE = re.compile(r"^\s*:type\s+([*]*\w+)\s*:\s*(.*)$")
_RETURN = re.compile(r"^\s*:returns?\s*:\s*(.*)$")
_RTYPE = re.compile(r"^\s*:rtype\s*:\s*(.*)$")


@dataclass(frozen=True)
class Finding:
	"""Décrit un diagnostic documentaire sérialisable."""

	severity: str
	"""Niveau de gravité du diagnostic."""
	code: str
	"""Identifiant stable du contrôle documentaire."""
	path: str
	"""Chemin du fichier relatif à la racine du dépôt."""
	line: int
	"""Numéro de ligne du diagnostic, à partir de un."""
	message: str
	"""Description du problème constaté."""


class Auditor:
	"""Collecte les diagnostics documentaires sans exécuter le code du projet."""

	# --------------------------------------------------
	def __init__(self, root: Path):
		"""Initialise l'audit pour la racine du dépôt indiquée."""
		self.root = root
		self.findings: list[Finding] = []

	# --------------------------------------------------
	def add(self, severity: str, code: str, path: Path, line: int, message: str):
		"""Enregistre un diagnostic avec un chemin relatif à la racine du dépôt."""
		self.findings.append(Finding(severity, code, path.relative_to(self.root).as_posix(), line, message))

	# --------------------------------------------------
	def file(self, path: Path):
		"""Contrôle l'encodage et transmet le fichier à l'analyseur adapté."""
		raw = path.read_bytes()
		if raw.startswith(b"\xef\xbb\xbf"): self.add("warning", "TEXT_BOM", path, 1, "BOM UTF-8 présent.")
		if b"\r\n" in raw: self.add("error", "TEXT_CRLF", path, 1, "Fins de lignes CRLF présentes.")
		if raw and not raw.endswith(b"\n"): self.add("error", "TEXT_EOF", path, 1, "Saut de ligne final absent.")
		try:
			text = raw.decode("utf-8-sig")
		except UnicodeDecodeError as error:
			self.add("error", "TEXT_UTF8", path, error.start + 1, "Encodage différent d'UTF-8.")
			return
		if path.suffix == ".py":
			self.python(path, text)
		elif path.suffix == ".po": self.po(path, text)

	# --------------------------------------------------
	def python(self, path: Path, text: str):
		"""Analyse les conventions documentaires d'un module sans l'importer."""
		lines = text.splitlines()
		try:
			tree = ast.parse(text, filename=str(path))
		except SyntaxError as error:
			self.add("error", "PY_SYNTAX", path, error.lineno or 1, error.msg)
			return

		doc_lines: set[int] = set()
		parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
		self.doc_owner(path, tree, "module", path.stem, lines, doc_lines)
		for node in ast.walk(tree):
			if isinstance(node, ast.ClassDef):
				self.doc_owner(path, node, "classe", node.name, lines, doc_lines)
				self.members(path, node)
			elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
				parent = parents.get(node)
				if not (isinstance(parent, ast.ClassDef) and parent.name in _TRIVIAL_UNDOCUMENTED_CLASSES):
					self.doc_owner(path, node, "fonction", node.name, lines, doc_lines)
					self.fields(path, node)
			elif isinstance(node, ast.Call) and self.call_name(node.func) in _USER_CALLS: self.user_strings(path, node)

		double_grave = chr(96) * 2
		for number, line in enumerate(lines, 1):
			if len(line.expandtabs(4)) > _MAX_LENGTH and (number in doc_lines or line.lstrip().startswith("#")):
				self.add("warning", "PY_DOC_WIDTH", path, number, "Ligne documentaire supérieure à 160 caractères.")
			comment = self.comment_index(line)
			if comment >= 0 and double_grave in line[comment:]:
				self.add("warning", "PY_COMMENT_LITERAL", path, number, "Double accent grave présent dans un commentaire.")
			indent = line[: len(line) - len(line.lstrip(" \t"))]
			if indent.startswith(" ") and line.strip(): self.add("warning", "PY_INDENT_SPACE", path, number, "Indentation commençant par des espaces.")

	# --------------------------------------------------
	def doc_owner(self, path: Path, node: ast.AST, kind: str, name: str, lines: Sequence[str], doc_lines: set[int]):
		"""Vérifie la présence et la présentation d'une docstring, puis repère ses lignes."""
		body = getattr(node, "body", [])
		doc_node = (
			body[0] if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str) else None
		)
		if doc_node is None:
			if kind != "fonction" or name != "get_ui":
				self.add("warning", "PY_DOC_MISSING", path, getattr(node, "lineno", 1), f"Docstring absente pour {kind} {name}.")
			return
		doc = doc_node.value.value
		doc_lines.update(range(doc_node.lineno, getattr(doc_node, "end_lineno", doc_node.lineno) + 1))
		if "\n" in doc:
			opening = lines[doc_node.lineno - 1]
			match = re.search(r"(?:[rRuUbBfF]*)('''|\"\"\")", opening)
			if match and opening[match.end() :].strip():
				self.add("warning", "PY_DOC_MULTILINE_OPEN", path, doc_node.lineno, "Le texte multiligne commence sur la ligne des triples guillemets.")

	# --------------------------------------------------
	def fields(self, path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef):
		"""Contrôle la cohérence et le contenu des balises reStructuredText d'une fonction."""
		doc = ast.get_docstring(node, clean=False)
		if not doc: return
		params: set[str] = set()
		types: set[str] = set()
		has_return = False
		has_rtype = False
		for offset, line in enumerate(doc.splitlines()):
			number = node.lineno + offset
			if match := _PARAM.match(line):
				params.add(match.group(1).lstrip("*"))
				if not match.group(2).strip(): self.add("error", "PY_PARAM_EMPTY", path, number, f"Description vide pour {match.group(1)}.")
			elif match := _TYPE.match(line):
				types.add(match.group(1).lstrip("*"))
				if not match.group(2).strip(): self.add("error", "PY_TYPE_EMPTY", path, number, f"Type vide pour {match.group(1)}.")
			elif match := _RETURN.match(line):
				has_return = True
				if not match.group(1).strip(): self.add("error", "PY_RETURN_EMPTY", path, number, "Description de retour vide.")
			elif match := _RTYPE.match(line):
				has_rtype = True
				if not match.group(1).strip(): self.add("error", "PY_RTYPE_EMPTY", path, number, "Type de retour vide.")
		for name in sorted(types - params): self.add("warning", "PY_TYPE_WITHOUT_PARAM", path, node.lineno, f":type {name}: sans :param {name}: correspondant.")
		if has_rtype and not has_return: self.add("warning", "PY_RTYPE_WITHOUT_RETURN", path, node.lineno, ":rtype: sans :return: correspondant.")

	# --------------------------------------------------
	def members(self, path: Path, node: ast.ClassDef):
		"""Repère les membres de classe dépourvus de documentation adjacente."""
		for index, statement in enumerate(node.body):
			names: list[str] = []
			if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
				names = [statement.target.id]
			elif isinstance(statement, ast.Assign): names = [target.id for target in statement.targets if isinstance(target, ast.Name)]
			if not names or all(name.startswith("_") for name in names): continue
			following = node.body[index + 1] if index + 1 < len(node.body) else None
			documented = isinstance(following, ast.Expr) and isinstance(following.value, ast.Constant) and isinstance(following.value.value, str)
			if not documented:
				self.add("warning", "PY_MEMBER_DOC_MISSING", path, statement.lineno, "Membre potentiellement non documenté : " + ", ".join(names) + ".")

	# --------------------------------------------------
	def user_strings(self, path: Path, node: ast.Call):
		"""Repère les chaînes françaises susceptibles d'être affichées par un appel."""
		name = self.call_name(node.func)
		for argument in (*node.args, *(keyword.value for keyword in node.keywords)):
			if isinstance(argument, ast.Constant) and isinstance(argument.value, str) and _FRENCH.search(argument.value):
				self.add("warning", "PY_USER_FRENCH", path, argument.lineno, f"Chaîne française potentiellement visible via {name}.")

	# --------------------------------------------------
	def po(self, path: Path, text: str):
		"""Contrôle les métadonnées et les références des traductions Gettext actives."""
		grave = chr(96)
		class_role = re.compile(r":class:" + grave + r"([^" + grave + r"]+)" + grave)
		header_found = False

		# --------------------------------------------------
		def class_targets(value: str) -> list[str]:
			"""Extrait les cibles indépendamment du libellé et de l’abréviation Sphinx."""
			return sorted(re.sub(r"^.*<([^<>]+)>$", r"\1", target).strip().lstrip("~") for target in class_role.findall(value))

		for match in re.finditer(r"(?ms)(?:\A|\n\n)(.*?)(?=\n\n|\Z)", text):
			block = match.group(1)
			if not block.strip() or block.lstrip().startswith("#~"): continue
			lines = block.splitlines()
			number = text.count("\n", 0, match.start()) + 1
			if any(re.match(r"^#,.*\bfuzzy\b", line) for line in lines): self.add("warning", "PO_FUZZY", path, number, "Translation requires review (fuzzy).")
			msgid = self.po_field(lines, "msgid")
			msgstr = self.po_field(lines, "msgstr")
			if msgid == "":
				header_found = True
				if not msgstr: self.add("warning", "PO_HEADER_EMPTY", path, number, "Gettext header metadata is empty.")
				continue
			if not msgid or not msgstr: continue
			if msgid == msgstr: self.add("warning", "PO_IDENTICAL", path, number, "Translation matches source; an empty msgstr may be intentional.")
			if class_targets(msgid) != class_targets(msgstr):
				self.add("warning", "PO_CLASS_MISMATCH", path, number, "Sphinx class targets differ between source and translation.")
		if not header_found: self.add("warning", "PO_HEADER_MISSING", path, 1, "Gettext header entry is missing.")

	# --------------------------------------------------
	@staticmethod
	def po_field(lines: Sequence[str], keyword: str) -> str | None:
		"""Reconstitue un champ Gettext et ses éventuelles lignes de continuation."""
		for index, line in enumerate(lines):
			if not line.startswith(keyword + " "): continue
			try:
				value = json.loads(line[len(keyword) :].strip())
				for continuation in lines[index + 1 :]:
					if not continuation.startswith('"'): break
					value += json.loads(continuation)
				return value
			except (json.JSONDecodeError, TypeError):
				return None
		return None

	# --------------------------------------------------
	@staticmethod
	def call_name(node: ast.expr) -> str:
		"""Extrait le nom terminal d'une fonction ou d'une méthode dans l'arbre syntaxique."""
		return node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else ""

	# --------------------------------------------------
	@staticmethod
	def comment_index(line: str) -> int:
		"""Recherche un commentaire en tenant compte des chaînes et des caractères échappés."""
		single = double = escaped = False
		for index, character in enumerate(line):
			if escaped:
				escaped = False
			elif character == "\\":
				escaped = True
			elif character == "'" and not double:
				single = not single
			elif character == '"' and not single:
				double = not double
			elif character == "#" and not single and not double: return index
		return -1


# --------------------------------------------------
def git(root: Path, *arguments: str, required: bool = True) -> list[str]:
	"""Exécute une commande Git d'inspection et retourne ses lignes de sortie non vides."""
	result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, text=True, encoding="utf-8", errors="replace")
	if result.returncode:
		if required:
			raise RuntimeError(result.stderr.strip() or "Échec Git.")
		return []
	return [line.strip() for line in result.stdout.splitlines() if line.strip()]


# --------------------------------------------------
def repository_root(candidate: Path) -> Path:
	"""Résout la racine du dépôt Git contenant le chemin indiqué."""
	return Path(git(candidate.resolve(), "rev-parse", "--show-toplevel")[0]).resolve()


# --------------------------------------------------
def base_reference(root: Path, requested: str | None) -> str:
	"""Recherche une référence de comparaison disponible parmi les candidates prévues."""
	for candidate in [requested] if requested else ["origin/main", "origin/master", "main", "master"]:
		if candidate and git(root, "rev-parse", "--verify", "--quiet", candidate, required=False): return candidate
	raise RuntimeError("Branche de base introuvable ; fournir --base.")


# --------------------------------------------------
def files_to_audit(root: Path, scope: str, base: str | None) -> list[Path]:
	"""Sélectionne les sources Python et catalogues Gettext dans le périmètre demandé."""
	if scope == "all":
		names = set(git(root, "ls-files"))
	else:
		reference = base_reference(root, base)
		names = set(git(root, "diff", "--name-only", "--diff-filter=ACMR", f"{reference}...HEAD"))
		names.update(git(root, "diff", "--name-only", "--diff-filter=ACMR"))
		names.update(git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR"))
		names.update(git(root, "ls-files", "--others", "--exclude-standard"))
	result = []
	for name in names:
		path = root / name
		if path.is_file() and path.suffix in {".py", ".po"} and not any(part in _EXCLUDED for part in path.relative_to(root).parts): result.append(path)
	return sorted(result)


# --------------------------------------------------
def arguments(argv: Sequence[str]) -> argparse.Namespace:
	"""Analyse les arguments de ligne de commande de l'audit."""
	parser = argparse.ArgumentParser(description="Audit documentaire Python en lecture seule.")
	parser.add_argument("--root", type=Path, default=Path.cwd())
	parser.add_argument("--scope", choices=("branch", "all"), default="branch")
	parser.add_argument("--base")
	parser.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
	return parser.parse_args(argv)


# --------------------------------------------------
def main(argv: Sequence[str] | None = None) -> int:
	"""Exécute l'audit documentaire et retourne un code indiquant son résultat."""
	options = arguments(argv or sys.argv[1:])
	try:
		root = repository_root(options.root)
		files = files_to_audit(root, options.scope, options.base)
	except RuntimeError as error:
		print(f"Erreur : {error}", file=sys.stderr)
		return 2
	auditor = Auditor(root)
	for path in files: auditor.file(path)
	findings = sorted(auditor.findings, key=lambda item: (item.path, item.line, item.code))
	if options.output_format == "json":
		print(
			json.dumps(
				{"root": str(root), "scope": options.scope, "files": len(files), "findings": [asdict(item) for item in findings]}, ensure_ascii=False, indent=2
			)
		)
	else:
		print(f"Périmètre : {options.scope} — {len(files)} fichier(s) Python/PO analysé(s)")
		for item in findings: print(f"{item.path}:{item.line}: {item.severity.upper()} {item.code}: {item.message}")
		errors = sum(item.severity == "error" for item in findings)
		warnings = sum(item.severity == "warning" for item in findings)
		print(f"Résultat : {errors} erreur(s), {warnings} avertissement(s).")
	return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
	raise SystemExit(main())
