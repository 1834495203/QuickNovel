from datetime import datetime

from pony.orm import PrimaryKey, Required, Set

from core.mapper.config.DatabaseConfig import db

# 世界观信息
class WorldEntity(db.Entity):
    world_id = PrimaryKey(int, auto=True)
    world_name = Required(str)
    world_desc = Required(str)
    create_time = Required(datetime)

    # 反向引用
    world_detail = Set('WorldDetailEntity')

    # 多对多，关联小说
    novel = Set('NovelEntity')


# 对应详细世界观信息
class WorldDetailEntity(db.Entity):
    world_detail_name = Required(str)
    world_detail_desc = Required(str)
    world = Required(WorldEntity)
