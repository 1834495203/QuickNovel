from typing import List

from pydantic import BaseModel


# 最必要的信息，存入数据库的字段
# class ChatContentMain:
#     def __init__(self, cid: int,
#                  role: str,
#                  content: str,
#                  chat_type: ChatMessageType,
#                  users: List[UserCard],
#                  characters: List[CharacterCard],
#                  reasoning_content: Optional[str] = None,):
#         self.cid = cid                                       # 对话唯一id
#         self.role = role                                     # 角色
#         self.content = content                               # 消息
#         self.chat_type = chat_type                           # 对话类型
#         self.users = users                                   # 用户角色
#         self.characters = characters                         # 对话角色
#         self.reasoning_content = reasoning_content           # 推理


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
