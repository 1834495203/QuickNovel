from datetime import datetime

from pony.orm import PrimaryKey, Required, Optional, Set

from core.mapper.config.DatabaseConfig import db


# 小说基本信息
class NovelEntity(db.Entity):
    novel_id = PrimaryKey(int, auto=True)
    novel_name = Required(str)
    novel_desc = Optional(str)
    create_time = Required(datetime)
    chapter = Set('ChapterEntity')

    # 多对多关联世界观
    world = Set('WorldEntity')

    # 多对多关联角色
    character = Set('CharacterEntity')


# 小说章节信息
class ChapterEntity(db.Entity):
    chapter_id = PrimaryKey(int, auto=True)
    chapter_number = Required(int)
    chapter_title = Required(str)
    chapter_desc = Optional(str)
    create_time = Required(datetime)

    # 定义父章节
    # parent = Optional('ChapterEntity') 表示一个章节可以有一个父章节，也可以没有（根章节）
    # 'ChapterEntity' 用字符串形式，因为类本身还没完全定义完（Python前向引用问题）
    parent = Optional('ChapterEntity')

    # 定义子章节（反向引用）
    # children = Set('ChapterEntity') 表示一个章节可以有多个子章节
    # 这个 Set 字段会自动关联到那些 'parent' 字段指向当前章节的子章节
    children = Set('ChapterEntity')

    # 外键，关联小说
    novel = Required(NovelEntity)

    # 反向引用
    scene = Set('SceneEntity')


# 情景信息
class SceneEntity(db.Entity):
    scene_id = PrimaryKey(int, auto=True)
    scene_name = Required(str)
    scene_desc = Optional(str)
    create_time = Required(datetime)

    # 定义父情景
    parent = Optional('SceneEntity')

    # 定义子情节
    children = Set('SceneEntity')

    # 外键，关联章节，可独立
    chapter = Optional(ChapterEntity)

    # 反向引用
    conversation = Set('ConversationEntity')
