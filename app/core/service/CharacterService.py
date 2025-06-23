from core.entity.ResponseEntity import ResponseModel, success
from core.entity.dto.CharacterDto import CreateCharacterDto, ResponseCharacterDto
from core.mapper.CharacterMapper import CharacterMapperInterface


class CharacterService:

    def __init__(self, character_mapper: CharacterMapperInterface):
        self.character_mapper = character_mapper

    def create_character(self, character: CreateCharacterDto) -> ResponseModel:
        character_id = self.character_mapper.create_character(character)
        return success(f"创建角色成功, 角色id为{character_id}")

    def select_character_by_id(self, character_id: int) -> ResponseModel[ResponseCharacterDto]:
        character = self.character_mapper.select_character_by_id(character_id)
        return success(data=character, message="获取角色成功")
