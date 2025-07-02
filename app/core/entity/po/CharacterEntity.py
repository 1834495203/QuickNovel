from pony.orm import PrimaryKey, Required, Set, Optional

from core.mapper.config.DatabaseConfig import db


# 角色实体类
class CharacterEntity(db.Entity):
    character_id = PrimaryKey(int, auto=True)
    avatar = Optional(str)
    name = Required(str)
    description = Optional(str)
    background_story = Optional(str)
    trait = Set('Trait')
    speak = Set('Speak')
    distinctive = Set('Distinctive')

    # 多对多关联小说
    # novel = Set('NovelEntity')

    # 多对一关联小说角色表
    novel = Set('CharacterNovelEntity')

    # 反向引用
    sender_character = Set('ConversationEntity', reverse='sender_character')
    receiver_character = Set('ConversationEntity', reverse='receiver_character')


# 角色性格特征
class Trait(db.Entity):
    label = Required(str)
    description = Required(str)
    character = Required(CharacterEntity)


# 角色说话方式
class Speak(db.Entity):
    role = Required(str)
    content = Required(str)
    reply = Required(str)
    character = Required(CharacterEntity)


# 用户自定义字段
class Distinctive(db.Entity):
    name = Required(str)
    content = Required(str)
    character = Required(CharacterEntity)
