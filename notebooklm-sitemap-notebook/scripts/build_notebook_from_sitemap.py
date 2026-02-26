#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import OrderedDict

UUID_RE = re.compile(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I)
URL_RE = re.compile(r"https?://\S+", re.I)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-notebooklm-sitemap-skill/1.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_llms_txt(content: str):
    urls = []
    for m in re.finditer(r"\[[^\]]+\]\((https?://[^)]+)\)", content):
        urls.append(m.group(1).strip())
    return urls


def parse_sitemap_xml(url: str, content: str, seen=None):
    if seen is None:
        seen = set()
    if url in seen:
        return []
    seen.add(url)

    urls = []
    root = ET.fromstring(content)
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    if root.tag.endswith("sitemapindex"):
        for sm in root.findall(f".//{ns}sitemap/{ns}loc"):
            sm_url = (sm.text or "").strip()
            if not sm_url:
                continue
            try:
                sub = fetch(sm_url)
                urls.extend(parse_sitemap_xml(sm_url, sub, seen=seen))
            except Exception:
                continue
        return urls

    for loc in root.findall(f".//{ns}url/{ns}loc"):
        u = (loc.text or "").strip()
        if u:
            urls.append(u)
    return urls


def dedupe_keep_order(items):
    return list(OrderedDict((x, True) for x in items if x).keys())


def normalize_url(u: str, drop_md_suffix: bool):
    u = u.strip()
    if drop_md_suffix and u.endswith(".md"):
        u = u[:-3]
    return u


def apply_filters(urls, include_pat=None, exclude_pat=None):
    out = []
    inc = re.compile(include_pat) if include_pat else None
    exc = re.compile(exclude_pat) if exclude_pat else None
    for u in urls:
        if inc and not inc.search(u):
            continue
        if exc and exc.search(u):
            continue
        out.append(u)
    return out


def run(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def create_notebook(title):
    code, out = run(["notebooklm", "create", title])
    if code != 0:
        raise RuntimeError(f"Failed creating notebook: {out}")
    m = UUID_RE.search(out)
    if not m:
        raise RuntimeError(f"Could not parse notebook id from output: {out}")
    return m.group(1), out


def list_sources(notebook_id):
    code, out = run(["notebooklm", "source", "list", "-n", notebook_id, "--json"])
    if code != 0:
        return []
    try:
        data = json.loads(out)
        urls = [s.get("url", "") for s in data.get("sources", []) if s.get("url")]
        return dedupe_keep_order(urls)
    except Exception:
        # fallback best-effort regex parse
        urls = []
        for m in URL_RE.finditer(out):
            urls.append(m.group(0).rstrip(")"))
        return dedupe_keep_order(urls)


def add_source(notebook_id, url):
    code, out = run(["notebooklm", "source", "add", "-n", notebook_id, url])
    return code == 0, out


def main():
    ap = argparse.ArgumentParser(description="Build/update NotebookLM notebook from sitemap.xml or llms.txt")
    ap.add_argument("--sitemap-url", required=True)
    ap.add_argument("--title", help="Notebook title when creating a new notebook")
    ap.add_argument("--notebook-id", help="Existing notebook id to update")
    ap.add_argument("--max-urls", type=int, default=200)
    ap.add_argument("--include", dest="include_pat")
    ap.add_argument("--exclude", dest="exclude_pat")
    ap.add_argument("--drop-md-suffix", action="store_true", help="Normalize .../page.md to .../page")
    ap.add_argument("--sync", action="store_true", help="Update mode: add only missing URLs to existing notebook")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.notebook_id and not args.title:
        raise SystemExit("Provide either --title (create) or --notebook-id (update).")
    if args.sync and not args.notebook_id:
        raise SystemExit("--sync requires --notebook-id.")

    raw = fetch(args.sitemap_url)
    lower = args.sitemap_url.lower()
    is_llms = lower.endswith("llms.txt") or "\n## Docs\n" in raw[:4000] or "# " in raw[:100]

    if is_llms:
        urls = parse_llms_txt(raw)
    else:
        urls = parse_sitemap_xml(args.sitemap_url, raw)

    drop_md = args.drop_md_suffix or is_llms
    urls = [normalize_url(u, drop_md) for u in urls]
    urls = dedupe_keep_order(urls)
    urls = apply_filters(urls, include_pat=args.include_pat, exclude_pat=args.exclude_pat)
    if args.max_urls > 0:
        urls = urls[: args.max_urls]

    report = {
        "sitemap_url": args.sitemap_url,
        "url_count": len(urls),
        "dry_run": args.dry_run,
        "mode": "sync" if args.sync else "create" if not args.notebook_id else "update",
    }

    notebook_id = args.notebook_id
    create_out = ""

    if not notebook_id and not args.dry_run:
        notebook_id, create_out = create_notebook(args.title)
        report["title"] = args.title
        report["create_output"] = create_out.strip()
    elif not notebook_id and args.dry_run:
        report["title"] = args.title
        report["notebook_id"] = "(will-create)"

    if notebook_id:
        report["notebook_id"] = notebook_id

    to_add = urls
    existing = []
    if args.sync:
        existing = list_sources(notebook_id)
        existing_set = set(existing)
        to_add = [u for u in urls if u not in existing_set]

    if args.dry_run:
        report["urls_preview"] = urls[:20]
        if args.sync:
            report["existing_count_detected"] = len(existing)
            report["to_add_count"] = len(to_add)
            report["to_add_preview"] = to_add[:20]
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    ok = 0
    failed = []
    for u in to_add:
        success, out = add_source(notebook_id, u)
        if success:
            ok += 1
        else:
            failed.append({"url": u, "error": out.strip()[:500]})

    report.update(
        {
            "expected": len(urls),
            "attempted_add": len(to_add),
            "imported": ok,
            "failed": len(failed),
            "failed_items": failed[:20],
        }
    )
    if args.sync:
        report["existing_count_detected"] = len(existing)
        report["skipped_existing"] = len(urls) - len(to_add)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
