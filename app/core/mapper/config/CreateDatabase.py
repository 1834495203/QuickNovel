from core.entity.po.CharacterEntity import *
from core.entity.po.ConversationEntity import *
from core.entity.po.NovelEntity import *
from core.entity.po.WorldEntity import *

def create_table():
    db.generate_mapping(create_tables=True)
    db.create_tables()

def generate_table_mapping():
    db.generate_mapping(create_tables=True)


if __name__ == '__main__':
    create_table()