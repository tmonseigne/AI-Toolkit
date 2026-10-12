"""Retire une suite vérifiée de numéros de ligne textuels dans la marge d'un PDF."""
from __future__ import annotations

import argparse
import hashlib
import json
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, ByteStringObject, ContentStream, DecodedStreamObject, NameObject, TextStringObject


def tokens(page):
    """Relève les blocs de texte visibles et leur police sans modifier le PDF."""
    rows = []

    def visit(text, cm, tm, font, size):
        if text.strip():
            rows.append((text, round(float(cm[4] + tm[4]), 2), round(float(size), 3)))

    page.extract_text(visitor_text=visit)
    return rows


def main():
    """Contrôle la suite avant retrait, puis vérifie le PDF rouvert."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--font-size", type=float, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--margin-fraction", type=float, default=0.12)
    args = parser.parse_args()
    paths = [x.resolve() for x in (args.source, args.output, args.manifest)]
    if len(set(paths)) != 3 or args.output.exists() or args.manifest.exists():
        parser.error("Chemins distincts et sorties absentes requis.")
    reader = PdfReader(args.source)
    if reader.is_encrypted:
        raise ValueError("PDF chiffré.")
    # Une signature invaliderait toute réécriture.
    if reader.get_fields() and any(str(f.get("/FT")) == "/Sig" for f in reader.get_fields().values()):
        raise ValueError("PDF signé.")
    before = [tokens(page) for page in reader.pages]
    line_numbers = []
    for page, rows in zip(reader.pages, before):
        width = float(page.mediabox.width)
        line_numbers += [
            int(text.strip()) for text, x, size in rows
            if text.strip().isdecimal()
            and abs(size - args.font_size) < 0.003
            and x <= width * args.margin_fraction
        ]
    if line_numbers != list(range(1, args.expected_count + 1)):
        raise ValueError(f"Suite de marge inattendue : {len(line_numbers)} éléments ; premier={line_numbers[:5]}, dernier={line_numbers[-5:]}")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    removed = []
    for page in writer.pages:
        stream = ContentStream(page.get_contents(), writer)
        size = None
        operations = []
        for operands, op in stream.operations:
            if op == b"Tf":
                size = float(operands[1])
            elif size is not None and abs(size - args.font_size) < 0.003 and op in (b"Tj", b"TJ"):
                if op == b"Tj" and len(operands) == 1 and str(operands[0]).isdecimal():
                    removed.append(int(str(operands[0])))
                    operands = [TextStringObject("")]
                elif op == b"TJ":
                    replacement = []
                    for value in operands[0]:
                        if isinstance(value, (TextStringObject, ByteStringObject)) and str(value).isdecimal():
                            removed.append(int(str(value)))
                            replacement.append(TextStringObject(""))
                        else:
                            replacement.append(value)
                    operands = [ArrayObject(replacement)]
            operations.append((operands, op))
        stream.operations = operations
        packed = DecodedStreamObject()
        packed.set_data(stream.get_data())
        page[NameObject("/Contents")] = writer._add_object(packed.flate_encode())
    if removed != line_numbers:
        raise ValueError("Les objets PDF ne correspondent pas aux numéros de marge détectés.")
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    # Le clonage conserve les anciens flux de pages devenus orphelins.
    # Les supprimer évite de doubler les grandes figures vectorielles.
    writer.compress_identical_objects(remove_duplicates=False, remove_unreferenced=True)
    buffer = BytesIO()
    writer.write(buffer)
    reopened = PdfReader(BytesIO(buffer.getvalue()))
    after = [tokens(page) for page in reopened.pages]
    if len(after) != len(before):
        raise ValueError("Pagination modifiée.")
    for index, (old, new) in enumerate(zip(before, after), 1):
        width = float(reader.pages[index-1].mediabox.width)
        kept = [
            text for text, x, size in old
            if not (text.strip().isdecimal() and abs(size - args.font_size) < 0.003
                    and x <= width * args.margin_fraction)
        ]
        if kept != [text for text, _, _ in new]:
            raise ValueError(f"Texte hors numéros modifié page {index}.")
        old_page, new_page = reader.pages[index-1], reopened.pages[index-1]
        if old_page.mediabox != new_page.mediabox or (len(old_page["/Annots"]) if "/Annots" in old_page else 0) != (len(new_page["/Annots"]) if "/Annots" in new_page else 0):
            raise ValueError(f"Géométrie ou annotations modifiées page {index}.")
    with output.open("xb") as handle:
        handle.write(buffer.getvalue())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "source": str(args.source), "output": str(output),
        "source_sha256": sha(args.source), "output_sha256": sha(output),
        "before_bytes": args.source.stat().st_size, "after_bytes": output.stat().st_size,
        "pages": len(reopened.pages), "line_numbers_removed": len(removed),
        "range": [removed[0], removed[-1]], "other_text_preserved": True,
        "page_geometry_and_annotation_counts_preserved": True,
        "visual_review": "pending",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
