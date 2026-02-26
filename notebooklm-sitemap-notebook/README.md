# sitemap2notebooklm

Create or update a NotebookLM notebook from a `sitemap.xml` or `llms.txt` index.

## What it does
- Extracts URLs from sitemap/index
- Normalizes URLs (including `.md` stripping for `llms.txt` links)
- Deduplicates URLs
- Creates a new notebook or syncs an existing notebook
- Outputs JSON summary for verification/auditing

## Files
- `SKILL.md` — skill trigger + usage instructions
- `scripts/build_notebook_from_sitemap.py` — main CLI script

## Requirements
- Python 3.9+
- `notebooklm` CLI installed and authenticated

## Quick start

### 1) Dry-run (preview URLs)
```bash
python3 scripts/build_notebook_from_sitemap.py \
  --sitemap-url "https://docs.example.com/llms.txt" \
  --title "Product Docs" \
  --dry-run
```

### 2) Create notebook from sitemap/index
```bash
python3 scripts/build_notebook_from_sitemap.py \
  --sitemap-url "https://docs.example.com/sitemap.xml" \
  --title "Product Docs" \
  --max-urls 500
```

### 3) Sync existing notebook (future updates)
```bash
python3 scripts/build_notebook_from_sitemap.py \
  --sitemap-url "https://docs.example.com/sitemap.xml" \
  --notebook-id "<existing_notebook_id>" \
  --sync \
  --max-urls 500
```

## Useful flags
- `--include "regex"` only include matching URLs
- `--exclude "regex"` exclude matching URLs
- `--drop-md-suffix` force `.../page.md` -> `.../page`
- `--dry-run` preview without importing

## Example output (sync)
```json
{
  "mode": "sync",
  "expected": 58,
  "attempted_add": 0,
  "imported": 0,
  "failed": 0,
  "skipped_existing": 58
}
```

## Notes
- Universal for any docs site exposing `sitemap.xml` or `llms.txt`.
- In sync mode, this script currently adds missing URLs only (no deletions).
