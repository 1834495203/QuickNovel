from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from core.entity.dto.ChapterDto import ResponseAllChapterDto


class CreateNovelDto(BaseModel):
    novel_name: str
    novel_desc: str
    create_time: datetime


class ResponseNovelDto(BaseModel):
    novel_id: int
    novel_name: str
    novel_desc: str
    create_time: datetime


class ResponseAllNovelDto(ResponseNovelDto):
    chapter: Optional[List[ResponseAllChapterDto]]
