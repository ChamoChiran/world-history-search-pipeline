"""Script to search the ChromaDB vector database."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval.search import retrieve_context, print_results
from src.utils import PROJECT_ROOT


def main():
    """Search the vector database with example queries."""
    
    # Database path
    db_dir = PROJECT_ROOT / "data" / "world_history_store"
    
    if not db_dir.exists():
        print(f"Database not found at: {db_dir}")
        print("Please run 04_build_vector_db.py first")
        return
    
    print("="*80)
    print("World History - Vector Search")
    print("="*80)
    print(f"Database: {db_dir}")
    print(f"Collection: world_history")
    print()
    
    # Example queries
    queries = [
        "How did the Neolithic Revolution change human societies?",
        "What were the main achievements of ancient Egyptian civilization?",
        "Describe the social structure of Mesopotamian cities",
    ]
    
    print("Running example queries...\n")
    
    for i, query in enumerate(queries, 1):
        print("="*80)
        print(f"Query {i}: {query}")
        print("="*80)
        
        try:
            results = retrieve_context(
                query=query,
                db_path=str(db_dir),
                collection_name="world_history",
                k=10
            )
            
            print_results(results)
            
        except Exception as e:
            print(f"Error during search: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(queries):
            print("\n" + "-"*80 + "\n")
    
    print("="*80)
    print("Search complete!")
    print()
    print("To search with custom queries, use the retrieve_context() function:")
    print("  from src.retrieval.search import retrieve_context")
    print("  results = retrieve_context(query='your question', db_path='...', k=5)")


def interactive_search():
    """Interactive search mode."""
    db_dir = PROJECT_ROOT / "data" / "world_history_store"
    
    if not db_dir.exists():
        print(f"Database not found at: {db_dir}")
        return
    
    print("="*80)
    print("AI Tutor - Interactive Search")
    print("="*80)
    print("Type your questions (or 'quit' to exit)")
    print()
    
    while True:
        query = input("Query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            results = retrieve_context(
                query=query,
                db_path=str(db_dir),
                collection_name="world_history",
                k=5
            )
            
            print_results(results)
            print()
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Run example queries
    main()
    
    # Uncomment to run interactive mode
    # interactive_search()

