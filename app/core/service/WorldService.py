from datetime import datetime
from typing import List

from core.entity.ResponseEntity import ResponseModel, success
from core.entity.dto.WorldDto import CreateWorldDto, ResponseWorldDto, ResponseAllWorldDetailDto
from core.mapper.WorldMapper import WorldMapperInterface
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class WorldService:
    def __init__(self, world_mapper: WorldMapperInterface):
        self.world_mapper = world_mapper

    def create_world(self, world: CreateWorldDto) -> ResponseModel:
        world.create_time = datetime.now()
        world_id = self.world_mapper.create_world(world)

        logging.info(f"创建世界观 {world.world_name} 成功，ID 为 {world_id}")
        return success(message=f"创建世界观 {world.world_name} 成功，ID 为 {world_id}")

    def get_all_worlds(self) -> ResponseModel[List[ResponseWorldDto]]:
        worlds = self.world_mapper.get_all_worlds()
        logging.info(f"获取全部世界成功，数量为 {len(worlds)}")
        return success(data=worlds, message=f"获取全部世界成功，数量为 {len(worlds)}")

    def get_world_by_id(self, world_id: int) -> ResponseModel[ResponseAllWorldDetailDto]:
        all_world = self.world_mapper.get_world_by_id(world_id)
        logging.info(f"获取 ID 为 {world_id} 的世界观成功")
        return success(message=f"获取 ID 为 {world_id} 的世界观成功", data=all_world)
