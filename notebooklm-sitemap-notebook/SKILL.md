---
name: notebooklm-sitemap-notebook
description: Create or update a NotebookLM notebook from sitemap.xml or llms.txt by extracting URLs, normalizing links, deduplicating, and importing sources in bulk. Use when the user wants repeatable notebook bootstrapping or ongoing sitemap-based sync for any docs site (not only Claude Code docs).
---

# NotebookLM Sitemap Notebook

Use this skill for **any documentation site** that exposes either:
- `sitemap.xml` (or sitemap index), or
- `llms.txt` with markdown links.

## What it does
1. Extract URLs from sitemap/index.
2. Normalize links (for `llms.txt`, strip `.md` suffix by default).
3. Deduplicate URL list.
4. Create a new NotebookLM notebook **or** update an existing one.
5. Return JSON audit summary (expected/attempted/imported/failed).

## Create a new notebook

```bash
python3 scripts/build_notebook_from_sitemap.py \
  --sitemap-url "<sitemap_or_llms_txt_url>" \
  --title "<Notebook Title>" \
  --max-urls 200
```

## Dry-run (always do this first)

```bash
python3 scripts/build_notebook_from_sitemap.py \
  --sitemap-url "<sitemap_or_llms_txt_url>" \
  --title "<Notebook Title>" \
  --max-urls 200 \
  --dry-run
```

## Update existing notebook from sitemap index (future sync)
Use this to keep your notebook fresh over time.

```bash
python3 scripts/build_notebook_from_sitemap.py \
  --sitemap-url "<sitemap_or_llms_txt_url>" \
  --notebook-id "<existing_notebook_id>" \
  --sync \
  --max-urls 500
```

`--sync` behavior:
- reads current source list,
- compares with sitemap-derived URLs,
- adds only missing URLs,
- reports skipped existing vs newly imported.

## Optional filters

```bash
--include "regex"
--exclude "regex"
```

Examples:
- include only English docs: `--include "/en/"`
- exclude changelog pages: `--exclude "changelog|release-notes"`

## Notes
- Universal: works for any docs site with `sitemap.xml` or `llms.txt` index.
- `llms.txt` links ending in `.md` are normalized automatically (prevents common import failures).
- For strict behavior, you can force suffix removal with `--drop-md-suffix`.
- Output is JSON so it can be logged/audited or piped into automation.
