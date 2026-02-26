---
name: vendor-ddq-research
description: Research vendor or outsourcing service provider due diligence evidence from online sources, map findings to DDQ questionnaire requirements, download supporting documents, and prioritize SOC report collection. Use when user asks to perform vendor DDQ/TPRM research, complete outsourcing questionnaires, gather public compliance evidence, or obtain SOC reports based on policy/questionnaire documents (.docx, .pdf, .txt, .md).
---

# Vendor DDQ Research

Collect evidence for vendor due diligence and outsourcing questionnaires with repeatable scripts.

## Workflow

1. Extract questionnaire requirements from source documents.
2. Build vendor-specific search queries from those requirements.
3. Search online, collect evidence URLs, and download document artifacts.
4. Isolate SOC report candidates and determine if a SOC report was obtained.
5. If SOC report is not public, generate a request pack and evidence gap note.

## Inputs

- Vendor name (required)
- DDQ templates/policy documents (recommended)
- Output directory for research artifacts (required)

## Commands

Run from this skill folder.

### Step 1: Extract requirements
```bash
python3 scripts/extract_ddq_requirements.py \
  --input "/Users/dapeitan/Library/CloudStorage/OneDrive-RiverLabsPteLtd/_Sharepoint/2. Policy, Form [INTERNAL USE ONLY]/OED/DDQ Templates" \
  --input "/Users/dapeitan/Library/CloudStorage/OneDrive-RiverLabsPteLtd/_Sharepoint/2. Policy, Form [INTERNAL USE ONLY]/OED/G7.1. Outsourcing Policy - Service Provider Questionnaire (Template).docx" \
  --output-dir output/requirements
```

Output files:
- `requirements.json`
- `requirements.csv`
- `requirements_summary.md`

### Step 2: Research and download artifacts
```bash
python3 scripts/collect_vendor_evidence.py \
  --vendor "Vendor Name" \
  --requirements output/requirements/requirements.json \
  --output-dir output/vendor-name \
  --max-results 8
```

Output files:
- `search_results.json`
- `evidence_index.csv`
- `evidence_summary.md`
- `downloads/` (downloaded documents)
- `soc_candidates.json`
- `soc_status.md`
- `soc_request_email.txt` (if SOC report not found)

## Decision Rules

- Prefer first-party sources: vendor website, trust center, investor relations, official filings.
- Capture source URL for every claim.
- Treat marketing pages as secondary evidence; prioritize downloadable policies/reports.
- SOC report success condition:
  - Downloaded file is a report-like artifact containing SOC indicators in filename, URL, or nearby context.
- If no SOC report is downloaded, mark as gap and generate a request email.

## Deliverables

- Requirements extraction package (`requirements.*`)
- Evidence package (`search_results.json`, `evidence_index.csv`, `downloads/`)
- SOC package (`soc_candidates.json`, `soc_status.md`, optional `soc_request_email.txt`)

## References

- For evidence expectations and SOC handling, read [references/evidence-checklist.md](references/evidence-checklist.md).

## Notes

- Scripts use standard library only; no external Python package is required.
- Search uses DuckDuckGo HTML endpoint and may miss sources that block crawlers.
- Some SOC reports are private and require NDA/request workflow.
