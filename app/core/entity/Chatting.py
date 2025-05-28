from typing import Optional

from pydantic import BaseModel


class Relationship(BaseModel):
    source: str  # 关系的发起者
    target: str  # 关系的对象（如“用户”或“其他角色名”）
    type: str  # 关系类型（如“朋友”、“家人”、“敌人”等）
    attitude: str  # 态度（如“友好”、“冷漠”、“敌对”等）
    description: str  # 关系简介，关系发起者对关系对象的看法
    history: Optional[list[str]] = []  # 关系简史（如“认识三年，曾一起旅行”）

    class Config:
        from_attributes = True


# 聊天场景（每次新聊天时填写或选择）
class ChatEnv(BaseModel):
    location: Optional[str] = None  # 聊天地点（如“咖啡馆”、“网络”）
    time: Optional[str] = None  # 聊天时间（如“深夜”、“午后”）默认现实时间
    situation: Optional[str] = None  # 当前情景（如“用户刚失恋”、“角色在赶deadline”），若为小说人物则需要总结上下文

    class Config:
        from_attributes = True
