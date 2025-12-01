"""GenAI model for RAG pipeline."""

import os
import time
from typing import Optional
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

from .prompts import build_rag_prompt


# Load environment variables
load_dotenv()


class HistoryAgent:
    """GenAI history tutor agent with RAG capabilities."""
    
    def __init__(
        self,
        db_path: str,
        collection_name: str = "world_history",
        model_name: str = "models/gemini-2.5-pro",
        api_key: Optional[str] = None
    ):
        """
        Initialize the tutor agent.
        
        Args:
            db_path: Path to ChromaDB database
            collection_name: Name of the ChromaDB collection
            model_name: Gemini model name
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        # Setup ChromaDB
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(name=collection_name)
        
        # Setup Gemini
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def query_vector_db(self, query: str, n_results: int = 10) -> dict:
        """
        Query the ChromaDB collection with a question.
        
        Args:
            query: User question
            n_results: Number of results to retrieve
        
        Returns:
            ChromaDB query results
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def generate_answer(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: int = 10
    ) -> str:
        """
        Generate answer using Gemini with retry logic.
        
        Args:
            prompt: Formatted prompt
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay in seconds between retries
        
        Returns:
            Generated answer text
        """
        for attempt in range(max_retries):
            try:
                answer = self.model.generate_content(prompt)
                return answer.text
            except Exception as e:
                if "ResourceExhausted" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * retry_delay
                    print(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def parse_chapter_metadata(self, metadata_string: str) -> dict:
        """
        Parse chapter metadata string into structured data.
        
        Args:
            metadata_string: String like "CHAPTER: 1 - Ancient Egypt | pg-42"
        
        Returns:
            Dict with chapter_number, chapter_name, and page_number
        """
        result = {
            "chapter_number": None,
            "chapter_name": None,
            "page_number": None
        }
        
        try:
            # Split by | to separate chapter info from page
            parts = metadata_string.split("|")
            
            # Extract page number
            if len(parts) > 1:
                page_part = parts[1].strip()
                if page_part.startswith("pg-"):
                    result["page_number"] = int(page_part.replace("pg-", ""))
            
            # Extract chapter info
            if len(parts) > 0 and "CHAPTER:" in parts[0]:
                chapter_part = parts[0].replace("CHAPTER:", "").strip()
                chapter_info = chapter_part.split("-", 1)
                
                if len(chapter_info) > 0:
                    chapter_num = chapter_info[0].strip()
                    if chapter_num and chapter_num.lower() != "none":
                        result["chapter_number"] = chapter_num
                
                if len(chapter_info) > 1:
                    chapter_name = chapter_info[1].strip()
                    if chapter_name and chapter_name.lower() != "none":
                        result["chapter_name"] = chapter_name
        except Exception as e:
            print(f"Error parsing metadata: {e}")
        
        return result
    
    def ask(
        self,
        question: str,
        n_results: int = 10,
        max_retries: int = 3
    ) -> dict:
        """
        Complete RAG pipeline: retrieve, prompt, and generate.
        
        Args:
            question: User question
            n_results: Number of results to retrieve from vector DB
            max_retries: Maximum number of retry attempts for generation
        
        Returns:
            Dict with 'answer' (str) and 'sources' (list)
        """
        # Step 1: Retrieve relevant context
        retrieved_data = self.query_vector_db(question, n_results=n_results)
        
        # Step 2: Build prompt with context
        prompt = build_rag_prompt(question, retrieved_data)
        
        # Step 3: Generate answer
        answer = self.generate_answer(prompt, max_retries=max_retries)
        
        # Step 4: Format sources from retrieved data
        sources = []
        documents = retrieved_data.get("documents", [[]])[0]
        metadatas = retrieved_data.get("metadatas", [[]])[0]
        
        for i, doc in enumerate(documents):
            if i < len(metadatas):
                chapter_metadata = metadatas[i].get("chapter_metadata", "")
                parsed_metadata = self.parse_chapter_metadata(chapter_metadata)
                
                sources.append({
                    "text": doc,
                    "chapter_number": parsed_metadata["chapter_number"],
                    "chapter_name": parsed_metadata["chapter_name"],
                    "page_number": parsed_metadata["page_number"]
                })
        
        return {
            "answer": answer,
            "sources": sources
        }


def get_chroma_collection(db_path: str, collection_name: str):
    """
    Get a ChromaDB collection by name.
    
    Args:
        db_path: Path to ChromaDB database
        collection_name: Name of the collection
    
    Returns:
        ChromaDB collection
    """
    client = chromadb.PersistentClient(path=db_path)
    return client.get_collection(name=collection_name)
