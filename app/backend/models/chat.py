from pydantic import BaseModel, Field
from typing import List, Optional

class Source(BaseModel):
    text: str = Field(..., description="Title or name of the source document")
    author: Optional[str] = Field(None, description="Author or reference information")
    page: Optional[int] = Field(None, description="Page number")

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's query for the chat")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Generated answer from the chat model")
    sources: List[Source] = Field(..., description="List of source documents used to generate the answer")

class ChatNameRequest(BaseModel):
    message: str = Field(..., min_length=1, description="First message to generate a chat name from")

class ChatNameResponse(BaseModel):
    name: str = Field(..., description="Generated short chat name")