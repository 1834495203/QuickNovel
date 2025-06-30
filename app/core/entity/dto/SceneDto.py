from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from core.entity.dto.ConversationDto import ResponseConversationDto


class CreateSceneDto(BaseModel):
    scene_name: str
    scene_desc: Optional[str] = ''
    create_time: Optional[datetime] = None
    parent: Optional[int] = None
    chapter: Optional[int] = None


class ResponseSceneDto(BaseModel):
    scene_id: int
    scene_name: str
    scene_desc: Optional[str] = ''
    create_time: datetime
    parent: Optional[int]
    chapter: Optional[int]

    conversation: Optional[List[ResponseConversationDto]] = []
