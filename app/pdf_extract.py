# app/pdf_extract.py
import fitz  # PyMuPDF
from typing import List, Dict

def extract_pdf_pages_with_spans(file_path: str) -> List[Dict]:
    """
    Returns list of pages with:
    { "page": int, "text": str, "start_char": int, "end_char": int }
    Start/end are cumulative offsets across the whole document.
    """
    doc = fitz.open(file_path)
    pages = []
    offset = 0
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text("text")
        start = offset
        end = offset + len(text)
        pages.append({"page": i, "text": text, "start_char": start, "end_char": end})
        offset = end
    doc.close()
    return pages

def join_pages_to_full_text(pages):
    return "\n".join(p["text"] for p in pages)
