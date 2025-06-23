from typing import List

from fastapi import APIRouter, Depends

from core.entity.ResponseEntity import ResponseModel
from core.entity.dto.CharacterDto import ResponseCharacterDto, CreateCharacterDto
from core.mapper.CharacterMapper import CharacterMapper
from core.service.CharacterService import CharacterService


character_router = APIRouter(prefix="/api/character", tags=["Character"])


def get_character_service():
    return CharacterService(CharacterMapper())


@character_router.get("/{character_id}")
def get_character_by_id(
        character_id: int,
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel[ResponseCharacterDto]:
    return character_service.select_character_by_id(character_id)


@character_router.post("/")
def create_character(
        character: CreateCharacterDto,
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel:
    return character_service.create_character(character)


@character_router.get("/")
def get_all_characters(
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel[List[ResponseCharacterDto]]:
    return character_service.get_all_characters()


@character_router.delete("/{character_id}")
def delete_character(
        character_id: int,
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel:
    return character_service.delete_character(character_id)
