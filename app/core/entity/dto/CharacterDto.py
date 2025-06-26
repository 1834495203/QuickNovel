from typing import Optional, List

from pydantic import BaseModel


class TraitDto(BaseModel):
    label: str
    description: str


class SpeakingDto(BaseModel):
    role: str
    content: str
    reply: str


class DistinctiveDto(BaseModel):
    name: str
    content: str


# 创建角色信息
class CreateCharacterDto(BaseModel):
    avatar: Optional[str] = ''
    name: str
    description: Optional[str] = ''
    background_story: Optional[str] = ''

    trait: Optional[List[TraitDto]] = None
    speak: Optional[List[SpeakingDto]] = None
    distinctive: Optional[List[DistinctiveDto]] = None


# 角色信息
class CharacterDto(BaseModel):
    id: int
    avatar: Optional[str] = ''
    name: str
    description: Optional[str] = ''
    background_story: Optional[str] = ''

    trait: Optional[List[TraitDto]] = None
    speak: Optional[List[SpeakingDto]] = None
    distinctive: Optional[List[DistinctiveDto]] = None


# 返回角色信息
class ResponseCharacterDto(CharacterDto):
    pass


# 更新角色信息
class UpdateCharacterDto(CharacterDto):
    pass
