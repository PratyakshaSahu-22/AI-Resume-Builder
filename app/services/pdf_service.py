"""
PDF Generation service – creates downloadable resume PDFs.
Uses WeasyPrint (preferred) or xhtml2pdf as fallback.
"""
from __future__ import annotations
import io


def generate_pdf_from_html(html_content: str) -> bytes:
    """
    Convert rendered HTML to PDF bytes.
    Tries WeasyPrint first, falls back to xhtml2pdf.
    """
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except ImportError:
        pass

    try:
        from xhtml2pdf import pisa
        result_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=result_buffer)
        if not pisa_status.err:
            return result_buffer.getvalue()
    except ImportError:
        pass

    raise RuntimeError(
        "No PDF library available. Install weasyprint or xhtml2pdf."
    )
