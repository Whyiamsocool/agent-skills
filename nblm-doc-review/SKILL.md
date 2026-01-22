---
name: nblm-doc-review
description: Review any document against NotebookLM notebooks to identify gaps, assess alignment, and generate recommendations. REQUIRES NotebookLM skill to be installed and configured first. Use when user asks to "review this document against my notebooks", "check compliance alignment", "compare document to reference sources", or wants gap analysis for policies, procedures, contracts, proposals, or technical documentation. Works with .docx, .pdf, .txt, .md formats and queries all available NotebookLM notebooks intelligently.
---

# NotebookLM Document Alignment Reviewer

Review any document against your NotebookLM notebooks to identify gaps, assess alignment, and generate actionable recommendations.

## ⚠️ Prerequisites

**IMPORTANT: This skill requires the NotebookLM skill to be installed and configured first.**

Before using this skill, you must:
1. ✅ Install the NotebookLM skill
2. ✅ Authenticate with Google (`notebooklm auth_manager.py setup`)
3. ✅ Add at least one notebook to your library (`notebooklm notebook_manager.py add`)

This skill queries your NotebookLM notebooks at `~/.claude/skills/notebooklm/` and reads your notebook library at `~/.claude/skills/notebooklm/data/library.json`.

## When to Use This Skill

Trigger when user:
- Asks to review a document against notebooks/documentation
- Wants compliance or alignment checks
- Mentions "gap analysis", "document review", or "check against requirements"
- Uses phrases like:
  - "Review this document against my notebooks"
  - "Check compliance alignment"
  - "Compare my policy to regulatory requirements"
  - "What's missing from this document?"

## Quick Start

Basic review with all options enabled (default):
```bash
python scripts/review_document.py <document_path>
```

This will:
1. Extract document content
2. Intelligently select relevant NotebookLM notebooks
3. Query notebooks for comprehensive requirements
4. Generate report with gap analysis, alignment summary, and recommendations

## Workflow

### Step 1: Get Document Path

Ask user for the document to review. Supported formats:
- `.docx` - Word documents
- `.pdf` - PDF files
- `.txt` - Plain text
- `.md` - Markdown files

### Step 2: Determine Review Options

Ask user about review preferences (or use defaults):

**Output Options** (default: all):
- `gap` - Gap analysis (missing requirements)
- `alignment` - Alignment summary (coverage assessment)
- `recommendations` - Actionable recommendations
- `all` - All of the above (default)

**Review Depth** (default: detailed):
- `quick` - High-level summary, top findings only (~5-10 min)
- `detailed` - Comprehensive analysis with full coverage (~30-60 min)

**Notebook Threshold** (default: 5):
- Relevance score threshold for notebook selection
- Lower = more notebooks included
- Higher = only most relevant notebooks

### Step 3: Run Review

```bash
# Basic review (all options, detailed)
python scripts/review_document.py /path/to/document.docx

# Customized review
python scripts/review_document.py /path/to/document.docx --output gap,recommendations --depth quick --threshold 3

# Only gap analysis, detailed depth
python scripts/review_document.py /path/to/document.docx --output gap --depth detailed
```

The script will:
1. Extract document content using `extract_content.py`
2. Select relevant notebooks using `notebook_selector.py` based on content keywords
3. Query each selected notebook via NotebookLM integration
4. Compare document against requirements
5. Generate comprehensive report as `<document_name>_alignment_report.md`

### Step 4: Review Report

The generated report includes:
- **Executive Summary** - Overview of notebooks reviewed and relevance scores
- **Source Notebooks** - Details on reference sources used
- **Requirements Analysis** - Comprehensive requirements from each notebook
- **Gap Analysis** (if selected) - Missing or inadequate requirements
- **Alignment Summary** (if selected) - Coverage assessment by category
- **Recommendations** (if selected) - Prioritized actionable improvements

### Step 5: Follow-Up Questions

After initial review, you may want to:
- Query specific notebooks for more detail on certain requirements
- Ask follow-up questions about unclear requirements
- Request deeper analysis on specific sections

Use the NotebookLM skill directly for follow-up queries:
```bash
cd ~/.claude/skills/notebooklm
python3 scripts/run.py ask_question.py --question "Your follow-up question" --notebook-id <notebook-id>
```

## Output Options Detail

### Gap Analysis
Identifies requirements from reference sources that are:
- **Missing** - Not addressed at all in the document
- **Inadequate** - Partially covered but insufficient detail
- **Inconsistent** - Conflicts with reference requirements

See [references/report_formats.md](references/report_formats.md) for gap analysis template.

### Alignment Summary
Assesses how well the document covers requirements:
- Overall compliance score/assessment
- Coverage by category (table format)
- Well-covered areas (strengths)
- Areas needing improvement (weaknesses)

See [references/report_formats.md](references/report_formats.md) for alignment summary template.

### Recommendations
Provides prioritized, actionable guidance:
- **Priority 1: Critical** - Legal/regulatory violations, mandatory requirements
- **Priority 2: Important** - Best practice gaps with significant risk
- **Priority 3: Best Practice** - Minor enhancements and improvements

Each recommendation includes:
- Issue description
- Specific action needed
- Source reference
- Impact explanation

See [references/report_formats.md](references/report_formats.md) for recommendations template.

## Review Depth Options

### Quick Review
**Time:** ~5-10 minutes
**Best for:** Initial assessments, executive briefings, prioritization

**Process:**
- Extracts document keywords
- Selects 1-2 most relevant notebooks
- Queries for high-level requirements summary
- Identifies top 3-5 critical findings
- Generates quick summary report

**Output:** High-level summary with key findings and top actions

### Detailed Review
**Time:** ~30-60 minutes
**Best for:** Formal compliance reviews, document updates, audit preparation

**Process:**
- Analyzes full document structure
- Selects all relevant notebooks (1-3 typically)
- Queries each notebook for comprehensive requirements by category
- Performs section-by-section comparison
- Categorizes findings by severity
- Generates full report with all sections

**Output:** Comprehensive gap analysis, alignment summary, and detailed recommendations

## Notebook Selection

The skill intelligently selects relevant notebooks using keyword matching:

1. **Extract Keywords** - Identifies key terms from document (excludes stopwords)
2. **Score Notebooks** - Calculates relevance score based on:
   - Notebook name matches (5 points each)
   - Description matches (3 points each)
   - Topic matches (2 points each)
3. **Rank by Relevance** - Sorts notebooks by score
4. **Apply Threshold** - Includes notebooks above threshold (default: 5)

**Adjusting Threshold:**
- Too few notebooks? Lower threshold (e.g., `--threshold 3`)
- Too many notebooks? Raise threshold (e.g., `--threshold 10`)

## Document Type Patterns

This skill handles various document types with specialized analysis approaches. See [references/analysis_guide.md](references/analysis_guide.md) for detailed patterns.

**Common Document Types:**
- **Compliance Policies** - Regulatory coverage, controls, roles, monitoring
- **Operational Procedures** - Step completeness, technical accuracy, exceptions
- **Business Proposals** - Regulatory compliance, risk assessment, feasibility
- **Contracts** - Legal requirements, standard terms, risk allocation
- **Technical Documentation** - Standards compliance, security, operations

## Example Usage

### Example 1: Compliance Policy Review
```bash
# User: "Review my AML policy against Bermuda regulations"
python scripts/review_document.py "/path/to/AML_Policy.docx"

# Output:
# - Extracts policy content (777 paragraphs)
# - Selects "Bermuda AML/ATF Regulations" notebook (score: 45)
# - Queries for comprehensive AML/ATF requirements
# - Generates report identifying:
#   * Missing $1,000 transaction threshold
#   * Inadequate blockchain analysis procedures
#   * Complete coverage of reporting requirements
#   * Recommendations prioritized by severity
```

### Example 2: Quick Contract Review
```bash
# User: "Quick check if this vendor agreement covers data privacy requirements"
python scripts/review_document.py "/path/to/Vendor_Agreement.pdf" --output gap --depth quick

# Output:
# - Extracts contract text
# - Selects "Data Privacy Regulations" notebook
# - Queries for high-level privacy requirements
# - Generates quick report with top 3-5 data privacy gaps
```

### Example 3: Multi-Notebook Analysis
```bash
# User: "Check if this proposal meets both technical standards and compliance requirements"
python scripts/review_document.py "/path/to/Proposal.docx" --threshold 3

# Output:
# - Extracts proposal content
# - Selects multiple notebooks:
#   * "Technical Standards" (score: 12)
#   * "Regulatory Compliance" (score: 8)
#   * "Industry Best Practices" (score: 6)
# - Queries each notebook for requirements
# - Generates comprehensive report covering all sources
```

## Integration with NotebookLM

**This skill is a wrapper around the NotebookLM skill** - it does not work standalone.

**Setup NotebookLM First:**
1. Install the NotebookLM skill (separate download)
2. Authenticate: `cd ~/.claude/skills/notebooklm && python3 scripts/run.py auth_manager.py setup`
3. Add notebooks: `python3 scripts/run.py notebook_manager.py add --url <url> --name <name> --description <desc> --topics <topics>`

**How It Works:**
- This skill calls NotebookLM scripts at `~/.claude/skills/notebooklm/scripts/`
- Reads notebook library at `~/.claude/skills/notebooklm/data/library.json`
- Uses NotebookLM's browser automation to query your notebooks

**Notebook Library Location:**
```
~/.claude/skills/notebooklm/data/library.json
```

**To manage notebooks:**
```bash
cd ~/.claude/skills/notebooklm

# List notebooks
python3 scripts/run.py notebook_manager.py list

# Add notebook
python3 scripts/run.py notebook_manager.py add --url <url> --name <name> --description <desc> --topics <topics>

# Search notebooks
python3 scripts/run.py notebook_manager.py search --query <keyword>
```

## Troubleshooting

### No Notebooks Found
**Problem:** "No relevant notebooks found"
**Solution:**
- Lower threshold: `--threshold 3`
- Check NotebookLM library has notebooks: `cd ~/.claude/skills/notebooklm && python3 scripts/run.py notebook_manager.py list`
- Add relevant notebooks to library if missing

### Extraction Failed
**Problem:** "Failed to extract document"
**Solution:**
- Verify file path is correct
- Check file format is supported (.docx, .pdf, .txt, .md)
- For PDF: Install PyPDF2 (`pip install PyPDF2`)
- Try converting file to different format

### Query Timeout
**Problem:** NotebookLM query times out
**Solution:**
- Check NotebookLM authentication: `cd ~/.claude/skills/notebooklm && python3 scripts/run.py auth_manager.py status`
- Re-authenticate if needed: `python3 scripts/run.py auth_manager.py reauth`
- Simplify question or reduce depth to `quick`

### Script Not Found
**Problem:** Cannot find review script
**Solution:**
- Ensure you're in skill directory or use full path
- Check script exists: `ls scripts/review_document.py`
- Make script executable: `chmod +x scripts/review_document.py`

## Best Practices

1. **Start with Quick Review** - Get high-level assessment before detailed analysis
2. **Use Default Options** - `--output all --depth detailed` provides comprehensive coverage
3. **Lower Threshold for Broad Topics** - Generic documents may need `--threshold 3`
4. **Follow Up on Unclear Requirements** - Query notebooks directly for clarification
5. **Iterate** - Review → Update document → Review again to verify improvements
6. **Keep Notebooks Updated** - Add new reference sources to NotebookLM library as needed

## Command Reference

```bash
# Basic usage
python scripts/review_document.py <document_path>

# All options
python scripts/review_document.py <document_path> \
  --output gap,alignment,recommendations,all \
  --depth quick|detailed \
  --threshold N

# Examples
python scripts/review_document.py policy.docx
python scripts/review_document.py contract.pdf --output gap --depth quick
python scripts/review_document.py proposal.docx --threshold 3 --depth detailed
python scripts/review_document.py procedure.txt --output alignment,recommendations
```

## Resources

### Scripts
- `review_document.py` - Main orchestrator for document review workflow
- `extract_content.py` - Extract text from .docx, .pdf, .txt, .md files
- `notebook_selector.py` - Intelligent notebook selection based on content

### References
- `report_formats.md` - Templates for gap analysis, alignment, and recommendations
- `analysis_guide.md` - Patterns for analyzing different document types, depth levels, severity classification
