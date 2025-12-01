from fastapi import APIRouter, HTTPException
from app.backend.models.chat import ChatRequest, ChatResponse, ChatNameRequest, ChatNameResponse
from app.backend.services.chat_service import process_user_question, generate_chat_name

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Send a question to the Model.
    Body: {"query": "query string"}
    Returns: Dict with answer and sources, or just a string if not found
    """

    try:
        # Call the service
        result = await process_user_question(request.query)

        # Response Mapping
        # agent.ask() now returns a dict with 'answer' and 'sources'
        if isinstance(result, dict):
            answer = result.get("answer", "")
            raw_sources = result.get("sources", [])
            
            # Check if the answer indicates nothing was found
            if "Not found in ChromaDB" in answer:
                return {"answer": answer}
            
            # Transform sources to match frontend structure
            transformed_sources = []
            for source in raw_sources:
                transformed_source = {
                    "text": source.get("chapter_name") or source.get("text") or "Historical Document",
                    "author": f"Chapter {source.get('chapter_number')}" if source.get("chapter_number") else "Ancient Text",
                    "page": source.get("page_number")
                }
                transformed_sources.append(transformed_source)
            
            return ChatResponse(answer=answer, sources=transformed_sources)
        
        # Fallback for backward compatibility (if it returns just a string)
        if isinstance(result, str):
            return {"answer": result}

    except Exception as e:
        # In a real app, you would log the full error here
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error processing RAG request.")

@router.post("/chat/generate-name", response_model=ChatNameResponse)
async def generate_chat_name_endpoint(request: ChatNameRequest):
    """
    Generate a short, descriptive name for a chat based on the first message.
    Body: {"message": "first message string"}
    Returns: {"name": "generated chat name"}
    """
    
    try:
        chat_name = await generate_chat_name(request.message)
        return ChatNameResponse(name=chat_name)
    
    except Exception as e:
        print(f"Error generating chat name: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error generating chat name.")