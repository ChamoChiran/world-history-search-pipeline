from functools import lru_cache
from src.agents.model import HistoryAgent
from app.backend.core.settings import get_settings

@lru_cache()
def get_rag_agent() -> HistoryAgent:
    """
    Initializes the RAG agent.
    this handles loading the embedding model, and connecting to ChromaDB.
    """
    print("Loading RAG Agent... this might take a moment...")
    
    settings = get_settings()

    # we initate the class you built in src/agents/model.py
    agent = HistoryAgent(
        db_path=settings.CHROMA_DB_DIR,
        collection_name="world_history"
    )

    print("RAG Agent loaded and ready.")
    return agent

async def process_user_question(query: str):
    """
    Helper function to process a single question.
    """

    agent = get_rag_agent()

    # We call the "asj" method defined in HistoryAgent
    response = agent.ask(query)

    return response