"""Clean extracted text and add chapter metadata."""

import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.utils import setup_logger, EXTRACTED_DATA_DIR

logger = setup_logger(__name__)

# Regex to match chapter headers
CHAPTER_REGEX = re.compile(
    r"CHAPTER\s+(\d+)\s*:\s*([A-Z][A-Z \-]+)"
)


def normalize_chapter_title(title: str) -> str:
    """Normalize chapter title by removing OCR artifacts."""
    if not title:
        return "UNTITLED"

    t = title.strip().upper()

    # Keep only letters, spaces, and digits
    t = "".join(c for c in t if c.isalnum() or c.isspace())

    # Remove trailing single letters or numbers (OCR garbage)
    parts = t.split()
    while parts and len(parts[-1]) <= 1:
        parts.pop()

    t = " ".join(parts)

    return t if t else "UNTITLED"


def extract_chapter_details(text: str) -> Tuple[Optional[int], Optional[str]]:
    """Extract chapter number and title from text."""
    head = text[:250]
    m = CHAPTER_REGEX.search(head)

    if not m:
        return None, None
    
    chapter_number = int(m.group(1))
    chapter_title = normalize_chapter_title(m.group(2))

    return chapter_number, chapter_title


def filter_pages(data: Dict, start_page: int = 10, end_page: int = 486) -> Dict:
    """Filter pages to remove boilerplate (TOC, index, etc)."""
    filtered = {}

    for key, value in data.items():
        page_no = value['page']

        if start_page <= page_no <= end_page:
            filtered[key] = value
    
    logger.info(f"Filtered pages: {len(data)} → {len(filtered)}")
    return filtered


def add_chapter_metadata(pages: Dict) -> Dict:
    """Add chapter metadata to each page."""
    pages_with_metadata = {}

    for key, value in pages.items():
        text = value.get('text', '')
        chapter_number, chapter_title = extract_chapter_details(text)

        pages_with_metadata[key] = {
            "page": value['page'],
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split()),
            "chapter_number": chapter_number,
            "chapter_title": chapter_title
        }
    
    logger.info(f"Added chapter metadata to {len(pages_with_metadata)} pages")
    return pages_with_metadata


def backfill_chapter_details(pages: Dict) -> Dict:
    """Backfill missing chapter metadata and clean up."""
    last_chapter_number = None
    last_chapter_title = None

    for key, value in pages.items():
        chapter_num = value.get("chapter_number")
        chapter_title = value.get("chapter_title")
        page_number = value.get("page")

        # Update memory when a chapter header appears
        if chapter_num is not None:
            last_chapter_number = chapter_num
            last_chapter_title = chapter_title
        else:
            # Backfill missing chapter metadata
            value["chapter_number"] = last_chapter_number
            value["chapter_title"] = last_chapter_title

        # Add combined chapter details (after backfill)
        value["chapter_details"] = (
            f"CHAPTER: {value['chapter_number']} - {value['chapter_title']} | pg-{page_number}"
        )

        # Remove unwanted keys (keep text and chapter_details)
        for unwanted in ["page", "char_count", "word_count", "chapter_number", "chapter_title"]:
            value.pop(unwanted, None)

    logger.info("Backfilled chapter details")
    return pages


def clean_extracted_text(
    input_path: str,
    output_path: str,
    start_page: int = 10,
    end_page: int = 486
) -> Dict:
    """
    Clean extracted text data.
    
    Steps:
    1. Load extracted JSON
    2. Filter pages (remove TOC, index, etc)
    3. Extract chapter metadata
    4. Backfill missing chapter info
    5. Save cleaned data
    
    Args:
        input_path: Path to extracted JSON file
        output_path: Path to save cleaned JSON
        start_page: First page to keep (default 10)
        end_page: Last page to keep (default 486)
        
    Returns:
        Dictionary with cleaned page data
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info(f"Loading extracted text from: {input_path}")
    
    with open(input_path, "r", encoding="utf8") as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data)} pages")

    # Process data
    filtered = filter_pages(data, start_page, end_page)
    with_metadata = add_chapter_metadata(filtered)
    backfilled = backfill_chapter_details(with_metadata)

    # Save output
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(backfilled, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved cleaned data to: {output_path}")
    
    # Print sample
    sample = list(backfilled.values())[0]
    logger.info(f"Sample: {sample['chapter_details']}")
    logger.info(f"Text snippet: {sample['text'][:100]!r}")

    return backfilled


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean extracted text")
    parser.add_argument("input_path", help="Path to extracted JSON file")
    parser.add_argument("-o", "--output", help="Output JSON path")
    parser.add_argument("--start-page", type=int, default=10, help="First page to keep")
    parser.add_argument("--end-page", type=int, default=486, help="Last page to keep")
    
    args = parser.parse_args()
    
    output = args.output or str(EXTRACTED_DATA_DIR / "cleaned_book.json")
    
    clean_extracted_text(
        args.input_path,
        output,
        args.start_page,
        args.end_page
    )
