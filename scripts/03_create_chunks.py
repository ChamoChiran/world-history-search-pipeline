"""Script to create semantic chunks from cleaned text."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.chunk_text import chunk_from_json
from src.utils import EXTRACTED_DATA_DIR


def main():
    """Create semantic chunks from cleaned JSON files."""
    json_files = list(EXTRACTED_DATA_DIR.glob("*_cleaned.json"))
    
    if not json_files:
        print(f"No cleaned JSON files found in {EXTRACTED_DATA_DIR}")
        return
    
    print(f"Found {len(json_files)} cleaned file(s)")
    print("="*60)
    
    for json_path in json_files:
        print(f"\nProcessing: {json_path.name}")
        
        # Output: same name but replace "_cleaned" with "_chunks"
        output_path = json_path.parent / json_path.name.replace("_cleaned", "_chunks")
        
        try:
            chunks = chunk_from_json(
                input_path=str(json_path),
                output_path=str(output_path),
                similarity_threshold=0.55,
                max_sentences_per_chunk=10
            )
            print(f"✓ Created {len(chunks)} semantic chunks")
            
            # Show first chunk example
            if chunks:
                print(f"\nExample chunk:")
                print(f"  Chapter: {chunks[0]['chapter_metadata']}")
                print(f"  Text preview: {chunks[0]['text'][:150]}...")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Chunking complete!")


if __name__ == "__main__":
    main()
