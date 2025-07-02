from abc import ABC
from typing import List

from pony.orm import commit, db_session

from core.entity.dto.WorldDto import CreateWorldDto, ResponseWorldDto, ResponseAllWorldDetailDto, ResponseWorldDetailDto
from core.entity.po.WorldEntity import WorldEntity
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import DatabaseError, NotFoundError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class WorldMapperInterface(ABC):

    def create_world(self, world: CreateWorldDto) -> int:
        raise NotImplementedError()

    def get_all_worlds(self) -> List[ResponseWorldDto]:
        raise NotImplementedError()

    def get_world_by_id(self, world_id: int) -> ResponseAllWorldDetailDto:
        raise NotImplementedError()


class WorldMapper(WorldMapperInterface):

    @db_session
    def create_world(self, world: CreateWorldDto) -> int:
        try:
            world = WorldEntity(
                world_name=world.world_name,
                world_desc=world.world_desc,
                create_time=world.create_time)

            commit()
            return world.world_id
        except Exception as e:
            logging.error(f"创建世界观失败, {str(e)}")
            raise DatabaseError(f"创建世界观失败, {str(e)}")

    @db_session
    def get_all_worlds(self) -> List[ResponseWorldDto]:
        try:
            worlds = WorldEntity.select(lambda data: data)[:]

            result: List[ResponseWorldDto] = []
            for world in worlds:
                result.append(ResponseWorldDto(
                    world_id=world.world_id,
                    world_name=world.world_name,
                    world_desc=world.world_desc,
                    create_time=world.create_time
                ))

            return result
        except Exception as e:
            logging.error(f"获取全部世界观失败, {str(e)}")
            raise DatabaseError(f"获取全部世界观失败, {str(e)}")

    @db_session
    def get_world_by_id(self, world_id: int) -> ResponseAllWorldDetailDto:
        world = WorldEntity.select(lambda data: data.world_id == world_id).prefetch(
            WorldEntity.world_detail
        ).first()

        if not world:
            logging.error(f"世界观 ID {world_id} 不存在")
            raise NotFoundError(world_id)

        try:
            world_detail_list = [
                ResponseWorldDetailDto(
                    id=detail.id,
                    world_detail_name=detail.world_detail_name,
                    world_detail_desc=detail.world_detail_desc,
                    world=detail.world.world_id)for detail in world.world_detail
            ]

            return ResponseAllWorldDetailDto(
                world_id=world.world_id,
                world_name=world.world_name,
                world_desc=world.world_desc,
                create_time=world.create_time,
                world_details=world_detail_list
            )
        except Exception as e:
            logging.error(f"获取世界观 ID {world_id} 失败，{str(e)}")
            raise DatabaseError(f"获取世界观 ID {world_id} 失败，{str(e)}")



if __name__ == '__main__':
    generate_table_mapping()
    world_mapper = WorldMapper()
    ws = world_mapper.get_world_by_id(1)
    print(ws)