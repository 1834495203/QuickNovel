from fastapi import APIRouter, HTTPException
from typing import List

from core.entity.ResponseEntity import ResponseModel
from core.service.CharacerService import (
    load_all_characters,
    add_character,
    get_character_by_id,
    update_character,
    delete_character,
    get_id
)
from core.entity.CharacterCard import CharacterCard

characters_router = APIRouter(prefix="/api/characters", tags=["characters"])

@characters_router.get("/", response_model=ResponseModel)
async def get_all_characters() -> ResponseModel:
    return load_all_characters()

@characters_router.get("/{character_id}", response_model=ResponseModel)
async def get_character(character_id: int):
    return get_character_by_id(character_id)

@characters_router.post("/", response_model=ResponseModel)
async def create_character(character: CharacterCard):
    character.id = get_id().data
    return add_character(character)


@characters_router.put("/{character_id}", response_model=ResponseModel)
async def update_character_by_id(character_id: int, character: CharacterCard):
    character.id = character_id
    return update_character(character_id, character)

@characters_router.delete("/{character_id}")
async def delete_character_by_id(character_id: int):
    try:
        return delete_character(character_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
