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
            # 在这里对获取到的集合进行排序，这是最通用和显式的方式
            # 即使你在实体中定义了 order_by，你也可以在这里覆盖它
            sorted_chapters = sorted(novel.chapter, key=lambda ch: ch.chapter_number,
                                     reverse=False)  # 假设按 chapter_number 升序

            chapters_dto = []
            for chapter in sorted_chapters:
                sorted_scenes = sorted(chapter.scene, key=lambda s: s.scene_id, reverse=False)  # 假设按 create_time 降序

                scenes_dto = []
                for scene in sorted_scenes:
                    sorted_conversations = sorted(scene.conversation, key=lambda conv: conv.conversation_id,
                                                  reverse=True)  # 假设按 create_time 降序

                    conversations_dto = [
                        ResponseConversationDto(
                            conversation_id=conv.conversation_id,
                            role=conv.role,
                            sender_character=conv.sender_character,
                            receiver_character=conv.receiver_character,
                            content=conv.content,
                            create_time=conv.create_time,
                            parent=conv.parent,
                            scene=conv.scene.scene_id
                        ) for conv in sorted_conversations
                    ]
                    scenes_dto.append(
                        ResponseSceneDto(
                            scene_id=scene.scene_id,
                            scene_name=scene.scene_name,
                            scene_desc=scene.scene_desc,
                            create_time=scene.create_time,
                            parent=scene.parent,
                            chapter=scene.chapter.chapter_id,
                            conversation=conversations_dto
                        )
                    )
                chapters_dto.append(
                    ResponseAllChapterDto(
                        chapter_id=chapter.chapter_id,
                        chapter_number=chapter.chapter_number,
                        chapter_desc=chapter.chapter_desc,
                        chapter_title=chapter.chapter_title,
                        create_time=chapter.create_time,
                        parent=chapter.parent,
                        novel=chapter.novel.novel_id,
                        scene=scenes_dto
                    )
                )

            return ResponseAllNovelDto(
                novel_id=novel.novel_id,
                novel_name=novel.novel_name,
                novel_desc=novel.novel_desc,
                create_time=novel.create_time,
                chapter=chapters_dto
            )
        except Exception as e:
            logging.error(f"获取小说 ID {novel_id}失败，{str(e)}")
            raise DatabaseError(str(e))


if __name__ == '__main__':
    generate_table_mapping()
    mapper = NovelMapper()
    novel = mapper.get_novel_by_id(1)
    print(novel)
