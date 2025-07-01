from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateConversationDto(BaseModel):
    role: str
    sender_character: Optional[int] = None
    receiver_character: Optional[int] = None
    content: str
    create_time: Optional[datetime] = None
    parent: Optional[int] = None
    scene: int

    # 创建对话时，需要获取整个小说的内容，所以需要novel_id
    novel: Optional[int] = None


class ResponseConversationDto(CreateConversationDto):
    conversation_id: int
