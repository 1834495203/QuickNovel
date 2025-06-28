from fastapi import APIRouter, Depends

from core.entity.dto.SceneDto import CreateSceneDto
from core.mapper.SceneMapper import SceneMapper
from core.service.SceneService import SceneService
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)

scene_router = APIRouter(prefix="/api/scene", tags=["scene"])

def get_scene_service():
    return SceneService(SceneMapper())


@scene_router.post("/")
def create_scene(
        scene: CreateSceneDto,
        scene_service: SceneService = Depends(get_scene_service)):
    return scene_service.create_scene(scene)