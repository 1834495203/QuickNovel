from abc import ABC
from datetime import datetime

from pony.orm import commit, db_session

from core.entity.dto.SceneDto import CreateSceneDto
from core.entity.po.NovelEntity import SceneEntity
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import DatabaseError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class SceneMapperInterface(ABC):

    def create_scene(self, scene: CreateSceneDto) -> int:
        raise NotImplementedError()


class SceneMapper(SceneMapperInterface):

    @db_session
    def create_scene(self, scene: CreateSceneDto) -> int:
        try:
            s = SceneEntity(
                scene_name=scene.scene_name,
                scene_desc=scene.scene_desc,
                create_time=scene.create_time,
                parent=scene.parent,
                chapter=scene.chapter,
            )

            commit()
            return s.scene_id
        except Exception as e:
            logging.error(f"创建情景{scene.scene_name}失败，{e}")
            raise DatabaseError(message=f"创建情景{scene.scene_name}失败，{e}")


if __name__ == '__main__':
    generate_table_mapping()
    scene_mapper = SceneMapper()
    scene_mapper.create_scene(
        CreateSceneDto(
            scene_name="酒店场景-夜晚",
            scene_desc="夏日夜晚的凉风吹散了白天的热气，清妍身穿浅色连衣裙，肉色丝袜和玛丽珍鞋赴约。",
            create_time=datetime.now(),
            chapter=1))
