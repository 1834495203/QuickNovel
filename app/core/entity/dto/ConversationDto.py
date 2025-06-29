from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateConversationDto(BaseModel):
    role: str
    sender_character: Optional[int] = None
    receiver_character: Optional[int] = None
    content: str
    create_time: datetime
    parent: Optional[int] = None
    scene: int


class ResponseConversationDto(CreateConversationDto):
    conversation_id: int
