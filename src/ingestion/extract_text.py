"""PDF text extraction with deduplication and cleaning."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import pymupdf

from src.utils import setup_logger, EXTRACTED_DATA_DIR


logger = setup_logger(__name__)


def normalize_text(text: str) -> str:
    """Normalize text: lowercase and collapse whitespace."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_key(text: str, n: int = 80) -> str:
    """Create a deduplication key from text."""
    text = normalize_text(text)
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text[:n]


def should_skip_paragraph(paragraph: str, seen_paragraphs: List[str]) -> bool:
    """Skip paragraph if it's a substring of existing or vice versa."""
    p_norm = normalize_text(paragraph)

    for i, prev in enumerate(seen_paragraphs):
        prev_norm = normalize_text(prev)

        if p_norm in prev_norm:
            return True

        if prev_norm in p_norm:
            seen_paragraphs[i] = paragraph
            return True

    return False


def clean_page(page) -> str:
    """Extract and clean text from a single PDF page."""
    blocks = page.get_text("blocks")

    cleaned_blocks = []
    seen_paragraph_keys = set()
    global_seen_paragraphs = []

    for b in blocks:
        x0, y0, x1, y1, text = b[:5]
        text = (text or "").strip()
        if not text:
            continue

        lowered = text.lower()

        # Skip page numbers
        if "page |" in lowered and len(text) < 40:
            continue

        # Skip captions and metadata
        if lowered.startswith(("figure ", "map ", "license:", "source:", "author:")):
            continue

        raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        block_paragraphs = []

        for para in raw_paragraphs:
            key = get_key(para)
            if not key:
                continue

            if key in seen_paragraph_keys:
                continue

            if should_skip_paragraph(para, global_seen_paragraphs):
                continue

            seen_paragraph_keys.add(key)
            global_seen_paragraphs.append(para)
            block_paragraphs.append(para)

        if block_paragraphs:
            cleaned_blocks.append(" ".join(block_paragraphs))

    full_page = " ".join(cleaned_blocks)
    full_page = re.sub(r"\s+", " ", full_page).strip()

    return full_page


def extract_pdf_text(
    pdf_path: str,
    output_path: Optional[str] = None
) -> Dict[str, Dict]:
    
    """Extract text from all pages of a PDF file."""
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Opening PDF: {pdf_path.name}")
    doc = pymupdf.open(str(pdf_path))
    output = {}

    total_pages = len(doc)
    logger.info(f"Processing {total_pages} pages...")

    for i in range(total_pages):
        page = doc[i]
        cleaned = clean_page(page)

        output[f"page_{i+1}"] = {
            "page": i + 1,
            "text": cleaned,
            "char_count": len(cleaned),
            "word_count": len(cleaned.split())
        }

        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{total_pages} pages")

    doc.close()

    total_words = sum(p['word_count'] for p in output.values())
    logger.info(f"Extraction complete: {total_pages} pages, {total_words:,} words")

    # Save to JSON
    if not output_path:
        output_path = EXTRACTED_DATA_DIR / f"{pdf_path.stem}_extracted.json"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved to: {output_path}")

    return output


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("-o", "--output", help="Output JSON path")
    
    args = parser.parse_args()
    extract_pdf_text(args.pdf_path, args.output)
