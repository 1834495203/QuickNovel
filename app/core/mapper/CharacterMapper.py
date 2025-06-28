import os
from abc import ABC

from pony.orm import db_session, commit

from core.entity.dto.CharacterDto import *
from core.entity.po.CharacterEntity import *
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import NotFoundError, DatabaseError, FileError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


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

    def update_character(self, character: UpdateCharacterDto) -> bool:
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

        # 处理 trait
        if character.trait:
            for trait_dto in character.trait:
                trait = Trait(
                    label=trait_dto.label,
                    description=trait_dto.description,
                    character=c
                )
                c.trait.add(trait)

        # 处理 speak
        if character.speak:
            for speaking_dto in character.speak:
                speaking = Speak(
                    role=speaking_dto.role,
                    content=speaking_dto.content,
                    reply=speaking_dto.reply,
                    character=c
                )
                c.speak.add(speaking)

        # 处理 distinctive
        if character.distinctive:
            for distinctive_dto in character.distinctive:
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
        character = self._select_character_by_id(character_id)
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
    def update_character(self, update_character: CharacterDto):
        character_id = update_character.id
        # 查询角色并预加载关联数据
        character = self._select_character_by_id(character_id)

        # 更新角色基本信息
        character.avatar = update_character.avatar
        character.name = update_character.name
        character.description = update_character.description
        character.background_story = update_character.background_story

        # 更新 Trait（性格特征）
        if update_character.trait is not None or update_character.trait == []:
            # 删除现有的 trait
            Trait.select(lambda data: data.character.character_id == character_id).delete()
            # 添加新的 trait
            for trait_dto in update_character.trait:
                Trait(
                    label=trait_dto.label,
                    description=trait_dto.description,
                    character=character
                )

        # 更新 Speak（说话方式）
        if update_character.speak is not None or update_character.speak == []:
            # 删除现有的 speaks
            Speak.select(lambda data: data.character.character_id == character_id).delete()
            # 添加新的 speaks
            for speaking_dto in update_character.speak:
                Speak(
                    role=speaking_dto.role,
                    content=speaking_dto.content,
                    reply=speaking_dto.reply,
                    character=character
                )

        # 更新 Distinctive（自定义字段）
        if update_character.distinctive is not None or update_character.distinctive == []:
            # 删除现有的 distinctive
            Distinctive.select(lambda data: data.character.character_id == character_id).delete()
            # 添加新的 distinctive
            for distinctive_dto in update_character.distinctive:
                Distinctive(
                    name=distinctive_dto.name,
                    content=distinctive_dto.content,
                    character=character
                )

        commit()
        return True


    @db_session
    def get_all_characters(self) -> List[ResponseCharacterDto]:
        # 查询所有 CharacterEntity 记录
        characters = CharacterEntity.select(lambda data: data).prefetch(
            CharacterEntity.trait,
            CharacterEntity.speak,
            CharacterEntity.distinctive
        )[:]

        logging.info("获取所有角色成功")

        # 转换为 ResponseCharacterDto 列表
        result = []
        for character in characters:
            # 转换 trait
            traits = [
                TraitDto(label=t.label, description=t.description)
                for t in character.trait
            ] if character.trait else []

            # 转换 speak
            speakings = [
                SpeakingDto(role=s.role, content=s.content, reply=s.reply)
                for s in character.speak
            ] if character.speak else []

            # 转换 distinctive
            distinctive = [
                DistinctiveDto(name=d.name, content=d.content)
                for d in character.distinctive
            ] if character.distinctive else []

            # 创建 ResponseCharacterDto 实例
            character_dto = ResponseCharacterDto(
                id=character.character_id,
                avatar=character.avatar or '',
                name=character.name,
                description=character.description or '',
                background_story=character.background_story or '',
                trait=traits,
                speak=speakings,
                distinctive=distinctive
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
    def _select_character_by_id(self, character_id: int) -> CharacterEntity:
        # 查询角色并预加载关联数据
        character = CharacterEntity.select(lambda data: data.character_id == character_id).prefetch(
            CharacterEntity.trait,
            CharacterEntity.speak,
            CharacterEntity.distinctive
        ).get()

        if not character:
            logging.warning(f"角色 ID {character_id} 不存在")
            raise NotFoundError(character_id)
        return character

    @db_session
    def select_character_by_id(self, character_id: int) -> ResponseCharacterDto:
        """
                根据 character_id 查询角色及其关联数据，并返回 ResponseCharacterDto
                """
        try:
            # 查询角色并预加载关联数据
            character = self._select_character_by_id(character_id)

            # 转换为 ResponseCharacterDto
            return ResponseCharacterDto(
                id=character.character_id,
                avatar=character.avatar or '',
                name=character.name,
                description=character.description or '',
                background_story=character.background_story or '',
                trait=[
                    TraitDto(label=t.label, description=t.description)
                    for t in character.trait
                ],
                speak=[
                    SpeakingDto(role=s.role, content=s.content, reply=s.reply)
                    for s in character.speak
                ],
                distinctive=[
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
    select_character = character_mapper.select_character_by_id(1)

    select_character.avatar = "avatar"
    select_character.speak = [SpeakingDto(role="role", content="content", reply="reply")]
    select_character.trait = []

    character_mapper.update_character(select_character)
