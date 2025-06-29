from abc import ABC
from typing import List

from pony.orm import db_session, commit

from core.entity.dto.ChapterDto import ResponseAllChapterDto
from core.entity.dto.ConversationDto import ResponseConversationDto
from core.entity.dto.NovelDto import CreateNovelDto, ResponseNovelDto, ResponseAllNovelDto
from core.entity.dto.SceneDto import ResponseSceneDto
from core.entity.po.NovelEntity import NovelEntity, ChapterEntity, SceneEntity
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import DatabaseError, NotFoundError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class NovelMapperInterface(ABC):

    def create_novel(self, novel: CreateNovelDto) -> int:
        raise NotImplementedError()

    def get_all_novels(self) -> List[ResponseNovelDto]:
        raise NotImplementedError()

    def get_novel_by_id(self, novel_id: int) -> ResponseAllNovelDto:
        raise NotImplementedError()


class NovelMapper(NovelMapperInterface):

    @db_session
    def create_novel(self, novel: CreateNovelDto) -> int:
        try:
            n = NovelEntity(
                novel_name=novel.novel_name,
                novel_desc=novel.novel_desc,
                create_time=novel.create_time,
            )

            commit()
        except Exception as e:
            logging.error(f"创建小说 ID {novel.novel_name} 失败: {str(e)}")
            raise DatabaseError(str(e))
        return n.novel_id

    @db_session
    def get_all_novels(self) -> List[ResponseNovelDto]:
        try:
            novels = NovelEntity.select(lambda data: data)[:]
            logging.info("获取所有角色成功")

            result: List[ResponseNovelDto] = []

            for novel in novels:
                # 转换信息
                novel_dto = ResponseNovelDto(
                    novel_id=novel.novel_id,
                    novel_name=novel.novel_name,
                    novel_desc=novel.novel_desc,
                    create_time=novel.create_time,
                )
                result.append(novel_dto)

            return result
        except Exception as e:
            logging.error(f"获取全部小说信息失败, {str(e)}")
            raise DatabaseError(str(e))

    @db_session
    def get_novel_by_id(self, novel_id: int) -> ResponseAllNovelDto:
        novel = NovelEntity.select(lambda data: data.novel_id == novel_id).prefetch(
            NovelEntity.chapter,
            ChapterEntity.scene,
            SceneEntity.conversation
        ).first()

        if not novel:
            logging.warning(f"小说 ID {novel_id} 不存在")
            raise NotFoundError(novel_id)

        try:
            # 构建章节数据
            chapters = [
                ResponseAllChapterDto(
                    chapter_id=chapter.chapter_id,
                    chapter_number=chapter.chapter_number,
                    chapter_desc=chapter.chapter_desc,
                    chapter_title=chapter.chapter_title,
                    create_time=chapter.create_time,
                    parent=chapter.parent,
                    novel=chapter.novel.novel_id,
                    scene=[
                        ResponseSceneDto(
                            scene_id=scene.scene_id,
                            scene_name=scene.scene_name,
                            scene_desc=scene.scene_desc,
                            create_time=scene.create_time,
                            parent=scene.parent,
                            chapter=scene.chapter.chapter_id,
                            conversation=[
                                ResponseConversationDto(
                                    conversation_id=conv.conversation_id,
                                    role=conv.role,
                                    sender_character=conv.sender_character,
                                    receiver_character=conv.receiver_character,
                                    content=conv.content,
                                    create_time=conv.create_time,
                                    parent=conv.parent,
                                    scene=conv.scene.scene_id
                                )for conv in scene.conversation
                            ]
                        )for scene in chapter.scene
                    ]
                )for chapter in novel.chapter
            ]

            return ResponseAllNovelDto(
                novel_id=novel.novel_id,
                novel_name=novel.novel_name,
                novel_desc=novel.novel_desc,
                create_time=novel.create_time,
                chapter=chapters
            )
        except Exception as e:
            logging.error(f"获取小说 ID {novel_id}失败，{str(e)}")
            raise DatabaseError(str(e))


if __name__ == '__main__':
    generate_table_mapping()
    mapper = NovelMapper()
    novel = mapper.get_novel_by_id(1)
    print(novel)
