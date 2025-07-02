from abc import ABC
from typing import List

from pony.orm import commit, db_session

from core.entity.dto.CharacterDto import ResponseCharacterDto
from core.entity.dto.NovelDto import CreateCharacter2NovelDto
from core.entity.po.CharacterNovelEntity import CharacterNovelEntity
from core.mapper.NovelMapper import NovelMapperInterface
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
                 character_mapper: CharacterNovelMapperInterface,
                 novel_mapper: NovelMapperInterface):
        self.character_mapper = character_mapper
        self.novel_mapper = novel_mapper

    @db_session
    def connect_character_2_novel(self, character_novel: CreateCharacter2NovelDto):
        try:
            character_novel = CharacterNovelEntity(
                novel=character_novel.novel_id,
                character=character_novel.character,
            )

            commit()
            return character_novel.character_novel_id
        except Exception as e:
            logging.error(
                f"角色 ID {character_novel.character_id}，连接小说 ID {character_novel.novel_id} 失败，{str(e)}")
            raise DatabaseError(str(e))

    def get_connect_characters(self, novel_id: int):
        cn = CharacterNovelEntity.select(lambda data: data.novel.novel_id == novel_id)[:]

        result: List[ResponseCharacterDto] = []
        for c in cn:
            result.append(self.character_mapper.get_connect_characters_by_novel_id(c.character))


