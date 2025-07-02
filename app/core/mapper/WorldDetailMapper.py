from abc import ABC

from pony.orm import commit, db_session

from core.entity.dto.WorldDto import CreateWorldDetailDto
from core.entity.po.WorldEntity import WorldDetailEntity
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import DatabaseError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class WorldDetailMapperInterface(ABC):

    def create_world_detail(self, world_detail: CreateWorldDetailDto):
        raise NotImplementedError()


class WorldDetailMapper(WorldDetailMapperInterface):

    @db_session
    def create_world_detail(self, world_detail: CreateWorldDetailDto):
        try:
            world_detail = WorldDetailEntity(
                world_detail_name=world_detail.world_detail_name,
                world_detail_desc=world_detail.world_detail_desc,
                world=world_detail.world)

            commit()
            return world_detail.id
        except Exception as e:
            logging.error(f"创建详细世界观失败，{str(e)}")
            raise DatabaseError(f"创建详细世界观失败，{str(e)}")


if __name__ == '__main__':
    generate_table_mapping()
    world_detail_mapper = WorldDetailMapper()
