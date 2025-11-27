"""Script to clean extracted text data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.clean_text import clean_extracted_text
from src.utils import EXTRACTED_DATA_DIR


def main():
    """Clean all extracted JSON files."""
    json_files = list(EXTRACTED_DATA_DIR.glob("*_extracted.json"))
    
    if not json_files:
        print(f"No extracted JSON files found in {EXTRACTED_DATA_DIR}")
        return
    
    print(f"Found {len(json_files)} extracted file(s)")
    print("="*60)
    
    for json_path in json_files:
        print(f"\nProcessing: {json_path.name}")
        
        # Output: same name but replace "_extracted" with "_cleaned"
        output_path = json_path.parent / json_path.name.replace("_extracted", "_cleaned")
        
        try:
            result = clean_extracted_text(
                str(json_path),
                str(output_path),
                start_page=10,
                end_page=486
            )
            print(f"Successfully cleaned {len(result)} pages")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Cleaning complete!")


if __name__ == "__main__":
    main()
