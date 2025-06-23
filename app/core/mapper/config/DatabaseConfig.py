from pony.orm import *

# 定义数据库对象
db = Database('sqlite', 'database.sqlite', create_db=True)
