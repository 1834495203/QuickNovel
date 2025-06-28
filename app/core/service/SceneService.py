from datetime import datetime

from core.entity.ResponseEntity import success, ResponseModel
from core.entity.dto.SceneDto import CreateSceneDto
from core.mapper.SceneMapper import SceneMapperInterface
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class SceneService:
    def __init__(self, scene_mapper: SceneMapperInterface):
        self.scene_mapper = scene_mapper

    def create_scene(self, scene: CreateSceneDto) -> ResponseModel:
        scene.create_time = datetime.now()
        scene_id = self.scene_mapper.create_scene(scene)
        return success(message=f"创建情景{scene.scene_name}成功，ID为{scene_id}")