#!/usr/bin/env python3
"""
Compliance Checker - Verify document compliance against NotebookLM requirements.
Simple approach: Check if each requirement is mentioned/addressed in the document.
"""

import re
import sys


def parse_requirements(notebook_response):
    """
    Parse requirements from NotebookLM response.
    Looks for numbered lists, bullet points, and requirement patterns.
    Returns list of requirement dictionaries.
    """
    requirements = []

    # Split into lines
    lines = notebook_response.split('\n')

    current_category = None
    current_requirement = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect category headers (e.g., "1. Governance and Internal Controls")
        category_match = re.match(r'^(\d+)\.\s+(.+)', line)
        if category_match and len(line) < 100:  # Categories are typically short
            current_category = category_match.group(2).strip()
            continue

        # Detect requirement bullets (• or ◦)
        bullet_match = re.match(r'^[•◦]\s+(.+)', line)
        if bullet_match:
            req_text = bullet_match.group(1).strip()
            if len(req_text) > 20:  # Filter out very short items
                requirements.append({
                    'category': current_category or 'General',
                    'requirement': req_text,
                    'found': False,
                    'evidence': []
                })
            continue

    return requirements


def extract_keywords(requirement_text):
    """Extract key terms from a requirement for searching."""
    # Remove common requirement words
    noise_words = {
        'you', 'must', 'should', 'shall', 'need', 'required', 'requires',
        'ensure', 'establish', 'maintain', 'implement', 'apply', 'the', 'and',
        'for', 'with', 'that', 'this', 'from', 'have', 'has', 'been'
    }

    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', requirement_text.lower())

    # Filter noise and get unique keywords
    keywords = [w for w in words if w not in noise_words]

    # Return top keywords (prioritize longer, more specific terms)
    keywords.sort(key=len, reverse=True)
    return keywords[:10]


def check_requirement(requirement, document_content):
    """
    Check if a requirement is addressed in the document.
    Returns True if found, along with evidence snippets.
    """
    req_text = requirement['requirement'].lower()
    doc_lower = document_content.lower()

    # Extract keywords from requirement
    keywords = extract_keywords(req_text)

    if not keywords:
        return False, []

    # Check if multiple keywords appear in document
    matches = 0
    evidence = []

    for keyword in keywords[:5]:  # Check top 5 keywords
        if keyword in doc_lower:
            matches += 1

            # Find context around keyword
            pattern = r'.{0,100}\b' + re.escape(keyword) + r'\b.{0,100}'
            context_matches = re.finditer(pattern, doc_lower, re.IGNORECASE)

            for match in list(context_matches)[:1]:  # Take first occurrence
                snippet = match.group(0).strip()
                if snippet not in evidence:
                    evidence.append(snippet[:150])  # Limit snippet length

    # Consider "found" if at least 40% of top keywords are present
    threshold = max(2, len(keywords[:5]) * 0.4)
    found = matches >= threshold

    return found, evidence


def analyze_compliance(requirements, document_content):
    """
    Analyze document compliance against all requirements.
    Returns categorized results.
    """
    results = {
        'total': len(requirements),
        'found': 0,
        'missing': 0,
        'by_category': {}
    }

    for req in requirements:
        found, evidence = check_requirement(req, document_content)
        req['found'] = found
        req['evidence'] = evidence

        if found:
            results['found'] += 1
        else:
            results['missing'] += 1

        # Group by category
        category = req['category']
        if category not in results['by_category']:
            results['by_category'][category] = {
                'total': 0,
                'found': 0,
                'missing': 0,
                'requirements': []
            }

        results['by_category'][category]['total'] += 1
        if found:
            results['by_category'][category]['found'] += 1
        else:
            results['by_category'][category]['missing'] += 1
            results['by_category'][category]['requirements'].append(req)

    return results


def generate_gap_report(results):
    """Generate gap analysis report text."""
    report = []

    report.append("## Gap Analysis\n")
    report.append(f"**Total Requirements Checked:** {results['total']}")
    report.append(f"**Requirements Covered:** {results['found']}")
    report.append(f"**Requirements Missing:** {results['missing']}\n")

    if results['missing'] == 0:
        report.append("✅ **Excellent!** Your document appears to cover all identified requirements.\n")
        return '\n'.join(report)

    report.append("### Missing or Inadequate Requirements\n")

    for category, cat_data in results['by_category'].items():
        if cat_data['missing'] > 0:
            report.append(f"\n#### {category}")
            report.append(f"*Missing {cat_data['missing']} of {cat_data['total']} requirements*\n")

            for req in cat_data['requirements']:
                # Extract key part of requirement (first sentence or clause)
                req_text = req['requirement']
                if ':' in req_text:
                    req_text = req_text.split(':')[0]
                elif '.' in req_text and len(req_text) > 100:
                    req_text = req_text.split('.')[0] + '...'

                report.append(f"- **{req_text}**")

    report.append("\n")
    return '\n'.join(report)


def generate_recommendations(results):
    """Generate specific recommendations for missing requirements."""
    report = []

    report.append("## Recommendations\n")

    if results['missing'] == 0:
        report.append("Your document appears to cover all identified requirements. Consider:\n")
        report.append("1. Reviewing the requirements in detail to ensure adequate depth of coverage")
        report.append("2. Keeping the document updated as regulations evolve")
        report.append("3. Regular compliance audits\n")
        return '\n'.join(report)

    report.append("### Priority Actions\n")

    priority_num = 1

    for category, cat_data in results['by_category'].items():
        if cat_data['missing'] > 0:
            report.append(f"\n#### {category}\n")

            for req in cat_data['requirements'][:5]:  # Top 5 per category
                req_text = req['requirement']

                # Shorten if too long
                if len(req_text) > 200:
                    req_text = req_text[:197] + "..."

                report.append(f"{priority_num}. **Add requirement:** {req_text}")
                priority_num += 1

    report.append("\n")
    return '\n'.join(report)


def main():
    """
    Main function for testing compliance checker.
    Usage: python compliance_checker.py <document_file> <requirements_file>
    """
    if len(sys.argv) < 3:
        print("Usage: python compliance_checker.py <document_file> <requirements_file>")
        sys.exit(1)

    document_file = sys.argv[1]
    requirements_file = sys.argv[2]

    # Read files
    with open(document_file, 'r', encoding='utf-8') as f:
        document_content = f.read()

    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements_text = f.read()

    # Parse and analyze
    requirements = parse_requirements(requirements_text)
    print(f"Parsed {len(requirements)} requirements")

    results = analyze_compliance(requirements, document_content)

    # Generate reports
    gap_report = generate_gap_report(results)
    recommendations = generate_recommendations(results)

    print(gap_report)
    print(recommendations)


if __name__ == '__main__':
    main()
