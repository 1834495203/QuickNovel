import logging
import os
from abc import ABC

from pony.orm import db_session, commit

from core.entity.dto.CharacterDto import *
from core.entity.po.CharacterEntity import *
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import NotFoundError, DatabaseError, FileError


class CharacterMapperInterface(ABC):

    def create_character(self, character: CreateCharacterDto) -> bool:
        raise NotImplementedError()

    def update_avatar(self, character_id: int, avatar: str) -> bool:
        raise NotImplementedError()

    def get_all_characters(self) -> List[ResponseCharacterDto]:
        raise NotImplementedError()

    def delete_character_by_id(self, character_id: int) -> bool:
        raise NotImplementedError()

    def select_character_by_id(self, character_id: int) -> ResponseCharacterDto:
        raise NotImplementedError()


class CharacterMapper(CharacterMapperInterface):

    @db_session
    def create_character(self, character: CreateCharacterDto) -> int:
        # 创建角色实体
        c = CharacterEntity(
            name=character.name,
            description=character.description,
            background_story=character.background_story,
        )

        # 处理 traits
        if character.traits:
            for trait_dto in character.traits:
                trait = Trait(
                    label=trait_dto.label,
                    description=trait_dto.description,
                    character=c
                )
                c.trait.add(trait)

        # 处理 speaking
        if character.speakings:
            for speaking_dto in character.speakings:
                speaking = Speak(
                    role=speaking_dto.role,
                    content=speaking_dto.content,
                    reply=speaking_dto.reply,
                    character=c
                )
                c.speaking.add(speaking)

        # 处理 distinctive
        if character.distinct:
            for distinctive_dto in character.distinct:
                distinctive = Distinctive(
                    name=distinctive_dto.name,
                    content=distinctive_dto.content,
                    character=c
                )
                c.distinctive.add(distinctive)

        # 提交事务
        commit()

        # 记录日志
        logging.info(f"创建角色成功，id为:{c.character_id}，角色信息为:{c}")
        return c.character_id

    @db_session
    def update_avatar(self, character_id, avatar) -> bool:
        character = self.select_character_by_id(character_id)
        if character.avatar and os.path.exists(avatar):
            # 删除旧头像
            try:
                os.remove(avatar)
            except Exception as e:
                logging.error(f"删除文件失败，{e}")
                raise FileError(str(e))

        character.avatar = avatar
        logging.info(f"更新头像完成，角色id为{character_id}")
        return True

    @db_session
    def get_all_characters(self) -> List[ResponseCharacterDto]:
        # 查询所有 CharacterEntity 记录
        characters = CharacterEntity.select(lambda data: data).prefetch(
            CharacterEntity.trait,
            CharacterEntity.speak,
            CharacterEntity.distinctive
        )[:]

        # 转换为 ResponseCharacterDto 列表
        result = []
        for character in characters:
            # 转换 traits
            traits = [
                TraitDto(label=t.label, description=t.description)
                for t in character.trait
            ] if character.trait else None

            # 转换 speakings
            speakings = [
                SpeakingDto(role=s.role, content=s.content, reply=s.reply)
                for s in character.speak
            ] if character.speak else None

            # 转换 distinctive
            distinctive = [
                DistinctiveDto(name=d.name, content=d.content)
                for d in character.distinctive
            ] if character.distinctive else None

            # 创建 ResponseCharacterDto 实例
            character_dto = ResponseCharacterDto(
                id=character.character_id,
                avatar=character.avatar or '',
                name=character.name,
                description=character.description or '',
                background_story=character.background_story or '',
                traits=traits,
                speakings=speakings,
                distinct=distinctive
            )
            result.append(character_dto)

        return result


    @db_session
    def delete_character_by_id(self, character_id: int) -> bool:
        character = CharacterEntity.get(character_id=character_id)

        if not character:
            logging.warning(f"角色id: {character_id} 不存在")
            raise NotFoundError(entity_id=character_id)

        character.delete()
        logging.info(f"删除角色id为{character_id}成功")
        return True

    @db_session
    def select_character_by_id(self, character_id: int) -> ResponseCharacterDto:
        """
                根据 character_id 查询角色及其关联数据，并返回 ResponseCharacterDto
                """
        try:
            # 查询角色并预加载关联数据
            character = CharacterEntity.select(lambda data: data.character_id == character_id).prefetch(
                CharacterEntity.trait,
                CharacterEntity.speak,
                CharacterEntity.distinctive
            ).get()

            if not character:
                logging.warning(f"角色 ID {character_id} 不存在")
                raise NotFoundError(character_id)

            # 转换为 ResponseCharacterDto
            return ResponseCharacterDto(
                id=character.character_id,
                avatar=character.avatar or '',
                name=character.name,
                description=character.description or '',
                background_story=character.background_story or '',
                traits=[
                    TraitDto(label=t.label, description=t.description)
                    for t in character.trait
                ],
                speakings=[
                    SpeakingDto(role=s.role, content=s.content, reply=s.reply)
                    for s in character.speak
                ],
                distinct=[
                    DistinctiveDto(name=d.name, content=d.content)
                    for d in character.distinctive
                ]
            )

        except Exception as e:
            logging.error(f"查询角色 ID {character_id} 失败: {str(e)}")
            raise DatabaseError(str(e))


if __name__ == '__main__':
    generate_table_mapping()
    character_mapper = CharacterMapper()
    # character_test = CreateCharacterDto(name="567", distinct=[DistinctiveDto(name="name", content="content"), DistinctiveDto(name="name2", content="content2")])
    # character_mapper.create_character(character_test)
    # c = character_mapper.select_character_by_id(1)
    # print(c.traits[0].description)
    characters = character_mapper.get_all_characters()
    print(characters)
    # character_mapper.delete_character_by_id(2)
