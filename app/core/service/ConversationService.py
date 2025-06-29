from datetime import datetime
from typing import List

from core.entity.ResponseEntity import ResponseModel, success
from core.entity.dto.ConversationDto import CreateConversationDto, ResponseConversationDto
from core.mapper.ConversationMapper import ConversationMapperInterface
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class ConversationService:
    def __init__(self, conversation_mapper: ConversationMapperInterface):
        self.conversation_mapper = conversation_mapper

    def create_conversation(self, conversation: CreateConversationDto) -> ResponseModel:
        conversation.create_time = datetime.now()
        conversation_id = self.conversation_mapper.create_conversation(conversation)

        # 记录日志
        logging.info(f"创建角对话成功，id为:{conversation_id}")
        return success(message=f"创建角对话成功，id为:{conversation_id}")

    def get_conversation_by_scene_id(self, scene_id: str) -> ResponseModel[List[ResponseConversationDto]]:
        conversations = self.conversation_mapper.get_conversation_by_scene_id(scene_id)

        if not conversations or conversations == []:
            logging.warning(f"情景 ID 为{scene_id}的对话为空")

        logging.info(f"获取情景 ID 为{scene_id}的对话成功, 对话数量为{len(conversations)}")

        return success(message=f"情景 ID 为{scene_id}的对话为空", data=conversations)
