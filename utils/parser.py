import os
import pdfplumber
import docx
from utils.exceptions import ParsingError, UnsupportedFileFormat

def parse_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            return parse_pdf(file_path)
        elif ext == ".docx":
            return parse_docx(file_path)
        elif ext == ".md":
            return parse_md(file_path)
        else:
            raise UnsupportedFileFormat(f"Unsupported file type: {ext}")
    except Exception as e:
        raise ParsingError(f"Failed to parse {file_path}: {e}")

def parse_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return {"raw_text": text, "sections": split_sections(text)}
    except Exception as e:
        raise ParsingError(f"PDF parsing error: {e}")

def parse_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return {"raw_text": text, "sections": split_sections(text)}
    except Exception as e:
        raise ParsingError(f"DOCX parsing error: {e}")

def parse_md(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return {"raw_text": text, "sections": split_sections(text)}
    except Exception as e:
        raise ParsingError(f"Markdown parsing error: {e}")

def split_sections(text):
    # Simple section splitter by headings (## or similar)
    import re
    sections = re.split(r'\n#+\s', text)
    return [s.strip() for s in sections if s.strip()]