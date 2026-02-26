#!/usr/bin/env python3
"""
Extract requirement-like prompts/questions from DDQ source documents.
Supports .docx files and directories containing .docx files.
"""

import argparse
import csv
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def is_heading(text):
    if len(text) > 120:
        return False
    if text.endswith(":"):
        return True
    alpha = re.sub(r"[^A-Za-z ]", "", text)
    return bool(alpha) and alpha.isupper()


def is_requirement_line(text):
    if not text or len(text) < 8:
        return False
    if text.endswith("?"):
        return True
    patterns = [
        r"^(q(uestion)?\s*\d+[:.)-]?)",
        r"^\d+(\.\d+)*[.)-]\s+",
        r"\b(please|provide|describe|explain|confirm|state|attach|submit|include)\b",
        r"\b(shall|must|required|requirement)\b",
    ]
    lowered = text.lower()
    return any(re.search(p, lowered) for p in patterns)


def collect_docx_paths(inputs):
    found = []
    for item in inputs:
        p = Path(item).expanduser()
        if p.is_dir():
            found.extend(sorted(p.rglob("*.docx")))
        elif p.is_file() and p.suffix.lower() == ".docx":
            found.append(p)
    # preserve order and remove duplicates
    seen = set()
    unique = []
    for p in found:
        if str(p) not in seen:
            unique.append(p)
            seen.add(str(p))
    return unique


def extract_paragraph_texts(docx_path):
    rows = []
    with zipfile.ZipFile(docx_path, "r") as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    current_section = ""

    for p in root.iter(f"{W_NS}p"):
        text_parts = [t.text or "" for t in p.iter(f"{W_NS}t")]
        text = normalize_text("".join(text_parts))
        if not text:
            continue

        if is_heading(text):
            current_section = text.rstrip(":")
            continue

        rows.append({"text": text, "section": current_section})

    return rows


def keywords_from_text(text, limit=8):
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
        "have", "has", "will", "shall", "must", "should", "can", "you", "your",
        "please", "provide", "describe", "explain", "include", "state",
    }
    freq = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [w for w, _ in ranked[:limit]]


def main():
    parser = argparse.ArgumentParser(description="Extract DDQ requirements from docx sources.")
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Input .docx file or directory containing .docx files (repeatable).",
    )
    parser.add_argument("--output-dir", required=True, help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    docx_files = collect_docx_paths(args.input)
    if not docx_files:
        raise SystemExit("No .docx files found from provided --input paths.")

    requirements = []
    req_id = 1

    for doc in docx_files:
        for row in extract_paragraph_texts(doc):
            text = row["text"]
            if not is_requirement_line(text):
                continue
            requirements.append(
                {
                    "id": f"R{req_id:04d}",
                    "source_file": str(doc),
                    "section": row["section"],
                    "requirement": text,
                    "keywords": keywords_from_text(text),
                }
            )
            req_id += 1

    req_json = out_dir / "requirements.json"
    req_csv = out_dir / "requirements.csv"
    req_md = out_dir / "requirements_summary.md"

    req_json.write_text(json.dumps(requirements, indent=2), encoding="utf-8")

    with req_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "source_file", "section", "requirement", "keywords"],
        )
        writer.writeheader()
        for r in requirements:
            writer.writerow(
                {
                    "id": r["id"],
                    "source_file": r["source_file"],
                    "section": r["section"],
                    "requirement": r["requirement"],
                    "keywords": ",".join(r["keywords"]),
                }
            )

    lines = []
    lines.append("# Requirements Summary")
    lines.append("")
    lines.append(f"- Source documents: {len(docx_files)}")
    lines.append(f"- Requirements extracted: {len(requirements)}")
    lines.append("")
    lines.append("## Top Requirements")
    lines.append("")
    for r in requirements[:30]:
        sec = f" ({r['section']})" if r["section"] else ""
        lines.append(f"- `{r['id']}`{sec}: {r['requirement']}")
    req_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {req_json}")
    print(f"Wrote: {req_csv}")
    print(f"Wrote: {req_md}")
    print(f"Extracted {len(requirements)} requirements from {len(docx_files)} files.")


if __name__ == "__main__":
    main()
