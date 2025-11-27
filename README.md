# World History Search Pipeline

A semantic search system that processes world history textbooks into a queryable vector database, enabling intelligent information retrieval for educational applications.

## Current Phase: Data Ingestion & Vector Search

This project is currently in the **data pipeline and retrieval phase**, focusing on building a robust semantic search foundation for educational content.

![Data Ingestion Pipeline](diagrams/world-history-ingestion.png)

## Project Overview

The pipeline transforms unstructured PDF textbooks into a semantically searchable knowledge base using:
- **Semantic chunking** based on content similarity
- **Dense vector embeddings** for meaning-aware search
- **Persistent vector storage** for efficient retrieval

## Pipeline Workflow

### 1. **PDF Extraction**
- **Script**: `scripts/01_extract_pdf.py`
- **Module**: `src/ingestion/extract_text.py`
- Extracts text and metadata from PDF pages
- Preserves chapter structure and page information

### 2. **Text Cleaning**
- **Script**: `scripts/02_clean_text.py`
- **Module**: `src/ingestion/clean_text.py`
- Removes headers, footers, and page numbers
- Normalizes whitespace and formatting
- Maintains chapter metadata linkage

### 3. **Semantic Chunking**
- **Script**: `scripts/03_create_chunks.py`
- **Module**: `src/ingestion/chunk_text.py`
- Uses NLTK for sentence tokenization
- Employs `all-MiniLM-L6-v2` embeddings
- Groups semantically similar sentences (threshold: 0.55 cosine similarity)
- Max chunk size: 10 sentences

### 4. **Vector Database Creation**
- **Script**: `scripts/04_build_vector_db.py`
- **Module**: `src/embeddings/store.py`
- Generates 384-dimensional embeddings
- Stores in ChromaDB with HNSW indexing
- Uses cosine distance for similarity

### 5. **Semantic Search**
- **Script**: `scripts/05_search_vector_db.py`
- **Module**: `src/retrieval/search.py`
- Query-based vector similarity search
- Returns top-k relevant passages with metadata
- Context-aware results with chapter information

## Technology Stack

- **Python 3.x**
- **Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2)
- **Vector Store**: ChromaDB
- **NLP**: NLTK
- **PDF Processing**: PDFPlumber
- **Framework**: LangChain
- **Notebooks**: Jupyter Lab

## Installation

```bash
# Clone the repository
git clone https://github.com/ChamoChiran/world-history-search-pipeline.git
cd world-history-search-pipeline

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

## Usage

### Running the Full Pipeline

```bash
# 1. Extract text from PDF
python scripts/01_extract_pdf.py

# 2. Clean extracted text
python scripts/02_clean_text.py

# 3. Create semantic chunks
python scripts/03_create_chunks.py

# 4. Build vector database
python scripts/04_build_vector_db.py

# 5. Search the database
python scripts/05_search_vector_db.py
```

### Interactive Notebooks

Explore the pipeline interactively:
- `notebooks/pdf-explore.ipynb` - PDF exploration
- `notebooks/pdf-extract-test.ipynb` - Extraction testing
- `notebooks/vector-search.ipynb` - Search experimentation

## Project Structure

```
world-history-search-pipeline/
├── src/
│   ├── ingestion/          # Text extraction and processing
│   ├── embeddings/         # Vector store management
│   ├── retrieval/          # Search functionality
│   └── utils/              # Configuration and logging
├── scripts/                # Sequential pipeline scripts
├── notebooks/              # Jupyter notebooks for exploration
├── diagrams/               # Architecture diagrams
└── requirements.txt        # Python dependencies
```

## Example Query

```python
from src.retrieval.search import search_vector_db

results = search_vector_db(
    query="How did the Neolithic Revolution change human societies?",
    k=5
)

for result in results:
    print(f"Chapter: {result['chapter']}")
    print(f"Text: {result['text']}\n")
```

## Use Cases

- **Educational AI Tutors**: Retrieve relevant historical context for student questions
- **Study Assistants**: Find specific information across large textbooks
- **Research Tools**: Semantic exploration of historical topics
- **Quiz Generation**: Extract content for assessment creation

## Future Development

- [ ] Integration with LLM for conversational AI tutor
- [ ] Multi-document support
- [ ] Web interface with Gradio/FastAPI
- [ ] Advanced metadata filtering
- [ ] Citation and source tracking
- [ ] Multi-modal support (images, charts)

## License

MIT License - See LICENSE file for details
