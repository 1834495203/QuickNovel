from typing import Optional, List

from pydantic import BaseModel


class WorldDetail(BaseModel):
    wd_id: int                       # 设定唯一id
    aspect: List[str]                # 事件和设定的关键字
    description: str                 # 简介


# 世界观设定相关
class WorldSetting(BaseModel):
    ws_id: int                                   # 唯一世界观id
    description: str                             # 世界观简介
    details: Optional[List[WorldDetail]] = None  # 详细设定

