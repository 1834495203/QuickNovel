from pony.orm import PrimaryKey, Optional, Required

from core.entity.po.CharacterEntity import CharacterEntity
from core.entity.po.NovelEntity import NovelEntity
from core.mapper.config.DatabaseConfig import db

# 小说和角色的多对多中间表
class CharacterNovelEntity(db.Entity):
    character_novel_id = PrimaryKey(int, auto=True)
    memory = Optional(str)
    status = Optional(str)

    # 关联表信息，外键
    novel = Required(NovelEntity)
    character = Required(CharacterEntity)
