from fastapi import APIRouter, Depends

from core.entity.dto.ChapterDto import CreateChapterDto
from core.mapper.ChapterMapper import ChapterMapper
from core.service.ChapterService import ChapterService

chapter_router = APIRouter(prefix="/api/chapter", tags=["chapter"])


def get_chapter_service():
    return ChapterService(ChapterMapper())


@chapter_router.post("/")
def create_chapter(chapter: CreateChapterDto,
                   chapter_service: ChapterService = Depends(get_chapter_service)):
    return chapter_service.create_chapter(chapter)
