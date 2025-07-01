from abc import ABC
from datetime import datetime

from pony.orm import commit, db_session

from core.entity.dto.ChapterDto import CreateChapterDto
from core.entity.po.NovelEntity import ChapterEntity
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import DatabaseError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class ChapterMapperInterface(ABC):

    def create_chapter(self, chapter: CreateChapterDto) -> int:
        raise NotImplementedError()


class ChapterMapper(ChapterMapperInterface):

    @db_session
    def create_chapter(self, chapter: CreateChapterDto) -> int:
        try:
            c = ChapterEntity(
                chapter_number=chapter.chapter_number,
                chapter_title=chapter.chapter_title,
                chapter_desc=chapter.chapter_desc,
                create_time=chapter.create_time,
                parent=chapter.parent,
                novel=chapter.novel,
            )

            commit()
            return c.chapter_id
        except Exception as e:
            logging.error(f"创建章节{chapter.chapter_title}失败, {e}")
            raise DatabaseError(message=f"创建章节{chapter.chapter_title}失败, {e}")


if __name__ == '__main__':
    generate_table_mapping()
    mapper = ChapterMapper()
    mapper.create_chapter(CreateChapterDto(
        chapter_title="梦开始的地方",
        chapter_desc="主角名为裴橘(女)，是一位普通的大学生，她很善良，在福利院生活，但是总是被欺负。",
        create_time=datetime.now(),
        chapter_number=1,
        novel=1))
