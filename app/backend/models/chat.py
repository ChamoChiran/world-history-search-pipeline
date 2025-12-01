from pydantic import BaseModel, Field
from typing import List, Optional

class Source(BaseModel):
    text: str = Field(..., description="Text content from the source document")
    chapter_number: Optional[str] = Field(None, description="Chapter number")
    chapter_name: Optional[str] = Field(None, description="Chapter name")
    page_number: Optional[int] = Field(None, description="Page number")

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's query for the chat")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Generated answer from the chat model")
    sources: List[Source] = Field(..., description="List of source documents used to generate the answer")