import jsonlines
from typing import List, Optional

from core.entity.CharacterCard import CharacterCard
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = f'{CURRENT_DIR}\\db\\characters.jsonl'


def load_all_characters() -> List[CharacterCard]:
    try:
        with jsonlines.open(db_path) as reader:
            return [CharacterCard(**obj) for obj in reader]
    except FileNotFoundError:
        return []


def get_id() -> int:
    return len(load_all_characters()) + 1


def save_all_characters(characters: List[CharacterCard]):
    with jsonlines.open(db_path, mode='w') as writer:
        writer.write_all([char.model_dump() for char in characters])


def add_character(card: CharacterCard):
    characters = load_all_characters()
    if any(c.id == card.id for c in characters):
        raise ValueError(f"角色 ID {card.id} 已存在")
    characters.append(card)
    save_all_characters(characters)


def get_character_by_id(character_id: int) -> Optional[CharacterCard]:
    characters = load_all_characters()
    for c in characters:
        if c.id == character_id:
            return c
    return None


def update_character(character_id: int, updated_card: CharacterCard):
    characters = load_all_characters()
    updated = False
    for i, c in enumerate(characters):
        if c.id == character_id:
            characters[i] = updated_card
            updated = True
            break
    if not updated:
        raise ValueError(f"角色 ID {character_id} 不存在")
    save_all_characters(characters)


def delete_character(character_id: int):
    characters = load_all_characters()
    new_characters = [c for c in characters if c.id != character_id]
    if len(new_characters) == len(characters):
        raise ValueError(f"角色 ID {character_id} 不存在")
    save_all_characters(new_characters)
