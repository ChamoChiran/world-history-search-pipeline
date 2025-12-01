from fastapi import APIRouter, HTTPException
from app.backend.models.chat import ChatRequest, ChatResponse
from app.backend.services.chat_service import process_user_question

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Send a question to the Model.
    Body: {"query": "query string"}
    """

    try:
        # Call the service
        result = await process_user_question(request.query)

        # Response Mapping
        # agent.ask() now returns a dict with 'answer' and 'sources'
        if isinstance(result, dict):
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            return ChatResponse(answer=answer, sources=sources)
        
        # Fallback for backward compatibility (if it returns just a string)
        if isinstance(result, str):
            return ChatResponse(answer=result, sources=[])

    except Exception as e:
        # In a real app, you would log the full error here
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error processing RAG request.")