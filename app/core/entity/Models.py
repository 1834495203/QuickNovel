# 定义聊天内容类
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any

from core.entity.CharacterCard import UserCard, CharacterCard


class ChatMessageType(Enum):
    # 系统级别的prompt
    SYSTEM_PROMPT = 0
    # 角色的信息
    CHARACTER_TYPE = 1
    # 用户的信息
    USER_TYPE = 2
    # 一般的用户发的信息
    NORMAL_MESSAGE_USER = 3
    # 一般的llm回复的消息
    NORMAL_MESSAGE_ASSISTANT = 4
    # 旁白
    ASIDE_MESSAGE = 5
    # 联网搜索的信息
    ONLINE_MESSAGE = 6


# 最必要的信息，存入数据库的字段
class ChatContentMain:
    def __init__(self, cid: int,
                 role: str,
                 content: str,
                 chat_type: ChatMessageType,
                 user: UserCard,
                 character: CharacterCard,
                 reasoning_content: Optional[str] = None,
                 create_time: datetime = None):
        self.cid = cid                                       # 对话唯一id
        self.role = role                                     # 角色
        self.content = content                               # 消息
        self.chat_type = chat_type                           # 对话类型
        self.user = user                                     # 用户角色
        self.character = character                           # 对话角色
        self.reasoning_content = reasoning_content           # 推理
        self.create_time = create_time


# 原始的 ChatContent 类，添加 token 相关字段
class ChatContent(ChatContentMain):
    def __init__(self,
                 role: str,
                 content: Any,
                 cid: int,
                 user: UserCard,
                 character: CharacterCard,
                 create_time: datetime = None,
                 reasoning_content: Optional[str] = None,
                 tool_calls: Optional[List[Any]] = None,
                 name: Optional[str] = None,
                 tool_call_id: Optional[str] = None,
                 finish_reason: Optional[str] = None,
                 message: Optional[Any] = None,
                 prompt_tokens: Optional[int] = None,
                 completion_tokens: Optional[int] = None,
                 total_tokens: Optional[int] = None,
                 chat_type: Optional[ChatMessageType] = None,
                 user_card: Optional[UserCard] = None,
                 merge_count: int = 0):
        # 对话的角色
        super().__init__(cid, role, content, chat_type, user, character, reasoning_content, create_time)
        self.role = role

        # 消息的具体内容，和模型推理部分
        self.content = content
        self.reasoning_content = reasoning_content

        # openai接口返回的字段
        self.tool_calls = tool_calls
        self.name = name
        self.tool_call_id = tool_call_id
        self.finish_reason = finish_reason
        self.message = message

        # token相关参数
        self.prompt_tokens = prompt_tokens                   # 提示token
        self.completion_tokens = completion_tokens           # 完成token
        self.total_tokens = total_tokens                     # 总token

        # 该对话的类型
        self.chat_type = chat_type

        # 该对话发起的用户的具体信息
        self.user_card = user_card

        # 对话被合并的次数
        self.merge_count = merge_count

        self.create_time = create_time

    def __str__(self):
        role_map = {
            "user": "用户",
            "assistant": "助手",
            "system": "系统"
        }
        role_str = role_map.get(self.role, self.role)
        name_str = f" ({self.name})" if self.name else ""
        content = self.content if self.content else "\n没有输出内容"
        reasoning = f"\n[推理]: {self.reasoning_content}" if self.reasoning_content else "\n没有输出推理"
        tool_info = f"\n[工具调用]: {self.tool_calls}" if self.tool_calls else "\n没有工具调用"
        tool_id = f"\n[工具调用ID]: {self.tool_call_id}" if self.tool_call_id else "\n没有工具调用id"
        token_info = f"\n[Token使用]: 提示={self.prompt_tokens}, 完成={self.completion_tokens}, 总计={self.total_tokens}" \
            if self.total_tokens is not None else "\n没有token数据"

        return f"{role_str}{name_str}: {content}{reasoning}{tool_info}{tool_id}{token_info}"


# 将维护一个单次会话列表
class ChatAbstract(object):
    def __init__(self, messages: Optional[List[ChatContent]] = None):
        self.messages: List[ChatContent] = messages or []

    def get_messages_by_type(self, message_type: ChatMessageType) -> List[ChatContent]:
        raise NotImplementedError()

    def get_messages_by_types(self, message_types: List[ChatMessageType]) -> List[ChatContent]:
        raise NotImplementedError()

    def has_message_type(self, message_type: ChatMessageType) -> bool:
        raise NotImplementedError()

    def count_by_type(self, message_type: ChatMessageType) -> int:
        raise NotImplementedError()

    def merge_messages(self, threshold: int, core_count: int, kk: int) -> int:
        raise NotImplementedError()

    def append_message(self, message: ChatContent) -> bool:
        raise NotImplementedError()
