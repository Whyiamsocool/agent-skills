#!/usr/bin/env python3
"""
Main document alignment reviewer orchestrator.
Reviews documents against NotebookLM notebooks and generates comprehensive reports.
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Import compliance checker functions
from compliance_checker import (
    parse_requirements,
    analyze_compliance,
    generate_gap_report,
    generate_recommendations
)


def run_command(cmd, input_text=None):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            input=input_text
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return '', str(e), 1


def extract_document(file_path):
    """Extract text content from document"""
    script_dir = Path(__file__).parent
    extract_script = script_dir / 'extract_content.py'

    stdout, stderr, code = run_command(f'python3 "{extract_script}" "{file_path}"')

    if code != 0:
        return None, f"Failed to extract document: {stderr}"

    return stdout, None


def select_relevant_notebooks(document_content, threshold=5):
    """Select relevant notebooks based on document content"""
    script_dir = Path(__file__).parent
    selector_script = script_dir / 'notebook_selector.py'

    # Pass document content as argument (escaped for shell)
    stdout, stderr, code = run_command(
        f'python3 "{selector_script}" "$DOC_CONTENT" --threshold {threshold}',
        input_text=None
    )

    # Alternative: write to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(document_content)
        temp_path = f.name

    try:
        with open(temp_path, 'r') as f:
            doc_text = f.read()

        cmd = f'python3 "{selector_script}" "{doc_text}" --threshold {threshold}'
        stdout, stderr, code = run_command(cmd)

        if code != 0:
            return None, f"Failed to select notebooks: {stderr}"

        result = json.loads(stdout)
        return result, None
    finally:
        Path(temp_path).unlink()


def query_notebook(notebook_id, question):
    """Query a specific NotebookLM notebook"""
    notebooklm_env = os.environ.get('NOTEBOOKLM_SKILL_DIR')
    if notebooklm_env:
        notebooklm_path = Path(notebooklm_env).expanduser()
    else:
        notebooklm_path = Path.home() / '.codex' / 'skills' / 'notebooklm'
    ask_script = notebooklm_path / 'scripts' / 'run.py'

    cmd = f'cd "{notebooklm_path}" && python3 "{ask_script}" ask_question.py --question "{question}" --notebook-id "{notebook_id}"'

    stdout, stderr, code = run_command(cmd)

    if code != 0:
        return None, f"Failed to query notebook: {stderr}"

    # Extract answer from output (between "Question:" and "EXTREMELY IMPORTANT:")
    lines = stdout.split('\n')
    answer_start = False
    answer_lines = []

    for line in lines:
        if 'Question:' in line:
            answer_start = True
            continue
        if 'EXTREMELY IMPORTANT:' in line:
            break
        if answer_start and line.strip():
            answer_lines.append(line)

    return '\n'.join(answer_lines), None


def generate_report(document_path, document_content, notebooks, queries, output_options):
    """Generate comprehensive alignment report with real compliance analysis"""
    report = []

    # Header
    report.append("# Document Compliance Review Report")
    report.append(f"\n**Document:** {document_path}")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n---\n")

    # Executive Summary
    report.append("## Executive Summary")
    report.append(f"\nReviewed document against {len(notebooks)} relevant notebook(s):")
    for nb in notebooks:
        report.append(f"- {nb['name']} (relevance score: {nb['score']})")
    report.append("\n")

    # Notebooks Queried
    report.append("## Source Notebooks")
    for nb in notebooks:
        report.append(f"\n### {nb['name']}")
        report.append(f"- **Topics:** {', '.join(nb.get('topics', []))}")
        report.append(f"- **URL:** {nb['url']}")
        report.append(f"- **Relevance Score:** {nb['score']}")

    report.append("\n---\n")

    # Analyze compliance for each notebook
    all_requirements = []
    combined_results = None

    for query in queries:
        # Parse requirements from this notebook
        requirements = parse_requirements(query['answer'])
        all_requirements.extend(requirements)

        # Analyze compliance
        results = analyze_compliance(requirements, document_content)

        if combined_results is None:
            combined_results = results
        else:
            # Merge results
            combined_results['total'] += results['total']
            combined_results['found'] += results['found']
            combined_results['missing'] += results['missing']

            for category, cat_data in results['by_category'].items():
                if category not in combined_results['by_category']:
                    combined_results['by_category'][category] = cat_data
                else:
                    combined_results['by_category'][category]['total'] += cat_data['total']
                    combined_results['by_category'][category]['found'] += cat_data['found']
                    combined_results['by_category'][category]['missing'] += cat_data['missing']
                    combined_results['by_category'][category]['requirements'].extend(cat_data['requirements'])

    # Query Results (detailed requirements)
    report.append("## Detailed Requirements")
    for query in queries:
        report.append(f"\n### {query['notebook_name']}")
        report.append(f"\n**Query:** {query['question']}\n")
        report.append(f"**Response:**\n{query['answer']}\n")
        report.append("\n---\n")

    # Generate real gap analysis and recommendations
    if combined_results:
        if 'gap' in output_options or 'all' in output_options:
            gap_report = generate_gap_report(combined_results)
            report.append(gap_report)

        if 'recommendations' in output_options or 'all' in output_options:
            recommendations = generate_recommendations(combined_results)
            report.append(recommendations)

    return '\n'.join(report)


def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python review_document.py <document_path> [options]")
        print("\nOptions:")
        print("  --output gap,alignment,recommendations,all  (default: all)")
        print("  --depth quick|detailed  (default: detailed)")
        print("  --threshold N  (notebook relevance threshold, default: 5)")
        sys.exit(1)

    document_path = sys.argv[1]
    output_options = ['all']
    depth = 'detailed'
    threshold = 5

    # Parse options
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_options = sys.argv[idx + 1].split(',')

    if '--depth' in sys.argv:
        idx = sys.argv.index('--depth')
        if idx + 1 < len(sys.argv):
            depth = sys.argv[idx + 1]

    if '--threshold' in sys.argv:
        idx = sys.argv.index('--threshold')
        if idx + 1 < len(sys.argv):
            threshold = int(sys.argv[idx + 1])

    print(f"📄 Reviewing document: {document_path}")
    print(f"⚙️  Options: output={','.join(output_options)}, depth={depth}, threshold={threshold}\n")

    # Step 1: Extract document content
    print("1️⃣  Extracting document content...")
    content, error = extract_document(document_path)
    if error:
        print(f"❌ {error}")
        sys.exit(1)
    print(f"✅ Extracted {len(content)} characters\n")

    # Step 2: Select relevant notebooks
    print("2️⃣  Selecting relevant notebooks...")
    selection_result, error = select_relevant_notebooks(content, threshold)
    if error:
        print(f"❌ {error}")
        sys.exit(1)

    notebooks = selection_result.get('notebooks', [])
    keywords = selection_result.get('keywords', [])

    if not notebooks:
        print("❌ No relevant notebooks found. Try lowering the threshold.")
        sys.exit(1)

    print(f"✅ Found {len(notebooks)} relevant notebook(s)")
    print(f"   Keywords: {', '.join(keywords[:5])}\n")

    for nb in notebooks:
        print(f"   - {nb['name']} (score: {nb['score']})")
    print()

    # Step 3: Query notebooks for requirements
    print("3️⃣  Querying notebooks for requirements...\n")
    queries = []

    for nb in notebooks:
        print(f"   Querying: {nb['name']}...")

        # Craft question based on depth
        if depth == 'quick':
            question = "What are the key requirements covered in this documentation? Provide a high-level summary."
        else:
            question = "What are the comprehensive requirements covered in this documentation? Provide detailed information including all obligations, procedures, and standards."

        answer, error = query_notebook(nb['id'], question)
        if error:
            print(f"   ⚠️  Warning: {error}")
            continue

        queries.append({
            'notebook_name': nb['name'],
            'notebook_id': nb['id'],
            'question': question,
            'answer': answer
        })

        print(f"   ✅ Received response ({len(answer)} chars)\n")

    if not queries:
        print("❌ Failed to query any notebooks")
        sys.exit(1)

    # Step 4: Generate report
    print("4️⃣  Generating report...")
    report = generate_report(document_path, content, notebooks, queries, output_options)

    # Save report
    output_file = Path(document_path).stem + '_alignment_report.md'
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"✅ Report generated: {output_file}\n")
    print("="*60)
    print(report)


if __name__ == '__main__':
    main()
