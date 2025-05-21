from typing import List

from pydantic import BaseModel


class Conversation(BaseModel):
    root_cid: int               # 表示根节点会话
    cid: int                    # 会话唯一id
    characters: List[int]       # 涉及会话的角色id
    chat_env_id: int            # 涉及会话的环境
    chat_id: int                # 具体对话id


class ChatContentMain(BaseModel):
    cid: int                    # 单次对话唯一id
    role: str                   # 角色
    content: str                # 消息
    chat_type: int              # 对话类型
    reasoning_content: str      # 推理内容
    chat_time: str              # 对话时间
