"""Parse uploaded legal documents (PDF/DOCX/TXT/images) into clauses.
Falls back to Tesseract OCR when a PDF has no embedded text (scanned docs)."""
from __future__ import annotations
import io
import logging
import re
import uuid

log = logging.getLogger("lexgraph")

OCR_MIN_CHARS = 100  # if pypdf returns less than this, treat the PDF as scanned
OCR_MAX_PAGES = 15   # cap to protect Railway's 512MB ceiling


def extract_text(filename: str, content: bytes) -> str:
    """Extract raw text from a file based on its extension.
    PDFs get embedded-text extraction first, OCR fallback if empty.
    Images go straight to OCR."""
    name = filename.lower()
    if name.endswith(".pdf"):
        text = _extract_pdf(content)
        if len(text.strip()) >= OCR_MIN_CHARS:
            return text
        log.info("PDF embedded text too short (%d chars) — running OCR fallback", len(text))
        return _ocr_pdf(content)
    if name.endswith(".docx"):
        return _extract_docx(content)
    if name.endswith((".txt", ".md")):
        return content.decode("utf-8", errors="ignore")
    if name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp")):
        return _ocr_image(content)
    raise ValueError(
        f"Unsupported file type: {filename}. Use PDF, DOCX, TXT, or an image (PNG/JPG/TIFF)."
    )


def _extract_pdf(content: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def _extract_docx(content: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _ocr_pdf(content: bytes) -> str:
    """Rasterize PDF pages and OCR each. Requires poppler-utils + tesseract installed."""
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
    except ImportError as e:
        raise RuntimeError(
            "OCR dependencies missing. Install poppler-utils and tesseract-ocr."
        ) from e

    images = convert_from_bytes(content, dpi=200, fmt="png", first_page=1, last_page=OCR_MAX_PAGES)
    parts: list[str] = []
    for i, img in enumerate(images, 1):
        try:
            parts.append(pytesseract.image_to_string(img, lang="eng"))
        except Exception as e:
            log.warning("OCR failed on page %d: %s", i, e)
            continue
    return "\n".join(parts)


def _ocr_image(content: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise RuntimeError("OCR dependencies missing. Install tesseract-ocr.") from e
    img = Image.open(io.BytesIO(content))
    return pytesseract.image_to_string(img, lang="eng")


# Matches: "1.", "1.1", "§1", "Article 12", "Section 3", "Clause 4", "Art. 5"
_SECTION_RE = re.compile(
    r"(?:^|\n)\s*("
    r"§\s*\d+(?:\.\d+)*"
    r"|Article\s+\d+(?:\.\d+)*"
    r"|Section\s+\d+(?:\.\d+)*"
    r"|Clause\s+\d+(?:\.\d+)*"
    r"|Art\.?\s*\d+(?:\.\d+)*"
    r"|\d+\.\d+(?:\.\d+)*"
    r"|\d{1,2}\."
    r")\s*",
    re.IGNORECASE,
)


def segment_clauses(text: str, contract_id: str) -> list[dict]:
    """Split text into clauses on section markers. Falls back to paragraph splitting."""
    text = text.strip()
    if not text:
        return []

    matches = list(_SECTION_RE.finditer(text))
    clauses: list[dict] = []

    if len(matches) >= 2:
        for i, m in enumerate(matches):
            heading = m.group(1).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if not body or len(body) < 40:
                continue
            title_line = body.split("\n", 1)[0][:120]
            clauses.append({
                "clause_id": f"{contract_id}__cl_{len(clauses) + 1}",
                "section": f"{heading} {title_line}".strip(),
                "text": body,
            })

    if not clauses:
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) >= 80]
        for i, p in enumerate(paras[:30], 1):
            clauses.append({
                "clause_id": f"{contract_id}__cl_{i}",
                "section": f"¶{i} {p.split(chr(10), 1)[0][:80]}",
                "text": p,
            })

    return clauses[:40]


def make_contract_id(title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:40] or "uploaded"
    return f"{base}__{uuid.uuid4().hex[:6]}"
