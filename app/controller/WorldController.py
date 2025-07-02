from typing import List

from fastapi import APIRouter, Depends

from core.entity.ResponseEntity import ResponseModel
from core.entity.dto.WorldDto import ResponseWorldDto, CreateWorldDto, ResponseAllWorldDetailDto
from core.mapper.WorldMapper import WorldMapper
from core.service.WorldService import WorldService

world_router = APIRouter(prefix="/api/world", tags=["world"])


def get_world_service():
    return WorldService(WorldMapper())


@world_router.get("/")
def get_all_worlds(world_service: WorldService = Depends(get_world_service)) -> ResponseModel[List[ResponseWorldDto]]:
    return world_service.get_all_worlds()


@world_router.post("/")
def create_world(
        world: CreateWorldDto,
        world_service: WorldService = Depends(get_world_service)) -> ResponseModel:
    return world_service.create_world(world)


@world_router.get("/{world_id}")
def get_world_by_id(
        world_id: int,
        world_service: WorldService = Depends(get_world_service)) -> ResponseModel[ResponseAllWorldDetailDto]:
    return world_service.get_world_by_id(world_id)