import jsonlines
from typing import List, Optional
from core.entity.CharacterCard import CharacterCard
from core.entity.ResponseEntity import ResponseModel, success, error
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = f'{CURRENT_DIR}\\db\\characters.jsonl'

def load_all_characters() -> ResponseModel[List[CharacterCard]]:
    try:
        with jsonlines.open(db_path) as reader:
            characters = [CharacterCard(**obj) for obj in reader]
            return success(data=characters, message="角色列表获取成功")
    except Exception as e:
        return error(message=f"获取角色列表失败: {str(e)}")

def get_id() -> ResponseModel[int]:
    try:
        id = len(load_all_characters().data or []) + 1
        return success(data=id, message="ID生成成功")
    except Exception as e:
        return error(message=f"ID生成失败: {str(e)}")

def save_all_characters(characters: List[CharacterCard]) -> ResponseModel[None]:
    try:
        with jsonlines.open(db_path, mode='w') as writer:
            writer.write_all([char.model_dump() for char in characters])
        return success(message="保存成功")
    except Exception as e:
        return error(message=f"保存失败: {str(e)}")

def add_character(card: CharacterCard) -> ResponseModel[None]:
    try:
        characters = load_all_characters().data or []
        if any(c.id == card.id for c in characters):
            return error(message=f"角色 ID {card.id} 已存在")
        characters.append(card)
        save_result = save_all_characters(characters)
        if save_result.code != 200:
            return save_result
        return success(message="角色添加成功")
    except Exception as e:
        return error(message=f"添加角色失败: {str(e)}")

def get_character_by_id(character_id: int) -> ResponseModel[Optional[CharacterCard]]:
    try:
        characters = load_all_characters().data or []
        for c in characters:
            if c.id == character_id:
                return success(data=c, message="角色获取成功")
        return error(message=f"未找到ID为 {character_id} 的角色")
    except Exception as e:
        return error(message=f"获取角色失败: {str(e)}")

def update_character(character_id: int, updated_card: CharacterCard) -> ResponseModel[None]:
    try:
        characters = load_all_characters().data or []
        updated = False
        for i, c in enumerate(characters):
            if c.id == character_id:
                characters[i] = updated_card
                updated = True
                break
        if not updated:
            return error(message=f"角色 ID {character_id} 不存在")
        save_result = save_all_characters(characters)
        if save_result.code != 200:
            return save_result
        return success(message="角色更新成功")
    except Exception as e:
        return error(message=f"更新角色失败: {str(e)}")

def delete_character(character_id: int) -> ResponseModel[None]:
    try:
        characters = load_all_characters().data or []
        new_characters = [c for c in characters if c.id != character_id]
        if len(new_characters) == len(characters):
            return error(message=f"角色 ID {character_id} 不存在")
        save_result = save_all_characters(new_characters)
        if save_result.code != 200:
            return save_result
        return success(message="角色删除成功")
    except Exception as e:
        return error(message=f"删除角色失败: {str(e)}")
