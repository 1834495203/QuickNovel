from fastapi import APIRouter, Depends, Request

from core.entity.dto.ConversationDto import CreateConversationDto
from core.mapper.CharacterMapper import CharacterMapper
from core.mapper.CharacterNovelMapper import CharacterNovelMapper
from core.mapper.ConversationMapper import ConversationMapper
from core.mapper.NovelMapper import NovelMapper
from core.service.ConversationService import ConversationService
from core.service.ProviderService import ProviderService
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)

conversation_router = APIRouter(prefix="/api/conversation", tags=["Conversation"])


def get_conversation_service():
    return ConversationService(ConversationMapper(), ProviderService(
        novel_mapper=NovelMapper(),
        character_novel_mapper=CharacterNovelMapper(
            character_mapper=CharacterMapper(),
            novel_mapper=NovelMapper(),
        ),
        model="deepseek-chat",
        streaming=True))


@conversation_router.post("/")
def create_conversation(
        request: Request,
        conversation: CreateConversationDto,
        conversation_service: ConversationService = Depends(get_conversation_service)):
    """
    创建对话内容
    :param request:
    :param conversation: 创建的对话
    :param conversation_service: 对话的服务
    :return: resp
    """
    return conversation_service.create_conversation(request, conversation)


@conversation_router.get("/{scene_id}")
def get_conversation_by_scene_id(
        scene_id: str,
        conversation_service: ConversationService = Depends(get_conversation_service)):
    """
    根据scene id 获取对应的对话内容
    :param scene_id: 情景id
    :param conversation_service: 对话的服务
    :return: 对话列表
    """
    return conversation_service.get_conversation_by_scene_id(scene_id)
