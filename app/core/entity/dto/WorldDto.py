from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class CreateWorldDto(BaseModel):
    world_name: str
    world_desc: str
    create_time: Optional[datetime] = None


class CreateWorldDetailDto(BaseModel):
    world_detail_name: str
    world_detail_desc: str

    # 对应世界观的id
    world: int


# 返回世界观的基本信息
class ResponseWorldDto(BaseModel):
    world_id: int
    world_name: str
    world_desc: str
    create_time: datetime


# 返回的单个详细世界观的信息
class ResponseWorldDetailDto(BaseModel):
    id: int
    world_detail_name: str
    world_detail_desc: str
    world: int


# 返回单个世界观的全部信息
class ResponseAllWorldDetailDto(ResponseWorldDto):
    world_details: List[ResponseWorldDetailDto]

