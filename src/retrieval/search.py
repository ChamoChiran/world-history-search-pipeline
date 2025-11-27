"""Search and retrieve relevant content from ChromaDB vector database."""

import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Any


def get_embedder(model_name="all-MiniLM-L6-v2"):
    """
    Load a SentenceTransformer model for generating query embeddings.
    
    Args:
        model_name: Name of the model (default: all-MiniLM-L6-v2)
    
    Returns:
        SentenceTransformer model instance
    """
    return SentenceTransformer(model_name)


def load_collection(db_path, collection_name="world_history"):
    """
    Load an existing ChromaDB collection.
    
    Args:
        db_path: Directory path where the database is stored
        collection_name: Name of the collection to load
    
    Returns:
        ChromaDB collection object
    """
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database path not found: {db_path}")
    
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_collection(name=collection_name)
    
    return collection


def search(query: str, 
           collection, 
           embedder, 
           k: int = 10) -> Dict[str, Any]:
    """
    Search for relevant chunks using semantic similarity.
    
    Args:
        query: Search query text
        collection: ChromaDB collection object
        embedder: SentenceTransformer model for query embedding
        k: Number of results to return (default: 10)
    
    Returns:
        Dictionary with query results containing documents, metadatas, distances
    """
    # Generate query embedding
    query_emb = embedder.encode([query]).tolist()
    
    # Search in ChromaDB
    results = collection.query(
        query_embeddings=query_emb,
        n_results=k
    )
    
    return results


def format_search_results(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format raw ChromaDB results into a cleaner structure.
    
    Args:
        results: Raw results from ChromaDB query
    
    Returns:
        List of formatted result dictionaries
    """
    formatted = []
    
    if not results.get("documents") or not results["documents"]:
        return formatted
    
    documents = results["documents"][0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]
    
    for i, doc in enumerate(documents):
        formatted.append({
            "chunk_id": ids[i] if i < len(ids) else None,
            "text": doc,
            "chapter_metadata": metadatas[i].get("chapter_metadata", "UNKNOWN") if i < len(metadatas) else "UNKNOWN",
            "distance": distances[i] if i < len(distances) else None,
            "relevance_score": 1 - distances[i] if i < len(distances) else None  # Convert distance to similarity
        })
    
    return formatted


def retrieve_context(query: str,
                     db_path: str,
                     collection_name: str = "world_history",
                     model_name: str = "all-MiniLM-L6-v2",
                     k: int = 5) -> List[Dict[str, Any]]:
    """
    High-level retrieval function: load collection, search, and format results.
    
    Args:
        query: Search query text
        db_path: Path to ChromaDB database
        collection_name: Name of the collection
        model_name: SentenceTransformer model name
        k: Number of results to return
    
    Returns:
        List of formatted search results
    """
    embedder = get_embedder(model_name)
    collection = load_collection(db_path, collection_name)
    
    results = search(query, collection, embedder, k)
    formatted = format_search_results(results)
    
    return formatted


def print_results(results: List[Dict[str, Any]]):
    """
    Pretty print search results.
    
    Args:
        results: List of formatted search results
    """
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{'='*80}")
        print(f"Result {i}")
        print(f"{'='*80}")
        print(f"Chapter: {result['chapter_metadata']}")
        if result.get('relevance_score') is not None:
            print(f"Relevance Score: {result['relevance_score']:.4f}")
        print(f"\nText:\n{result['text']}")
        print()
