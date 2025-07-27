from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    reply: str
    language: str
    confidence: Optional[float] = None

class WebhookMessage(BaseModel):
    user_id: str
    user_name: str
    message: str
    message_id: str
    timestamp: str

class UserHistory(BaseModel):
    user_id: str
    messages: list[str]
    last_interaction: Optional[datetime] = None
    message_count: Optional[int] = 0 