"""
AI Module: Resume Parsing (PDF / DOCX)
"""
import io
import re

def parse_resume_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
    except Exception as e:
        return f"[PDF parse error: {e}]"


def parse_resume_docx(file_bytes: bytes) -> str:
    """Extract raw text from DOCX bytes."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[DOCX parse error: {e}]"


def extract_contact_info(text: str) -> dict:
    """Extract email, phone from raw resume text."""
    email_pattern = r"[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}"
    phone_pattern = r"(\+?\d[\d\s\-\(\)]{8,15}\d)"
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    phones = re.findall(phone_pattern, text)
    return {
        "email": emails[0] if emails else None,
        "phone": phones[0].strip() if phones else None,
    }
