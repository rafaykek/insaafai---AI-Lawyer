import os
import re

def clean_text(text: str) -> str:
    """
    Cleans formatting artifacts while preserving exact legal wording.
    Handles excessive whitespace and blank lines.
    """
    if not text:
        return ""
    
    # Standardize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Strip trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Replace 3+ consecutive newlines with 2 newlines (preserve paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple horizontal spaces/tabs with single space within lines
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def extract_text_from_pdf(filepath: str) -> list[dict]:
    """
    Extract text from PDF using PyMuPDF, preserving page numbers.
    Returns: list of dicts [{'text': str, 'page': int}]
    """
    import pymupdf as fitz

    pages_data = []
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc[page_num]
            raw_text = page.get_text("text")
            cleaned = clean_text(raw_text)
            if cleaned:
                pages_data.append({
                    'text': cleaned,
                    'page': page_num + 1  # 1-indexed page number
                })
        doc.close()
    except Exception:
        # Fallback to plain text reading if PDF decoding fails (e.g. invalid PDF header)
        return extract_text_from_txt(filepath)

    return pages_data

def extract_text_from_docx(filepath: str) -> list[dict]:
    """
    Extract text from DOCX using python-docx.
    Returns: list of dicts [{'text': str, 'page': None}]
    """
    import docx

    doc = docx.Document(filepath)
    full_text = []

    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())

    # Include table text if any
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                full_text.append(" | ".join(row_text))

    combined_text = "\n".join(full_text)
    cleaned = clean_text(combined_text)

    if not cleaned:
        return []

    return [{'text': cleaned, 'page': None}]

def extract_text_from_txt(filepath: str) -> list[dict]:
    """
    Extract text from plain text file.
    Returns: list of dicts [{'text': str, 'page': None}]
    """
    raw_content = ""
    # Try reading with utf-8 first, fallback to latin-1
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            raw_content = f.read()

    cleaned = clean_text(raw_content)
    if not cleaned:
        return []

    return [{'text': cleaned, 'page': None}]

def extract_text(filepath: str) -> list[dict]:
    """
    Main parser entrypoint. Determines file type and invokes appropriate extractor.
    Returns list of page dicts: [{'text': '...', 'page': 1 or None}]
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Document file not found at path: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext == '.docx':
        return extract_text_from_docx(filepath)
    elif ext == '.txt':
        return extract_text_from_txt(filepath)
    elif ext in ['.png', '.jpg', '.jpeg']:
        # OCR not implemented yet
        return [{'text': 'OCR not implemented yet', 'page': None}]
    else:
        # Fallback to plain text reader
        try:
            return extract_text_from_txt(filepath)
        except Exception:
            return [{'text': 'Unsupported file format', 'page': None}]
