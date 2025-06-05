from typing import Optional, List

from core.entity.Conversation import ChatMessageType, ChatContentBase, ChatContentMain, ChatContent
from core.service.ConvChatService import ChatContentService


def get_chat_content_service():
    return ChatContentService()

# 原始的 Chat 类，应该维护的是单次对话的上下文
class Chat:
    def __init__(self,
                 messages: Optional[List[ChatContent]] = None,
                 conversation_id: Optional[int] = None,
                 chat_content_service: ChatContentService = get_chat_content_service()):
        self.messages: List[ChatContent] = messages or []
        self.chat_content_service: ChatContentService = chat_content_service
        self.conversation_id = conversation_id

        if self.conversation_id is not None:
            self.chat_content_service.set_conversation_id(self.conversation_id)

    def set_message(self, message: ChatContentBase | ChatContent | ChatContentMain, is_save=False):
        if is_save:
            self.chat_content_service.create(message.to_chat_content_main())
        else:
            self.messages.append(message.to_chat_content())

    def get_messages(self):
        msg_in_jsonl = self.chat_content_service.get_by_conversation_id(self.conversation_id).data
        if len(msg_in_jsonl) != 0:
            for msg in msg_in_jsonl:
                self.messages.append(msg.to_chat_content())
        if len(self.messages) == 0:
            raise ValueError("没有对话内容")
        return self.messages

    def get_messages_by_type(self, message_type: ChatMessageType) -> List[ChatContent]:
        """
        根据指定的 ChatMessageType 返回对应类型的消息列表

        Args:
            message_type: 要筛选的消息类型

        Returns:
            List[ChatContent]: 指定类型的消息列表
        """
        return [message for message in self.messages if message.chat_type == message_type]

    def get_messages_by_types(self, message_types: List[ChatMessageType]) -> List[ChatContent]:
        """
        根据指定的多个 ChatMessageType 返回对应类型的消息列表

        Args:
            message_types: 要筛选的消息类型列表

        Returns:
            List[ChatContent]: 符合指定类型之一的消息列表
        """
        return [message for message in self.messages if message.chat_type in message_types]

    def has_message_type(self, message_type: ChatMessageType) -> bool:
        """
        检查是否存在指定类型的消息

        Args:
            message_type: 要检查的消息类型

        Returns:
            bool: 如果存在指定类型的消息则返回 True，否则返回 False
        """
        return any(message.chat_type == message_type for message in self.messages)

    def count_by_type(self, message_type: ChatMessageType) -> int:
        """
        统计指定类型消息的数量

        Args:
            message_type: 要统计的消息类型

        Returns:
            int: 指定类型的消息数量
        """
        return sum(1 for message in self.messages if message.chat_type == message_type)
