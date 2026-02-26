#!/usr/bin/env python3
"""
Research vendor DDQ evidence online and download document artifacts.
Prioritizes SOC report discovery and tracks SOC status.
"""

import argparse
import csv
import html
import json
import os
import re
import ssl
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError, HTTPError

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

DOC_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"}
SOC_TERMS = ("soc", "soc 1", "soc 2", "type ii", "service auditor", "aicpa")


def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


class DDGResultsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.current = None
        self.capture_title = False
        self.capture_snippet = False
        self.title_buf = []
        self.snippet_buf = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "")
        if tag == "a" and "result__a" in classes:
            if self.current:
                self.current["title"] = self.current.get("title", "").strip()
                self.current["snippet"] = self.current.get("snippet", "").strip()
                self.results.append(self.current)
            self.current = {
                "url": attrs_dict.get("href", ""),
                "title": "",
                "snippet": "",
            }
            self.capture_title = True
            self.title_buf = []
        elif self.current and (
            ("result__snippet" in classes and tag in {"a", "div"})
        ):
            self.capture_snippet = True
            self.snippet_buf = []

    def handle_data(self, data):
        if self.capture_title:
            self.title_buf.append(data)
        if self.capture_snippet:
            self.snippet_buf.append(data)

    def handle_endtag(self, tag):
        if self.capture_title and tag == "a":
            self.current["title"] = normalize_text("".join(self.title_buf))
            self.capture_title = False
        elif self.capture_snippet and tag in {"a", "div"}:
            self.current["snippet"] = normalize_text("".join(self.snippet_buf))
            self.capture_snippet = False
            if self.current:
                self.results.append(self.current)
                self.current = None


def parse_bing_results(page, max_results):
    block_pattern = re.compile(r'<li class="b_algo".*?</li>', re.DOTALL)
    link_pattern = re.compile(r'<h2><a href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a></h2>', re.DOTALL)
    snippet_pattern = re.compile(r'<p>(?P<snippet>.*?)</p>', re.DOTALL)
    results = []
    for block in block_pattern.findall(page):
        lm = link_pattern.search(block)
        if not lm:
            continue
        sm = snippet_pattern.search(block)
        title = normalize_text(re.sub(r"<[^>]+>", "", lm.group("title")))
        snippet = normalize_text(re.sub(r"<[^>]+>", "", sm.group("snippet"))) if sm else ""
        results.append(
            {
                "url": html.unescape(lm.group("href")),
                "title": html.unescape(title),
                "snippet": html.unescape(snippet),
            }
        )
        if len(results) >= max_results:
            break
    return results


def safe_slug(text):
    return re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-") or "item"


def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
    except URLError as exc:
        reason = getattr(exc, "reason", None)
        if not isinstance(reason, ssl.SSLCertVerificationError):
            raise
        # Some enterprise networks re-sign TLS traffic with private CAs.
        insecure_ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=insecure_ctx) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
    except ssl.SSLCertVerificationError:
        # Some enterprise networks re-sign TLS traffic with private CAs.
        insecure_ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=insecure_ctx) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
    return data, content_type


def search_duckduckgo(query, max_results=8):
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://duckduckgo.com/html/?{encoded}"
    try:
        page_bytes, _ = fetch_url(url)
    except (HTTPError, URLError, TimeoutError):
        return []

    page = page_bytes.decode("utf-8", errors="ignore")
    parser = DDGResultsParser()
    parser.feed(page)
    if parser.current:
        parser.current["title"] = parser.current.get("title", "").strip()
        parser.current["snippet"] = parser.current.get("snippet", "").strip()
        parser.results.append(parser.current)
    results = []
    for item in parser.results:
        href = html.unescape(item["url"])
        title = item["title"]
        snippet = item["snippet"]
        # DDG redirect link often contains uddg
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        if "uddg" in qs:
            href = urllib.parse.unquote(qs["uddg"][0])
        results.append(
            {
                "url": href,
                "title": html.unescape(title).strip(),
                "snippet": html.unescape(snippet).strip(),
            }
        )
        if len(results) >= max_results:
            break
    return results


def search_bing(query, max_results=8):
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://www.bing.com/search?{encoded}"
    try:
        page_bytes, _ = fetch_url(url)
    except (HTTPError, URLError, TimeoutError):
        return []
    page = page_bytes.decode("utf-8", errors="ignore")
    return parse_bing_results(page, max_results=max_results)


def search_web(query, max_results=8):
    ddg = search_duckduckgo(query, max_results=max_results)
    if ddg:
        return ddg
    return search_bing(query, max_results=max_results)


def extract_requirement_keywords(requirements_path, limit=20):
    if not requirements_path:
        return []
    path = Path(requirements_path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    freq = {}
    for row in data:
        for kw in row.get("keywords", []):
            if len(kw) < 3:
                continue
            freq[kw.lower()] = freq.get(kw.lower(), 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [k for k, _ in ranked[:limit]]


def build_queries(vendor, requirement_keywords):
    base = [
        f"{vendor} trust center",
        f"{vendor} security whitepaper",
        f"{vendor} compliance",
        f"{vendor} privacy policy",
        f"{vendor} business continuity disaster recovery",
        f"{vendor} SOC 2 Type II report",
        f"{vendor} SOC 1 Type II report",
        f"{vendor} SOC report",
        f"{vendor} service organization controls",
    ]
    for kw in requirement_keywords[:8]:
        base.append(f"{vendor} {kw}")
    # Deduplicate while preserving order
    seen = set()
    out = []
    for q in base:
        norm = q.lower().strip()
        if norm not in seen:
            seen.add(norm)
            out.append(q)
    return out


def guess_ext_from_url(url):
    path = urllib.parse.urlparse(url).path.lower()
    for ext in DOC_EXTENSIONS:
        if path.endswith(ext):
            return ext
    return ""


def contains_soc_text(*values):
    blob = " ".join((v or "").lower() for v in values)
    return any(term in blob for term in SOC_TERMS)


def maybe_download(url, out_dir, index):
    ext = guess_ext_from_url(url)
    if not ext:
        return None, None
    filename = f"{index:03d}-{safe_slug(Path(urllib.parse.urlparse(url).path).stem)}{ext}"
    path = out_dir / filename
    try:
        data, content_type = fetch_url(url)
        if len(data) > 30 * 1024 * 1024:
            return None, "File too large (>30MB)"
        path.write_bytes(data)
        return str(path), content_type
    except Exception as exc:
        return None, str(exc)


def write_soc_status(out_dir, soc_downloaded, soc_candidates, vendor):
    status_file = out_dir / "soc_status.md"
    lines = ["# SOC Status", ""]
    if soc_downloaded:
        lines.append("FOUND_PUBLIC_SOC_REPORT")
        lines.append("")
        lines.append("Downloaded SOC-related artifacts:")
        for item in soc_downloaded:
            lines.append(f"- {item['download_path']}")
    elif soc_candidates:
        lines.append("SOC_CANDIDATES_FOUND_BUT_NOT_DOWNLOADED")
        lines.append("")
        lines.append("Candidate sources:")
        for item in soc_candidates[:10]:
            lines.append(f"- {item['url']}")
    else:
        lines.append("NO_PUBLIC_SOC_REPORT_FOUND")
        lines.append("")
        lines.append("No SOC report candidate was found from current search scope.")
    status_file.write_text("\n".join(lines), encoding="utf-8")

    if not soc_downloaded:
        email_file = out_dir / "soc_request_email.txt"
        email_file.write_text(
            (
                f"Subject: Request for SOC Report - {vendor}\n\n"
                f"Hello {vendor} team,\n\n"
                "As part of vendor due diligence, please share your latest SOC report package:\n"
                "- SOC 2 Type II (preferred), or SOC 1 Type II\n"
                "- Report period dates\n"
                "- Bridge letter if there is a coverage gap\n"
                "- Access requirements (NDA/portal)\n\n"
                "Please also provide the primary contact for follow-up.\n\n"
                "Thank you."
            ),
            encoding="utf-8",
        )


def main():
    parser = argparse.ArgumentParser(description="Collect vendor due diligence evidence from public sources.")
    parser.add_argument("--vendor", required=True, help="Vendor/service provider name.")
    parser.add_argument("--requirements", help="Path to requirements.json from extractor.")
    parser.add_argument("--output-dir", required=True, help="Output directory.")
    parser.add_argument("--max-results", type=int, default=8, help="Max search hits per query.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser()
    downloads_dir = output_dir / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    req_keywords = extract_requirement_keywords(args.requirements)
    queries = build_queries(args.vendor, req_keywords)

    all_rows = []
    download_counter = 1
    for query in queries:
        hits = search_web(query, max_results=args.max_results)
        for hit in hits:
            row = {
                "vendor": args.vendor,
                "query": query,
                "url": hit["url"],
                "title": hit["title"],
                "snippet": hit["snippet"],
                "downloaded": False,
                "download_path": "",
                "download_note": "",
                "soc_candidate": contains_soc_text(hit["url"], hit["title"], hit["snippet"]),
            }
            dpath, note = maybe_download(hit["url"], downloads_dir, download_counter)
            if dpath:
                row["downloaded"] = True
                row["download_path"] = dpath
                row["download_note"] = ""
                download_counter += 1
            elif note:
                row["download_note"] = note
            all_rows.append(row)

    # Write JSON
    (output_dir / "search_results.json").write_text(
        json.dumps(all_rows, indent=2), encoding="utf-8"
    )

    # Write CSV index
    with (output_dir / "evidence_index.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "vendor",
                "query",
                "url",
                "title",
                "snippet",
                "downloaded",
                "download_path",
                "download_note",
                "soc_candidate",
            ],
        )
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    # SOC outputs
    soc_candidates = [r for r in all_rows if r["soc_candidate"]]
    soc_downloaded = [r for r in soc_candidates if r["downloaded"]]
    (output_dir / "soc_candidates.json").write_text(
        json.dumps(soc_candidates, indent=2), encoding="utf-8"
    )
    write_soc_status(output_dir, soc_downloaded, soc_candidates, args.vendor)

    # Human summary
    unique_urls = len({r["url"] for r in all_rows})
    downloaded = len([r for r in all_rows if r["downloaded"]])
    lines = [
        "# Vendor Evidence Summary",
        "",
        f"- Vendor: {args.vendor}",
        f"- Queries run: {len(queries)}",
        f"- URLs captured: {unique_urls}",
        f"- Files downloaded: {downloaded}",
        f"- SOC candidates: {len(soc_candidates)}",
        f"- SOC downloaded: {len(soc_downloaded)}",
        "",
        "## Top URLs",
        "",
    ]
    for row in all_rows[:25]:
        lines.append(f"- {row['url']}")
    (output_dir / "evidence_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {output_dir / 'search_results.json'}")
    print(f"Wrote: {output_dir / 'evidence_index.csv'}")
    print(f"Wrote: {output_dir / 'evidence_summary.md'}")
    print(f"Wrote: {output_dir / 'soc_candidates.json'}")
    print(f"Wrote: {output_dir / 'soc_status.md'}")
    if not soc_downloaded:
        print(f"Wrote: {output_dir / 'soc_request_email.txt'}")


if __name__ == "__main__":
    main()
