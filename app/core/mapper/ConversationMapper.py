from abc import ABC
from datetime import datetime
from typing import List

from pony.orm import commit, db_session

from core.entity.dto.ConversationDto import CreateConversationDto, ResponseConversationDto
from core.entity.po.ConversationEntity import ConversationEntity
from core.mapper.config.CreateDatabase import generate_table_mapping
from core.utils.CustomizeException import DatabaseError
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class ConversationMapperInterface(ABC):

    def create_conversation(self, conversation: CreateConversationDto) -> int:
        raise NotImplementedError()

    def get_conversation_by_scene_id(self, scene_id: str) -> List[ResponseConversationDto]:
        raise NotImplementedError()


class ConversationMapper(ConversationMapperInterface):

    @db_session
    def create_conversation(self, conversation: CreateConversationDto) -> int:
        try:
            c = ConversationEntity(
                role=conversation.role,
                sender_character=conversation.sender_character,
                receiver_character=conversation.receiver_character,
                content=conversation.content,
                create_time=conversation.create_time,
                parent=conversation.parent,
                scene=conversation.scene)

            # 提交事务
            commit()
            return c.conversation_id
        except Exception as e:
            logging.error(f"创建对话失败，{str(e)}")
            raise DatabaseError(str(e))

    @db_session
    def get_conversation_by_scene_id(self, scene_id: str) -> List[ResponseConversationDto]:
        try:
            conversations = ConversationEntity.select(lambda data: data.scene.scene_id == scene_id)[:]

            result: List[ResponseConversationDto] = []
            for conversation in conversations:
                result.append(ResponseConversationDto(
                    conversation_id=conversation.conversation_id,
                    role=conversation.role,
                    sender_character=conversation.sender_character,
                    receiver_character=conversation.receiver_character,
                    content=conversation.content,
                    create_time=conversation.create_time,
                    parent=conversation.parent,
                    scene=conversation.scene))
            return result
        except Exception as e:
            logging.error(f"获取情景 ID 为{scene_id}的对话失败，{str(e)}")
            raise DatabaseError(str(e))


if __name__ == '__main__':
    generate_table_mapping()
    conversation_mapper = ConversationMapper()
    conversation_mapper.create_conversation(conversation=CreateConversationDto(
        role="role",
        content="content",
        create_time=datetime.now(),
        scene=1
    ))
