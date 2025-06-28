from typing import List

from fastapi import APIRouter, Depends, UploadFile, File

from core.entity.ResponseEntity import ResponseModel
from core.entity.dto.CharacterDto import ResponseCharacterDto, CreateCharacterDto, UpdateCharacterDto
from core.mapper.CharacterMapper import CharacterMapper
from core.service.CharacterService import CharacterService


character_router = APIRouter(prefix="/api/character", tags=["Character"])


def get_character_service():
    return CharacterService(CharacterMapper())


@character_router.get("/{character_id}")
def get_character_by_id(
        character_id: int,
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel[ResponseCharacterDto]:
    """
    根据id获取角色
    :param character_id: 角色id
    :param character_service: service
    :return: resp
    """
    return character_service.select_character_by_id(character_id)


@character_router.post("/")
def create_character(
        character: CreateCharacterDto,
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel:
    """
    创建角色
    :param character: 创建角色的信息
    :param character_service: service
    :return: resp
    """
    return character_service.create_character(character)


@character_router.get("/")
def get_all_characters(
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel[List[ResponseCharacterDto]]:
    """
    获取全部角色信息
    :param character_service: service
    :return: resp
    """
    return character_service.get_all_characters()


@character_router.delete("/{character_id}")
def delete_character(
        character_id: int,
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel:
    """
    删除角色
    :param character_id: 角色id
    :param character_service: service
    :return: resp
    """
    return character_service.delete_character(character_id)


@character_router.post("/{character_id}/avatar")
async def update_avatar(character_id: int,
                  avatar: UploadFile = File(...),
                  character_service: CharacterService = Depends(get_character_service)) -> ResponseModel:
    """
    更新头像信息
    :param character_id: 角色id
    :param avatar: 角色头像
    :param character_service: service
    :return: resp
    """
    return await character_service.update_avatar(character_id, avatar)


@character_router.post("/{character_id}")
def update_character(
        character: UpdateCharacterDto,
        character_service: CharacterService = Depends(get_character_service)) -> ResponseModel[ResponseCharacterDto]:
    """
    更新角色信息，但不包含头像
    :param character: 角色信息
    :param character_service: service
    :return: resp
    """
    return character_service.update_character(character)
