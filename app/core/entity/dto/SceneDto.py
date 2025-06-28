from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateSceneDto(BaseModel):
    scene_name: str
    scene_desc: Optional[str] = ''
    create_time: datetime
    parent: Optional[int] = None
    chapter: Optional[int] = None


class ResponseSceneDto(BaseModel):
    scene_id: int
    scene_name: str
    scene_desc: Optional[str] = ''
    create_time: datetime
    parent: Optional[int]
    chapter: Optional[int]
