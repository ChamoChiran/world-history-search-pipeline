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
    
    def ask(
        self,
        question: str,
        n_results: int = 10,
        max_retries: int = 3
    ) -> str:
        """
        Complete RAG pipeline: retrieve, prompt, and generate.
        
        Args:
            question: User question
            n_results: Number of results to retrieve from vector DB
            max_retries: Maximum number of retry attempts for generation
        
        Returns:
            Generated answer
        """
        # Step 1: Retrieve relevant context
        retrieved_data = self.query_vector_db(question, n_results=n_results)
        
        # Step 2: Build prompt with context
        prompt = build_rag_prompt(question, retrieved_data)
        
        # Step 3: Generate answer
        answer = self.generate_answer(prompt, max_retries=max_retries)
        
        return answer


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
