#!/usr/bin/env python3
"""
Extract text content from various document formats.
Supports: .docx, .pdf, .txt, .md
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_docx(file_path):
    """Extract text from .docx file"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            with zip_ref.open('word/document.xml') as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                paragraphs = root.findall('.//w:p', namespace)

                text_content = []
                for para in paragraphs:
                    para_text = []
                    for text_node in para.findall('.//w:t', namespace):
                        if text_node.text:
                            para_text.append(text_node.text)
                    if para_text:
                        text_content.append(''.join(para_text))

                return '\n'.join(text_content)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def extract_pdf(file_path):
    """Extract text from .pdf file"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text_content = []
            for page in reader.pages:
                text_content.append(page.extract_text())
            return '\n'.join(text_content)
    except ImportError:
        return "Error: PyPDF2 not installed. Install with: pip install PyPDF2"
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def extract_text(file_path):
    """Extract text from .txt or .md file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_content.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    path = Path(file_path)

    if not path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    suffix = path.suffix.lower()

    if suffix == '.docx':
        content = extract_docx(file_path)
    elif suffix == '.pdf':
        content = extract_pdf(file_path)
    elif suffix in ['.txt', '.md']:
        content = extract_text(file_path)
    else:
        print(f"Error: Unsupported file format: {suffix}")
        print("Supported formats: .docx, .pdf, .txt, .md")
        sys.exit(1)

    print(content)


if __name__ == '__main__':
    main()
