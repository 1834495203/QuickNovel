from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel

from core.entity.CharacterCard import CharacterCard


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
    # 流式传输的数据
    NORMAL_MESSAGE_ASSISTANT_PART = 7
    # 排除的数据，报错
    EXCLUDE_MESSAGE_EXCEPTION = 8


class Conversation(BaseModel):
    root_conversation_id: int                        # 表示上一个父节点的会话id -1表示根节点
    conversation_id: Optional[int]                   # 会话唯一id
    character_id: int = None                         # 对话角色id
    create_time: Optional[float] = None              # 创建时间戳


# 最基础对话实体类
class ChatContentBase(BaseModel):
    role: str                                        # 角色
    content: str                                     # 消息
    chat_type: ChatMessageType                       # 对话类型
    reasoning_content: Optional[str] = None          # 推理内容

    # 转为临时对象
    def to_chat_content(self, *args, **kwargs):
        return self

    # 转为可存储对象
    def to_chat_content_main(self, *args, **kwargs):
        return self


# 定义 API 聊天模型，存入数据库
class ChatContentMain(ChatContentBase):
    cid: str                                         # 对话唯一id
    conversation_id: Optional[int]                   # 会话唯一id
    user_role_id: Optional[int]                      # 单次对话用户唯一id
    create_time: Optional[float] = None              # 时间

    def to_chat_content(self):
        return ChatContent(**self.model_dump(exclude={"cid", "conversation_id", "user_role_id", "create_time"}))


# 使用于llm的对话信息
class ChatContent(ChatContentBase):
    finish_reason: Optional[str] = None     # 完成原因
    message: Optional[Any] = None           # 消息对象

    # 转为可存储对象
    def to_chat_content_main(self, cid: str,
                             conversation_id: Optional[int],
                             user_role_id: Optional[int],
                             create_time: Optional[float] = None):
        return ChatContentMain(**self.model_dump(exclude={"finish_reason", "message"}),
                               cid=cid,
                               conversation_id=conversation_id,
                               user_role_id=user_role_id,
                               create_time=create_time)


# 返回和接收前端的额外参数
class ChatContentMainResp(ChatContentMain):
    character: Optional[CharacterCard] = None

    def to_chat_content(self):
        return ChatContent(**self.model_dump(exclude={"is_complete", "is_partial", "character", "cid", "conversation_id", "user_role_id", "create_time"}))

    def to_chat_content_main(self):
        return ChatContentMain(**self.model_dump(exclude={"is_complete", "is_partial", "character"}))
