"""Script to extract text from PDF files."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.extract_text import extract_pdf_text
from src.utils.config import RAW_DATA_DIR, EXTRACTED_DATA_DIR

def main():
    """Extract text from all PDFs in raw data directory."""
    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {RAW_DATA_DIR}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s)")
    print("="*60)
    
    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        output_path = EXTRACTED_DATA_DIR / f"{pdf_path.stem}_extracted.json"
        
        try:
            result = extract_pdf_text(str(pdf_path), str(output_path))
            print(f"✓ Successfully extracted {len(result)} pages")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Extraction complete!")


if __name__ == "__main__":
    main()