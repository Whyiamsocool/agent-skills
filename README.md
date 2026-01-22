# NotebookLM Document Review

A Claude Code skill that reviews any document against your NotebookLM notebooks to identify gaps, assess alignment, and generate actionable recommendations.

## Overview

This skill automatically:
- Extracts content from documents (.docx, .pdf, .txt, .md)
- Intelligently selects relevant NotebookLM notebooks based on content
- Queries notebooks for comprehensive requirements
- Generates detailed reports with gap analysis, alignment summaries, and recommendations

## Prerequisites

**⚠️ IMPORTANT:** This skill requires the NotebookLM skill to be installed and configured first.

Before using this skill:
1. Install the [NotebookLM skill](https://github.com/anthropics/notebooklm-skill) (if available)
2. Authenticate with Google
3. Add at least one notebook to your NotebookLM library

## Installation

### Option 1: Install from .skill file

```bash
# Copy the .skill file to your Claude skills directory
cp nblm-doc-review.skill ~/.claude/skills/
```

### Option 2: Install from source

```bash
# Clone this repository
git clone https://github.com/Whyiamsocool/nblm-doc-review.git

# Copy to Claude skills directory
cp -r nblm-doc-review ~/.claude/skills/
```

## Usage

### Basic Review (All Options, Detailed)

```bash
cd ~/.claude/skills/nblm-doc-review
python scripts/review_document.py /path/to/document.docx
```

### Quick Review (High-Level Summary)

```bash
python scripts/review_document.py /path/to/document.docx --depth quick
```

### Custom Options

```bash
# Gap analysis only
python scripts/review_document.py /path/to/document.docx --output gap

# Gap + Recommendations, Quick depth
python scripts/review_document.py /path/to/document.docx --output gap,recommendations --depth quick

# Lower threshold for more notebooks
python scripts/review_document.py /path/to/document.docx --threshold 3
```

## Command Options

### Output Options
- `gap` - Gap analysis (missing requirements)
- `alignment` - Alignment summary (coverage assessment)
- `recommendations` - Actionable recommendations
- `all` - All of the above (default)

### Review Depth
- `quick` - High-level summary (~5-10 min)
- `detailed` - Comprehensive analysis (~30-60 min, default)

### Notebook Threshold
- `--threshold N` - Relevance score threshold (default: 5)
- Lower = more notebooks included
- Higher = only most relevant notebooks

## Example Use Cases

### Compliance Policy Review
```bash
python scripts/review_document.py "AML Policy.docx"
```
Reviews policy against regulatory requirements, identifies gaps, and provides recommendations.

### Contract Review
```bash
python scripts/review_document.py "Vendor Agreement.pdf" --output gap --depth quick
```
Quick check for missing legal or regulatory clauses.

### Multi-Source Analysis
```bash
python scripts/review_document.py "Proposal.docx" --threshold 3
```
Reviews against multiple notebooks for comprehensive coverage.

## How It Works

1. **Extract** - Gets text content from any supported document format
2. **Select** - Intelligently chooses relevant NotebookLM notebooks based on keywords
3. **Query** - Asks each notebook for comprehensive requirements
4. **Compare** - Analyzes document against retrieved requirements
5. **Report** - Generates structured markdown report with findings

## Report Contents

Generated reports include:
- **Executive Summary** - Overview and relevance scores
- **Source Notebooks** - Details on reference sources used
- **Requirements Analysis** - Comprehensive requirements from each notebook
- **Gap Analysis** - Missing or inadequate requirements (if selected)
- **Alignment Summary** - Coverage assessment by category (if selected)
- **Recommendations** - Prioritized actionable improvements (if selected)

## Supported Document Formats

- `.docx` - Microsoft Word documents
- `.pdf` - PDF files (requires PyPDF2: `pip install PyPDF2`)
- `.txt` - Plain text files
- `.md` - Markdown files

## Structure

```
nblm-doc-review/
├── SKILL.md                    # Skill instructions for Claude
├── scripts/
│   ├── review_document.py      # Main orchestrator
│   ├── extract_content.py      # Document content extraction
│   └── notebook_selector.py    # Intelligent notebook selection
└── references/
    ├── report_formats.md       # Report templates
    └── analysis_guide.md       # Document analysis patterns
```

## Troubleshooting

### No Notebooks Found
**Problem:** "No relevant notebooks found"

**Solution:**
- Lower threshold: `--threshold 3`
- Verify NotebookLM library has notebooks
- Add relevant notebooks to your library

### Extraction Failed
**Problem:** "Failed to extract document"

**Solution:**
- Verify file path is correct
- Check file format is supported
- For PDF: Install PyPDF2 (`pip install PyPDF2`)

### Query Timeout
**Problem:** NotebookLM query times out

**Solution:**
- Check NotebookLM authentication status
- Re-authenticate if needed
- Use `--depth quick` for faster queries

## Dependencies

- Python 3.7+
- NotebookLM skill (separate installation required)
- PyPDF2 (optional, for PDF support)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Author

Created as a wrapper skill for NotebookLM integration with Claude Code.

## Related Skills

- [NotebookLM](https://github.com/anthropics/notebooklm-skill) - Required dependency
