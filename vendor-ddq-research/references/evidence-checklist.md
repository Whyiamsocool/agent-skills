# Vendor DDQ Evidence Checklist

Use this checklist to map research output to due diligence requirements.

## Core Evidence Categories

1. Corporate profile
- Legal entity name
- Headquarters and operating regions
- Service scope and business model

2. Governance and risk
- Risk management framework
- Third-party/sub-outsourcing controls
- Board or management oversight disclosures

3. Information security
- Security policy summary
- Access control and IAM controls
- Vulnerability management or penetration testing statements
- Incident response process

4. Business continuity
- Business continuity/disaster recovery statements
- Recovery objectives or resilience commitments

5. Compliance and legal
- Regulatory licenses/registrations (if applicable)
- Privacy commitments and subprocessors
- Sanctions/AML statements (if applicable)

6. Financial and operational resilience
- Financial reports or public indicators
- Service uptime, SLA, and support model

## SOC Report Expectations

Priority order:
1. SOC 2 Type II
2. SOC 1 Type II
3. SOC 3 (public summary only)

Accept as candidate SOC evidence when:
- URL, filename, title, or snippet contains SOC terms (`soc`, `soc 1`, `soc 2`, `type ii`, `service auditor`)
- File is downloadable (PDF/DOC/DOCX)

If not publicly downloadable:
- Record all trust center/contact URLs.
- Generate a request email asking for:
  - Latest SOC report period
  - Report type (SOC 1/2, Type I/II)
  - Bridge letter (if report period has gap)
  - NDA requirements and access process

## Output Requirements

- Every evidence item must include:
  - source URL
  - title/snippet
  - category tags
  - whether downloaded
  - local file path (if downloaded)

- SOC status file must state one of:
  - `FOUND_PUBLIC_SOC_REPORT`
  - `SOC_CANDIDATES_FOUND_BUT_NOT_DOWNLOADED`
  - `NO_PUBLIC_SOC_REPORT_FOUND`
