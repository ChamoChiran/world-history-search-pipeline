import json
import uuid
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util


def ensure_nltk_data():
    """Download required NLTK data if not present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt')


def split_into_sentences(pages_data):
    """
    Add a 'sentences' list to each page in the data.
    
    Args:
        pages_data: Dict of page data with 'text' field
    
    Returns:
        Updated pages_data with 'sentences' field added
    """
    ensure_nltk_data()
    
    for key, value in pages_data.items():
        text = value.get("text", "").strip()
        
        if text:
            sentences = sent_tokenize(text)
        else:
            sentences = []
        
        value["sentences"] = sentences
    
    return pages_data


def build_semantic_chunks(pages_data,
                          model_name="all-MiniLM-L6-v2",
                          similarity_threshold=0.55,
                          max_sentences_per_chunk=10):
    """
    Build semantic chunks from pages using sentence similarity.
    
    Args:
        pages_data: Dict of page data with 'sentences' and 'chapter_details' fields
        model_name: SentenceTransformer model to use for embeddings
        similarity_threshold: Minimum cosine similarity to keep sentences together
        max_sentences_per_chunk: Maximum sentences per chunk before forcing split
    
    Returns:
        List of chunk dicts with chunk_id, chapter_metadata, and text
    """
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    
    all_chunks = []
    
    for page_num, page in pages_data.items():
        sentences = page.get("sentences", [])
        chapter_metadata = page.get("chapter_details")
        
        if not sentences:
            continue
        
        # Embed all sentences for this page
        embeddings = model.encode(sentences, convert_to_tensor=True)
        
        current_chunk_sentences = []
        current_chunk_embeddings = []
        
        def flush_chunk():
            """Save the current chunk and reset."""
            if not current_chunk_sentences:
                return
            
            chunk_text = " ".join(current_chunk_sentences).strip()
            if not chunk_text:
                return
            
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "chapter_metadata": chapter_metadata if chapter_metadata else "UNKNOWN",
                "text": chunk_text,
            })
        
        # Build chunks by iterating through sentences
        for i, sentence in enumerate(sentences):
            sent_embedding = embeddings[i]
            
            # First sentence always starts a new chunk
            if not current_chunk_embeddings:
                current_chunk_sentences.append(sentence)
                current_chunk_embeddings.append(sent_embedding)
                continue
            
            # Calculate similarity with previous sentence
            prev_embedding = current_chunk_embeddings[-1]
            similarity = util.pytorch_cos_sim(prev_embedding, sent_embedding).item()
            
            # Decide whether to split chunk
            split_by_size = len(current_chunk_sentences) >= max_sentences_per_chunk
            split_by_similarity = similarity < similarity_threshold
            
            if split_by_size or split_by_similarity:
                # Save current chunk and start new one
                flush_chunk()
                current_chunk_sentences = [sentence]
                current_chunk_embeddings = [sent_embedding]
            else:
                # Add to current chunk
                current_chunk_sentences.append(sentence)
                current_chunk_embeddings.append(sent_embedding)
        
        # Flush any remaining chunk for this page
        flush_chunk()
    
    print(f"Created {len(all_chunks)} semantic chunks")
    return all_chunks


def chunk_from_json(input_path, 
                    output_path=None,
                    similarity_threshold=0.55,
                    max_sentences_per_chunk=10):
    """
    Load cleaned book JSON, tokenize into sentences, and create semantic chunks.
    
    Args:
        input_path: Path to cleaned_book.json
        output_path: Optional path to save chunks JSON
        similarity_threshold: Semantic similarity threshold for chunking
        max_sentences_per_chunk: Max sentences per chunk
    
    Returns:
        List of chunks
    """
    print(f"Loading data from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        pages_data = json.load(f)
    
    print("Tokenizing sentences...")
    pages_with_sentences = split_into_sentences(pages_data)
    
    print("Building semantic chunks...")
    chunks = build_semantic_chunks(
        pages_with_sentences,
        similarity_threshold=similarity_threshold,
        max_sentences_per_chunk=max_sentences_per_chunk
    )
    
    if output_path:
        print(f"Saving chunks to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(chunks)} chunks")
    
    return chunks


if __name__ == "__main__":
    # Example usage
    input_file = "../data/clean/cleaned_book.json"
    output_file = "../data/clean/semantic_chunks.json"
    
    chunks = chunk_from_json(
        input_path=input_file,
        output_path=output_file,
        similarity_threshold=0.55,
        max_sentences_per_chunk=10
    )
    
    print(f"\n✓ Complete! Generated {len(chunks)} chunks")
    
    # Show first chunk as example
    if chunks:
        print("\nExample chunk:")
        print(f"ID: {chunks[0]['chunk_id']}")
        print(f"Chapter: {chunks[0]['chapter_metadata']}")
        print(f"Text: {chunks[0]['text'][:200]}...")
