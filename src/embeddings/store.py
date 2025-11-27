"""Store embeddings in ChromaDB vector database."""

import json
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer


def get_embedder(model_name="all-MiniLM-L6-v2"):
    """
    Load a SentenceTransformer model for generating embeddings.
    
    Args:
        model_name: Name of the model (default: all-MiniLM-L6-v2)
    
    Returns:
        SentenceTransformer model instance
    """
    print(f"Loading embedding model: {model_name}...")
    return SentenceTransformer(model_name)


def create_chroma_collection(persist_path, collection_name="history_book"):
    """
    Create or get a ChromaDB collection.
    
    Args:
        persist_path: Directory path to persist the database
        collection_name: Name of the collection
    
    Returns:
        ChromaDB collection object
    """
    Path(persist_path).mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(persist_path))
    
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # cosine distance for embeddings
    )
    
    return collection


def store_chunks_in_chroma(chunks, collection, embedder, batch_size=100):
    """
    Store text chunks with embeddings in ChromaDB.
    
    Args:
        chunks: List of chunk dicts with chunk_id, chapter_metadata, text
        collection: ChromaDB collection object
        embedder: SentenceTransformer model for generating embeddings
        batch_size: Number of chunks to store per batch
    """
    texts = []
    ids = []
    metadatas = []
    
    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        texts.append(chunk["text"])
        
        metadatas.append({
            "chapter_metadata": chunk.get("chapter_metadata", "UNKNOWN"),
        })
    
    print("Generating embeddings...")
    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()
    
    # Add in batches to avoid ChromaDB batch size limits
    total_chunks = len(chunks)
    print(f"Storing {total_chunks} chunks in ChromaDB...")
    
    for i in range(0, total_chunks, batch_size):
        end_idx = min(i + batch_size, total_chunks)
        
        collection.add(
            ids=ids[i:end_idx],
            documents=texts[i:end_idx],
            metadatas=metadatas[i:end_idx],
            embeddings=embeddings[i:end_idx]
        )
        
        print(f"Batch {i//batch_size + 1}: {end_idx}/{total_chunks} chunks stored")
    
    print(f"All {total_chunks} chunks stored in ChromaDB")


def build_vector_db_from_chunks(chunks_path, 
                                  db_path,
                                  collection_name="world_history",
                                  model_name="all-MiniLM-L6-v2",
                                  batch_size=100):
    """
    Load chunks from JSON and build a ChromaDB vector database.
    
    Args:
        chunks_path: Path to chunks JSON file
        db_path: Directory path to store ChromaDB
        collection_name: Name for the ChromaDB collection
        model_name: SentenceTransformer model name
        batch_size: Batch size for storing chunks
    
    Returns:
        ChromaDB collection object
    """
    print(f"Loading chunks from {chunks_path}...")
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    
    embedder = get_embedder(model_name)
    collection = create_chroma_collection(db_path, collection_name)
    
    store_chunks_in_chroma(chunks, collection, embedder, batch_size)
    
    return collection
