from datetime import datetime

from pony.orm import PrimaryKey, Required, Optional, Set

from core.entity.po.NovelEntity import SceneEntity
from core.mapper.config.DatabaseConfig import db


class ConversationEntity(db.Entity):
    conversation_id = PrimaryKey(int, auto=True)

    role = Required(str)

    # 发送者角色：可选，因为系统消息或旁白可能没有角色
    sender_character = Optional('CharacterEntity')

    # 接收者角色：可选，用于多角色对话的指定接收方
    receiver_character = Optional('CharacterEntity')

    content = Required(str)

    create_time = Required(datetime)

    parent = Optional('ConversationEntity')

    children = Set('ConversationEntity')

    # 外键，关联情景表
    scene = Required(SceneEntity)


