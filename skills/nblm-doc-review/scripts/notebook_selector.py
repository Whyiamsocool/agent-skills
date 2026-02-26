#!/usr/bin/env python3
"""
Intelligently select relevant NotebookLM notebooks based on document content.
"""

import sys
import json
import re
import os
from pathlib import Path
from collections import Counter


def extract_keywords(text, top_n=20):
    """Extract key terms from document text"""
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Common stopwords to exclude
    stopwords = {
        'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'has',
        'will', 'would', 'could', 'should', 'may', 'must', 'can', 'are',
        'was', 'were', 'been', 'being', 'not', 'but', 'all', 'any', 'such',
        'shall', 'including', 'which', 'where', 'when', 'who', 'what'
    }

    # Filter stopwords and count
    filtered_words = [w for w in words if w not in stopwords]
    word_counts = Counter(filtered_words)

    return [word for word, _ in word_counts.most_common(top_n)]


def score_notebook(notebook, keywords):
    """Score a notebook's relevance based on keywords"""
    score = 0

    # Check notebook name
    name_lower = notebook.get('name', '').lower()
    for keyword in keywords:
        if keyword in name_lower:
            score += 5

    # Check notebook description
    desc_lower = notebook.get('description', '').lower()
    for keyword in keywords:
        if keyword in desc_lower:
            score += 3

    # Check notebook topics
    topics = notebook.get('topics', [])
    for topic in topics:
        topic_lower = topic.lower()
        for keyword in keywords:
            if keyword in topic_lower or topic_lower in keyword:
                score += 2

    return score


def select_notebooks(library_path, document_keywords, threshold=5):
    """Select relevant notebooks from library based on document keywords"""
    try:
        with open(library_path, 'r') as f:
            library = json.load(f)

        notebooks_dict = library.get('notebooks', {})

        # Handle both dict and list formats
        if isinstance(notebooks_dict, dict):
            notebooks = list(notebooks_dict.values())
        else:
            notebooks = notebooks_dict

        if not notebooks:
            return []

        # Score each notebook
        scored_notebooks = []
        for notebook in notebooks:
            score = score_notebook(notebook, document_keywords)
            if score >= threshold:
                scored_notebooks.append({
                    'notebook': notebook,
                    'score': score
                })

        # Sort by score descending
        scored_notebooks.sort(key=lambda x: x['score'], reverse=True)

        return scored_notebooks

    except Exception as e:
        print(f"Error selecting notebooks: {str(e)}", file=sys.stderr)
        return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python notebook_selector.py <document_content> [--threshold N]")
        sys.exit(1)

    document_text = sys.argv[1]
    threshold = 5

    # Parse optional threshold
    if '--threshold' in sys.argv:
        idx = sys.argv.index('--threshold')
        if idx + 1 < len(sys.argv):
            threshold = int(sys.argv[idx + 1])

    # Extract keywords from document
    keywords = extract_keywords(document_text)

    # Get library path
    library_path = resolve_notebooklm_library_path()

    if not library_path.exists():
        print(json.dumps({'error': 'NotebookLM library not found'}))
        sys.exit(1)

    # Select relevant notebooks
    selected = select_notebooks(library_path, keywords, threshold)

    # Output results as JSON
    result = {
        'keywords': keywords[:10],  # Top 10 keywords
        'notebooks': [
            {
                'id': nb['notebook']['id'],
                'name': nb['notebook']['name'],
                'url': nb['notebook']['url'],
                'score': nb['score'],
                'topics': nb['notebook'].get('topics', [])
            }
            for nb in selected
        ]
    }

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
def resolve_notebooklm_library_path():
    """Resolve notebook library path across agent runtimes."""
    env_dir = Path(os.environ.get('NOTEBOOKLM_SKILL_DIR', '')).expanduser() if os.environ.get('NOTEBOOKLM_SKILL_DIR') else None
    candidates = []

    if env_dir:
        candidates.append(env_dir / 'data' / 'library.json')

    # Prefer Codex layout.
    candidates.append(Path.home() / '.codex' / 'skills' / 'notebooklm' / 'data' / 'library.json')

    for path in candidates:
        if path.exists():
            return path

    return candidates[0]
