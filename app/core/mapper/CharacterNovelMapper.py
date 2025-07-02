from abc import ABC
from typing import List

from pony.orm import commit, db_session

from core.entity.dto.CharacterDto import ResponseCharacterDto
from core.entity.dto.NovelDto import CreateCharacter2NovelDto
from core.entity.po.CharacterNovelEntity import CharacterNovelEntity
from core.mapper.CharacterMapper import CharacterMapperInterface, CharacterMapper
from core.mapper.NovelMapper import NovelMapperInterface, NovelMapper
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import DatabaseError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class CharacterNovelMapperInterface(ABC):

    def connect_character_2_novel(self, character_novel: CreateCharacter2NovelDto):
        raise NotImplementedError()

    def get_connect_characters_by_novel_id(self, novel_id: int):
        raise NotImplementedError()


class CharacterNovelMapper(CharacterNovelMapperInterface):

    def __init__(self,
                 character_mapper: CharacterMapperInterface,
                 novel_mapper: NovelMapperInterface):
        self.character_mapper = character_mapper
        self.novel_mapper = novel_mapper

    @db_session
    def connect_character_2_novel(self, character_novel: CreateCharacter2NovelDto):
        try:
            cn = CharacterNovelEntity(
                novel=character_novel.novel_id,
                character=character_novel.character_id,
            )

            commit()
            return cn.character_novel_id
        except Exception as e:
            logging.error(
                f"角色 ID {character_novel.character_id}，连接小说 ID {character_novel.novel_id} 失败，{str(e)}")
            raise DatabaseError(str(e))

    @db_session
    def get_connect_characters_by_novel_id(self, novel_id: int) -> List[ResponseCharacterDto]:
        try:
            cn = CharacterNovelEntity.select(lambda data: data.novel.novel_id == novel_id)[:]

            result: List[ResponseCharacterDto] = []
            for c in cn:
                result.append(self.character_mapper.select_character_by_id(c.character.character_id))
            return result
        except Exception as e:
            logging.error(f"获取小说连接的角色失败，{str(e)}")
            raise DatabaseError(str(e))

    @db_session
    def create_character_prompt(self, character: ResponseCharacterDto):
        """
        将结构化的 CreateCharacterDto 数据转换为自然语言的 prompt 提示词。

        Args:
            character: CreateCharacterDto 对象，包含角色的详细信息

        Returns:
            str: 格式化后的 prompt 字符串
        """
        prompt = f"角色名称: {character.name}\n"

        prompt += f"描述: {character.description}\n\n"

        prompt += "背景故事:\n"
        prompt += f"{character.background_story}\n\n"

        prompt += "性格特征:\n"
        for trait in character.trait:
            prompt += f"- {trait.label}: {trait.description}\n"
        prompt += "\n"

        prompt += "标志性特征:\n"
        for distinctive in character.distinctive:
            prompt += f"- {distinctive.name}: {distinctive.content}\n"
        prompt += "\n"

        prompt += "对话示例:\n"
        for speak in character.speak:
            prompt += f"{speak.role}: {speak.content}\n"
            prompt += f"回复: {speak.reply}\n"

        return prompt


if __name__ == '__main__':
    generate_table_mapping()
    character_novel_mapper = CharacterNovelMapper(CharacterMapper(), NovelMapper())
    character_novel_mapper.connect_character_2_novel(CreateCharacter2NovelDto(
        novel_id=1,
        character_id=5
    ))
