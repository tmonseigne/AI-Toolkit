"""Génère un rapport HTML d’inspection à partir des exports existants, sans analyser ni importer le projet."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


def read_json(path: Path):
	"""Lit un export JSON UTF-8 avec ou sans marqueur d’encodage."""
	return json.loads(path.read_text(encoding="utf-8-sig"))


def source_path(root: Path, filename: str) -> Path | None:
	"""Résout un chemin de diagnostic et écarte les fichiers extérieurs au projet."""
	filename = filename.replace("file://$PROJECT_DIR$/", "").replace("$PROJECT_DIR$/", "")
	if filename.startswith("file://"):
		filename = unquote(filename[7:])
		if re.match(r"^/[A-Za-z]:/", filename): filename = filename[1:]
	path = Path(filename)
	path = (path if path.is_absolute() else root / path).resolve()
	try: path.relative_to(root)
	except ValueError: return None
	return path


def project_files(root: Path, scope: Path | None) -> set[str]:
	"""Lit le périmètre explicite ou les fichiers Git suivis et nouveaux non ignorés."""
	if scope is not None:
		return {line.strip().replace("\\", "/") for line in scope.read_text(encoding="utf-8-sig").splitlines() if line.strip()}
	result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root, capture_output=True, check=True)
	return {name for name in result.stdout.decode("utf-8").split("\0") if name}


def collect(args) -> list[dict]:
	"""Convertit les derniers exports des outils en diagnostics normalisés."""
	rows = []
	for path in args.ruff:
		for row in read_json(path):
			rows.append({"tool": "Ruff", "file": row["filename"], "line": row["location"]["row"], "code": row.get("code") or "syntax",
						 "message": row["message"], "severity": row.get("severity", "error")})
	pattern = re.compile(r"^(.+?):(\d+)(?::\d+)?: (error|warning): (.*?)(?:  \[([^\]]+)\])?$")
	for path in args.mypy:
		text = path.read_text(encoding="utf-8-sig")
		if "INTERNAL ERROR" in text or "Traceback (most recent call last)" in text:
			args.note.append(f"Mypy : export partiel ou échec interne dans {path.name} ; consulter le journal.")
		for line in text.splitlines():
			match = pattern.match(line)
			if match:
				file, number, severity, message, code = match.groups()
				rows.append({"tool": "Mypy", "file": file, "line": int(number), "code": code or "mypy", "message": message, "severity": severity})
	for directory in args.pycharm:
		files = sorted(path for path in directory.glob("*.xml") if path.stem.startswith(("Py", "Rest")))
		if not files: args.note.append(f"PyCharm : aucun export XML trouvé dans {directory}.")
		for path in files:
			try: tree = ET.parse(path)
			except ET.ParseError:
				args.note.append(f"PyCharm : export XML incomplet ou invalide : {path.name}.")
				continue
			for problem in tree.findall("problem"):
				kind = problem.find("problem_class")
				rows.append({"tool": "PyCharm", "file": problem.findtext("file", ""), "line": problem.findtext("line", "1"),
							 "code": kind.get("id", path.stem) if kind is not None else path.stem,
							 "severity": kind.get("severity", "warning").lower() if kind is not None else "warning",
							 "message": problem.findtext("description", "")})
	for path in args.diagnostics:
		data = read_json(path)
		rows.extend(data["rows"] if isinstance(data, dict) else data)
	return rows


def prepare(root: Path, raw: list[dict], allowed: set[str], decisions: dict) -> tuple[list[dict], Counter]:
	"""Filtre, déduplique et qualifie les diagnostics, puis embarque les extraits actuels."""
	unique = {}
	counts = Counter()
	paths = {}
	contents = {}
	for item in raw:
		filename = str(item.get("file", ""))
		if filename not in paths: paths[filename] = source_path(root, filename)
		path = paths[filename]
		if path is None or not path.is_file(): continue
		file = path.relative_to(root).as_posix()
		if file not in allowed: continue
		row = dict(item, file=file, line=max(1, int(item.get("line") or 1)), code=str(item.get("code", "")))
		key = tuple(row[name] for name in ("tool", "file", "line", "code", "message"))
		identifier = hashlib.sha256(json.dumps(key, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
		counts[row["tool"]] += 1
		if identifier in unique:
			unique[identifier]["occurrences"] += 1
			continue
		row.update(id=identifier, occurrences=1, severity=row.get("severity", "warning"), status=row.get("status", "À examiner"),
				   reason=row.get("reason", "Examiner le contexte : ce diagnostic ne prouve pas à lui seul un bug."),
				   evidence=row.get("evidence", "Qualification à poursuivre"))
		if row["tool"] == "Mypy" and row["code"] == "import-untyped":
			row.update(status="Limite de l'outil", reason="Bibliothèque sans stubs ou marqueur py.typed ; aucun composant installé par ce générateur.",
					   evidence="Limite de typage signalée par Mypy")
		if row["tool"] == "PyCharm" and row["code"] == "PyArgumentEqualDefaultInspection":
			row.update(status="Convention conservée", reason="Un argument explicite peut préciser l’intention même s’il correspond à la valeur par défaut ; conserver cet appel.",
					   evidence="Convention de lisibilité acceptée")
		for name in ("status", "reason", "evidence"):
			if name in decisions.get(identifier, {}): row[name] = decisions[identifier][name]
		try:
			if path not in contents: contents[path] = path.read_text(encoding="utf-8-sig").splitlines()
			lines = contents[path]
			row["excerpt"] = "\n".join(f"{n:4}  {lines[n - 1]}" for n in range(max(1, row["line"] - 1), min(len(lines), row["line"] + 1) + 1))
		except (UnicodeError, OSError): row["excerpt"] = "Extrait indisponible ; consulter le fichier source."
		row["href"] = path.as_uri()
		unique[identifier] = row
	return list(unique.values()), counts


def main():
	"""Lit les paramètres et écrit le rapport HTML autonome et ses données de revue."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--root", type=Path, required=True, help="Racine du dépôt à inspecter.")
	parser.add_argument("--output", type=Path, help="Rapport de sortie ; défaut : <root>/_output/remaining-diagnostics.html.")
	parser.add_argument("--title", help="Nom affiché du projet ; défaut : nom du dossier racine.")
	parser.add_argument("--review-key", help="Clé de relecture existante à préserver lors de la migration d’un ancien rapport.")
	for name in ("ruff", "mypy", "pycharm", "diagnostics"):
		parser.add_argument(f"--{name}", type=Path, action="append", default=[], help="Export de la passe ; option répétable.")
	parser.add_argument("--scope-file", type=Path, help="Chemins relatifs du périmètre, un par ligne.")
	parser.add_argument("--decisions", type=Path, help="Qualifications vérifiées, indexées par identifiant du diagnostic.")
	parser.add_argument("--note", action="append", default=[], help="Périmètre, vérifications, versions ou limites ; option répétable.")
	args = parser.parse_args()
	if not any((args.ruff, args.mypy, args.pycharm, args.diagnostics)): parser.error("Fournir au moins un export d’analyse.")
	root = args.root.resolve()
	output = args.output or root / "_output/remaining-diagnostics.html"
	allowed = project_files(root, args.scope_file)
	decisions = read_json(args.decisions) if args.decisions else {}
	rows, counts = prepare(root, collect(args), allowed, decisions)
	data = {"rows": rows, "counts": counts}
	template = (Path(__file__).resolve().parent.parent / "assets/inspection_report.html").read_text(encoding="utf-8")
	payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
	project_key = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
	review_key = args.review_key or f"inspection-report-{project_key}"
	if not args.review_key and output.is_file():
		previous = re.search(r"const size=60,key='([A-Za-z0-9_-]+)'", output.read_text(encoding="utf-8"))
		if previous: review_key = previous.group(1)
	if not re.fullmatch(r"[A-Za-z0-9_-]+", review_key): parser.error("La clé de relecture doit contenir uniquement lettres, chiffres, tirets et underscores.")
	notes = args.note or ["Exports fournis uniquement ; aucune vérification fonctionnelle exécutée par le générateur."]
	context = "".join(f"<p>{html.escape(note)}</p>" for note in notes)
	for token, value in {"@@PROJECT@@": html.escape(args.title or root.name), "@@DATE@@": datetime.date.today().isoformat(),
						 "@@PROJECT_KEY@@": project_key, "@@REVIEW_KEY@@": review_key, "@@CONTEXT@@": context, "@@DATA@@": payload}.items():
		template = template.replace(token, value)
	output.parent.mkdir(parents=True, exist_ok=True)
	output.write_bytes(template.encode("utf-8"))
	output.with_suffix(".data.json").write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
	print(json.dumps({"path": str(output.resolve()), "counts": counts, "distinct": len(rows)}, ensure_ascii=False))


if __name__ == "__main__": main()
