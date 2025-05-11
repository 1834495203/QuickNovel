from pydantic import BaseModel
from typing import Optional, List


# 基础角色卡（必填字段最小化，选填字段保留）
class SimpleCharacterCard(BaseModel):
    id: int  # 必填：角色唯一标识符
    avatar: Optional[str] = None  # 选填：头像链接
    name: Optional[str] = None  # 选填：角色名称
    description: Optional[str] = None   # 描述角色，重要

    class Config:
        from_attributes = True  # 支持 ORM 转换


# 性格特征（必填，简化）
class Trait(BaseModel):
    label: str  # 必填：特征标签
    description: str  # 描述每个性格

    class Config:
        from_attributes = True


# 性格（特征选填，描述必填，量表必填）
class Personality(BaseModel):
    traits: Optional[List[Trait]] = []  # 选填：性格特征列表（用于 chip 显示）

    class Config:
        from_attributes = True


# 背景（出身选填，记忆必填，其他删除）
class Background(BaseModel):
    background_story: Optional[str] = None  # 选填：角色出身

    class Config:
        from_attributes = True


# 说话方式（必填）
class Speaking(BaseModel):
    role: str   # 必填：询问的人
    content: str  # 必填：台词
    reply: str  # 必填：角色或这llm该如何回复（决定llm会如何回复，可以在语言的基础上加入动作，心里，神态描写。）

    class Config:
        from_attributes = True


# 行为（说话方式必填，其他删除）
class Behaviors(BaseModel):
    speakingStyle: List[Speaking]  # 必填：说话方式列表

    class Config:
        from_attributes = True


# 能力和专长类
class Abilities(BaseModel):
    knowledge: Optional[List[str]] = []  # 知识领域
    hobby: Optional[List[str]] = []      # 兴趣爱好

    class Config:
        from_attributes = True


class Distinctive(BaseModel):
    fieldName: str
    fieldValue: str


# 用户自定义字段
class CustomizeFields(BaseModel):
    fields: List[Distinctive]


# 扩展角色卡（整合所有保留字段）
class CharacterCard(SimpleCharacterCard):
    personality: Optional[Personality] = None   # 选填：性格详情
    background: Optional[Background] = None     # 选填：背景详情
    behaviors: Optional[Behaviors] = None       # 选填：行为详情
    abilities: Optional[Abilities] = None       # 能力和专长
    customize: Optional[CustomizeFields] = None # 用户自定义类型

    class Config:
        from_attributes = True

    def __repr__(self):
        return (
            f"CharacterCard(id={self.id}, name={self.name}, gender={self.gender}, "
            f"age={self.age}, occupation={self.occupation}, "
            f"avatar={self.avatar}, appearance={self.appearance}, "
            f"personality={self.personality}, background={self.background}, "
            f"behaviors={self.behaviors})",
            f"abilities={self.abilities}",
        )


class UserCard(CharacterCard):
    id: int
    is_conn_character: bool = False                    # 声明是否连接角色
    conn_character_id: Optional[int] = None            # 可选，选择对应角色信息
    description: Optional[str] = None                  # 用户说明
