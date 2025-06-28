from datetime import datetime
from typing import List

from core.entity.ResponseEntity import success, ResponseModel
from core.entity.dto.NovelDto import CreateNovelDto, ResponseAllNovelDto, ResponseNovelDto
from core.mapper.NovelMapper import NovelMapperInterface
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class NovelService:
    def __init__(self, novel_mapper: NovelMapperInterface):
        self.novel_mapper = novel_mapper

    def create_novel(self, novel: CreateNovelDto) -> ResponseModel:
        novel.create_time = datetime.now()
        novel_id = self.novel_mapper.create_novel(novel)
        logging.info(f"创建小说{novel.novel_name}成功，小说id为{novel_id}")
        return success(message=f"创建小说{novel.novel_name}成功，小说id为{novel_id}")

    def get_novel_by_id(self, novel_id: int) -> ResponseModel[ResponseAllNovelDto]:
        novel = self.novel_mapper.get_novel_by_id(novel_id)
        logging.info(f"获取小说 {novel.novel_name} 成功")
        return success(data=novel, message=f"获取小说 {novel.novel_name} 成功")

    def get_all_novels(self) -> ResponseModel[List[ResponseNovelDto]]:
        novels = self.novel_mapper.get_all_novels()
        logging.info(f"获取全部小说成功，数量为 {len(novels)}")
        return success(data=novels, message=f"获取全部小说成功，数量为 {len(novels)}")
