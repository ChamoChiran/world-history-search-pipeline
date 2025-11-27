"""Script to build ChromaDB vector database from chunks."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.store import build_vector_db_from_chunks
from src.utils import EXTRACTED_DATA_DIR, PROJECT_ROOT


def main():
    """Build vector database from chunk files."""
    chunks_dir = EXTRACTED_DATA_DIR
    chunks_files = list(chunks_dir.glob("*_chunks.json"))
    
    if not chunks_files:
        print(f"No chunk files found in {chunks_dir}")
        return
    
    print(f"Found {len(chunks_files)} chunk file(s)")
    print("="*60)
    
    # Vector DB storage location
    db_dir = PROJECT_ROOT / "data" / "vector_db"
    
    for chunks_path in chunks_files:
        print(f"\nProcessing: {chunks_path.name}")
        
        try:
            collection = build_vector_db_from_chunks(
                chunks_path=str(chunks_path),
                db_path=str(db_dir),
                model_name="all-MiniLM-L6-v2",
                batch_size=100
            )
            
            print(f"\nVector database built: {chunks_path.stem.replace('_chunks','')}")
            print(f"  Collection: {collection.name}")
            print(f"  Total vectors: {collection.count()}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"Vector database creation complete!")
    print(f"Database stored in: {db_dir}")


if __name__ == "__main__":
    main()
