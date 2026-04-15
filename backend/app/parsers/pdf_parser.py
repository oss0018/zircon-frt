from app.parsers.base import BaseParser


class PdfParser(BaseParser):
    """Extract text from PDF files using PyMuPDF (fitz) with pdfminer fallback."""

    def parse(self, filepath: str) -> str:
        try:
            import fitz  # PyMuPDF
            text_parts = []
            with fitz.open(filepath) as doc:
                for page in doc:
                    text_parts.append(page.get_text())
            return "\n".join(text_parts)
        except ImportError:
            pass
        except Exception:
            pass

        # Fallback to pdfminer
        try:
            from pdfminer.high_level import extract_text
            return extract_text(filepath) or ""
        except Exception:
            return ""
