from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from core.entity.dto.SceneDto import ResponseSceneDto


class CreateChapterDto(BaseModel):
    chapter_title: Optional[str] = ''
    chapter_desc: Optional[str] = ''
    create_time: Optional[datetime] = None
    parent: Optional[int] = None
    chapter_number: Optional[int]
    novel: int


class ResponseChapterDto(BaseModel):
    chapter_id: int
    chapter_number: int
    chapter_title: Optional[str]
    chapter_desc: Optional[str]
    create_time: datetime
    parent: Optional[int]
    novel: int


class ResponseAllChapterDto(ResponseChapterDto):
    scene: Optional[List[ResponseSceneDto]]
