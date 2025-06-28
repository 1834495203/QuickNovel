from typing import List

from fastapi import APIRouter, Depends

from core.entity.ResponseEntity import ResponseModel
from core.entity.dto.NovelDto import CreateNovelDto, ResponseAllNovelDto, ResponseNovelDto
from core.mapper.NovelMapper import NovelMapper
from core.service.NovelService import NovelService

novel_router = APIRouter(prefix="/api/novel", tags=["novel"])


def get_novel_service():
    return NovelService(NovelMapper())


@novel_router.post("/")
def create_novel(novel: CreateNovelDto,
                 novel_service: NovelService = Depends(get_novel_service)) -> ResponseModel:
    return novel_service.create_novel(novel)


@novel_router.get("/{novel_id}")
def get_novel_by_id(novel_id: int,
                    novel_service: NovelService = Depends(get_novel_service)) -> ResponseModel[ResponseAllNovelDto]:
    return novel_service.get_novel_by_id(novel_id)


@novel_router.get("/")
def get_all_novels(novel_service: NovelService = Depends(get_novel_service)) -> ResponseModel[List[ResponseNovelDto]]:
    return novel_service.get_all_novels()
