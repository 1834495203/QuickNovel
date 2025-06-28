from datetime import datetime

from core.entity.ResponseEntity import success, ResponseModel
from core.entity.dto.ChapterDto import CreateChapterDto
from core.mapper.ChapterMapper import ChapterMapperInterface
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)

class ChapterService:
    def __init__(self, chapter_mapper: ChapterMapperInterface):
        self.chapter_mapper = chapter_mapper

    def create_chapter(self, chapter: CreateChapterDto) -> ResponseModel:
        chapter.create_time = datetime.now()
        chapter_id = self.chapter_mapper.create_chapter(chapter)
        logging.info(f"创建章节{chapter.chapter_title}成功，章节ID为{chapter_id}")
        return success(message=f"创建章节{chapter.chapter_title}成功，章节ID为{chapter_id}")

