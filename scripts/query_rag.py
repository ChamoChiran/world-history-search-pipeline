"""Query RAG system - Ask questions from the RAG system."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import HistoryAgent
from src.utils import PROJECT_ROOT


def main():
    """Interactive Q&A with the AI tutor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ask questions from the RAG system"
    )
    parser.add_argument(
        "--collection",
        default="world_history",
        help="ChromaDB collection name (default: world_history)"
    )
    parser.add_argument(
        "--db-path",
        default=str(PROJECT_ROOT / "data" / "vector_db"),
        help="Path to ChromaDB database (default: data/vector_db/)"
    )
    parser.add_argument(
        "--question",
        "-q",
        help="Ask a single question and exit"
    )
    parser.add_argument(
        "--n-results",
        type=int,
        default=10,
        help="Number of results to retrieve (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Setup DB path
    db_path = args.db_path or str(PROJECT_ROOT / "data" / "vector_db")
    
    print("="*80)
    print("AI TUTOR - RAG QUERY SYSTEM")
    print("="*80)
    print(f"\nCollection: {args.collection}")
    print(f"Database: {db_path}")
    print(f"Retrieving top {args.n_results} results per query\n")
    
    # Initialize agent
    print("Initializing AI tutor...")
    try:
        agent = HistoryAgent(
            db_path=db_path,
            collection_name=args.collection
        )
        print("Agent ready!\n")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)
    
    # Single question mode
    if args.question:
        print(f"Question: {args.question}\n")
        print("🤔 Thinking...\n")
        
        try:
            answer = agent.ask(args.question, n_results=args.n_results)
            print(f"Answer: {answer}\n")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        return
    
    # Interactive mode
    print("="*80)
    print("💡 Ask questions (type 'exit' to quit)")
    print("="*80 + "\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            if not question:
                continue
            
            print("\nThinking...\n")
            
            answer = agent.ask(question, n_results=args.n_results)
            print(f"Answer: {answer}\n")
            print("-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
