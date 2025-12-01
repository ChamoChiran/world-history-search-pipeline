from functools import lru_cache
from src.agents.model import HistoryAgent
from app.backend.core.settings import get_settings
import google.generativeai as genai
import os

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

async def generate_chat_name(first_message: str) -> str:
    """
    Generate a short, descriptive name for a chat based on the first message.
    Uses a lightweight Gemini model (gemini-2.0-flash-lite) for fast generation.
    
    Args:
        first_message: The first message from the user in the chat
    
    Returns:
        A short chat name (3-6 words)
    """
    settings = get_settings()
    
    # Configure Gemini API
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    # Use a lightweight, fast model for name generation
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt = f"""Act as a deterministic naming system.

                    Instructions:
                    - Produce a chat title of 3–6 words.
                    - Summarize the user's message accurately.
                    - No quotes, symbols, or extra text.
                    - Output only the title.

                    User message: {first_message}

                    Chat name:
                """

    
    try:
        # Check if API key is configured
        if not settings.GEMINI_API_KEY:
            print("WARNING: GEMINI_API_KEY is not set. Using fallback chat name.")
            fallback_name = first_message[:40] + "..." if len(first_message) > 40 else first_message
            return fallback_name
        
        response = model.generate_content(prompt)
        chat_name = response.text.strip()
        
        # Remove quotes if present and limit length
        chat_name = chat_name.strip('"').strip("'").strip()
        
        # Fallback if name is too long (more than 50 characters)
        if len(chat_name) > 50:
            chat_name = chat_name[:47] + "..."
        
        print(f"Generated chat name: {chat_name}")
        return chat_name
    
    except Exception as e:
        print(f"Error generating chat name: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback to a truncated version of the first message
        fallback_name = first_message[:40] + "..." if len(first_message) > 40 else first_message
        return fallback_name