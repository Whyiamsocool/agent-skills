# NotebookLM Document Review Skill

Vendor-neutral agent skill to review documents against your NotebookLM notebooks, identify gaps, assess alignment, and generate recommendations.

## What It Does

- Extracts content from `.docx`, `.pdf`, `.txt`, and `.md`
- Selects relevant NotebookLM notebooks based on document keywords
- Queries selected notebooks for requirements
- Generates a markdown report with findings

## Prerequisites

- Python 3.7+
- NotebookLM skill installed in your agent skills directory
- NotebookLM authentication completed
- At least one notebook in your NotebookLM library

## Installation

From this repository structure:

```bash
agent-skills/
  skills/
    nblm-doc-review/
```

Use the `skills/nblm-doc-review` folder directly in your runtime, or set:

```bash
export NOTEBOOKLM_SKILL_DIR="$HOME/.codex/skills/notebooklm"
```

If `NOTEBOOKLM_SKILL_DIR` is not set, scripts try:
1. `$HOME/.codex/skills/notebooklm`

## Usage

```bash
cd skills/nblm-doc-review
python3 scripts/review_document.py /path/to/document.docx
```

### Common Options

```bash
python3 scripts/review_document.py /path/to/document.docx --output gap
python3 scripts/review_document.py /path/to/document.docx --depth quick
python3 scripts/review_document.py /path/to/document.docx --threshold 3
```

- `--output`: `gap`, `alignment`, `recommendations`, or `all` (default)
- `--depth`: `quick` or `detailed` (default)
- `--threshold`: notebook relevance threshold (default `5`)

## Structure

```text
skills/nblm-doc-review/
├── SKILL.md
├── nblm-doc-review.skill
├── scripts/
│   ├── review_document.py
│   ├── extract_content.py
│   ├── notebook_selector.py
│   └── compliance_checker.py
└── references/
    ├── report_formats.md
    └── analysis_guide.md
```

## Troubleshooting

- No notebooks found: lower `--threshold` and confirm notebook library has entries.
- Query fails: verify NotebookLM auth and that `NOTEBOOKLM_SKILL_DIR` points to the correct location.
- PDF extract fails: install PyPDF2 (`pip install PyPDF2`).

## License

MIT
