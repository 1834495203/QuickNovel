import json
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union

from pydantic import BaseModel

from core.entity.Conversation import Conversation, ChatContentMain, ChatMessageType

# 存储地址配置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 存储会话
CONVERSATION_DB_PATH = f'{CURRENT_DIR}/db/conversations.jsonl'
# 存储对话
CHAT_CONTENT_DB_PATH = f'{CURRENT_DIR}/db/chat_contents.jsonl'


class JSONLStorage:
    """JSONL文件存储基础类"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                pass

    def read_all(self) -> List[Any]:
        """读取所有数据"""
        data = []
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            item = json.loads(line)
                            data.append(item)
                        except json.JSONDecodeError:
                            continue
        return data

    def write_all(self, data: List[Union[BaseModel, Dict[str, Any]]]):
        """写入所有数据"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            for item in data:
                if isinstance(item, BaseModel):
                    f.write(item.model_dump_json() + '\n')
                else:
                    # 兼容dict格式，处理enum序列化
                    serialized_item = {}
                    for k, v in item.items():
                        if isinstance(v, Enum):
                            serialized_item[k] = v.value
                        else:
                            serialized_item[k] = v
                    f.write(json.dumps(serialized_item, ensure_ascii=False) + '\n')

    def append(self, item: Union[BaseModel, Dict[str, Any]]):
        """追加单条数据"""
        with open(self.file_path, 'a', encoding='utf-8') as f:
            if isinstance(item, BaseModel):
                f.write(item.model_dump_json() + '\n')
            else:
                # 兼容dict格式，处理enum序列化
                serialized_item = {}
                for k, v in item.items():
                    if isinstance(v, Enum):
                        serialized_item[k] = v.value
                    else:
                        serialized_item[k] = v
                f.write(json.dumps(serialized_item, ensure_ascii=False) + '\n')


class ConversationCRUD:
    """会话CRUD操作类"""

    def __init__(self, db_path: str = CONVERSATION_DB_PATH):
        self.storage = JSONLStorage(db_path)

    def create(self, conversation: Conversation) -> Conversation:
        """创建会话"""
        # 检查conversation_id是否已存在
        existing = self.get_by_id(conversation.conversation_id)
        if existing:
            raise ValueError(f"Conversation with ID {conversation.conversation_id} already exists")

        # 如果你需要 UTC 时间戳
        utc_datetime = datetime.now()
        conversation.create_time = utc_datetime.timestamp()

        # 添加到文件
        self.storage.append(conversation)
        return conversation

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """根据ID获取会话"""
        data = self.storage.read_all()
        for item in data:
            if item.get('conversation_id') == conversation_id:
                return Conversation(**item)
        return None

    def get_all(self) -> List[Conversation]:
        """获取所有会话"""
        data = self.storage.read_all()
        return [Conversation(**item) for item in data]

    def get_by_root_id(self, root_conversation_id: int) -> List[Conversation]:
        """根据根会话ID获取子会话"""
        data = self.storage.read_all()
        return [Conversation(**item) for item in data
                if item.get('root_conversation_id') == root_conversation_id]

    def get_by_character_id(self, character_id: int) -> List[Conversation]:
        """根据角色ID获取会话"""
        data = self.storage.read_all()
        return [Conversation(**item) for item in data
                if item.get('character_id') == character_id]

    def update(self, conversation_id: int, updates: Dict[str, Any]) -> Optional[Conversation]:
        """更新会话"""
        data = self.storage.read_all()
        for i, item in enumerate(data):
            if item.get('conversation_id') == conversation_id:
                # 更新字段
                for key, value in updates.items():
                    if hasattr(Conversation, key):
                        item[key] = value

                # 验证更新后的数据
                updated_conversation = Conversation(**item)
                data[i] = updated_conversation

                # 写回文件
                self.storage.write_all(data)
                return updated_conversation
        return None

    def delete(self, conversation_id: int) -> bool:
        """删除会话"""
        data = self.storage.read_all()
        original_len = len(data)
        data = [item for item in data if item.get('conversation_id') != conversation_id]

        if len(data) < original_len:
            self.storage.write_all(data)
            return True
        return False

    def get_root_conversations(self) -> List[Conversation]:
        """获取所有根会话（root_conversation_id = -1）"""
        data = self.storage.read_all()
        return [Conversation(**item) for item in data
                if item.get('root_conversation_id') == -1]


class ChatContentCRUD:
    """聊天内容CRUD操作类"""

    def __init__(self, db_path: str = CHAT_CONTENT_DB_PATH):
        self.storage = JSONLStorage(db_path)

    def create(self, chat_content: ChatContentMain) -> ChatContentMain:
        """创建聊天内容"""
        # 检查cid是否已存在
        existing = self.get_by_cid(chat_content.cid)
        if existing:
            raise ValueError(f"Chat content with CID {chat_content.cid} already exists")

        # 添加到文件
        utc_datetime = datetime.now()
        chat_content.create_time = utc_datetime.timestamp()
        self.storage.append(chat_content)
        return chat_content

    def get_by_cid(self, cid: str) -> Optional[ChatContentMain]:
        """根据CID获取聊天内容"""
        data = self.storage.read_all()
        for item in data:
            if item.get('cid') == cid:
                # 处理enum反序列化
                if 'chat_type' in item and isinstance(item['chat_type'], int):
                    item['chat_type'] = ChatMessageType(item['chat_type'])
                return ChatContentMain(**item)
        return None

    def get_all(self) -> List[ChatContentMain]:
        """获取所有聊天内容"""
        data = self.storage.read_all()
        result = []
        for item in data:
            # 处理enum反序列化
            if 'chat_type' in item and isinstance(item['chat_type'], int):
                item['chat_type'] = ChatMessageType(item['chat_type'])
            result.append(ChatContentMain(**item))
        return result

    def get_by_conversation_id(self, conversation_id: int) -> List[ChatContentMain]:
        """根据会话ID获取聊天内容"""
        data = self.storage.read_all()
        result = []
        for item in data:
            if item.get('conversation_id') == conversation_id:
                # 处理enum反序列化
                if 'chat_type' in item and isinstance(item['chat_type'], int):
                    item['chat_type'] = ChatMessageType(item['chat_type'])
                result.append(ChatContentMain(**item))
        return result

    def get_by_role(self, role: str) -> List[ChatContentMain]:
        """根据角色获取聊天内容"""
        data = self.storage.read_all()
        result = []
        for item in data:
            if item.get('role') == role:
                # 处理enum反序列化
                if 'chat_type' in item and isinstance(item['chat_type'], int):
                    item['chat_type'] = ChatMessageType(item['chat_type'])
                result.append(ChatContentMain(**item))
        return result

    def get_by_chat_type(self, chat_type: ChatMessageType) -> List[ChatContentMain]:
        """根据聊天类型获取聊天内容"""
        data = self.storage.read_all()
        result = []
        for item in data:
            if item.get('chat_type') == chat_type.value:
                # 处理enum反序列化
                item['chat_type'] = chat_type
                result.append(ChatContentMain(**item))
        return result

    def update(self, cid: str, updates: Dict[str, Any]) -> Optional[ChatContentMain]:
        """更新聊天内容"""
        data = self.storage.read_all()
        for i, item in enumerate(data):
            if item.get('cid') == cid:
                # 更新字段
                for key, value in updates.items():
                    if hasattr(ChatContentMain, key):
                        item[key] = value

                # 处理enum反序列化
                if 'chat_type' in item and isinstance(item['chat_type'], int):
                    item['chat_type'] = ChatMessageType(item['chat_type'])

                # 验证更新后的数据
                updated_content = ChatContentMain(**item)
                data[i] = updated_content

                # 写回文件
                self.storage.write_all(data)
                return updated_content
        return None

    def delete(self, cid: str) -> bool:
        """删除聊天内容"""
        data = self.storage.read_all()
        original_len = len(data)
        data = [item for item in data if item.get('cid') != cid]

        if len(data) < original_len:
            self.storage.write_all(data)
            return True
        return False

    def delete_by_conversation_id(self, conversation_id: int) -> int:
        """根据会话ID删除所有相关聊天内容"""
        data = self.storage.read_all()
        original_len = len(data)
        data = [item for item in data if item.get('conversation_id') != conversation_id]

        deleted_count = original_len - len(data)
        if deleted_count > 0:
            self.storage.write_all(data)
        return deleted_count

    def search_content(self, keyword: str) -> List[ChatContentMain]:
        """搜索聊天内容"""
        data = self.storage.read_all()
        result = []
        for item in data:
            content = item.get('content', '').lower()
            reasoning_content = item.get('reasoning_content', '').lower() if item.get('reasoning_content') else ''

            if keyword.lower() in content or keyword.lower() in reasoning_content:
                # 处理enum反序列化
                if 'chat_type' in item and isinstance(item['chat_type'], int):
                    item['chat_type'] = ChatMessageType(item['chat_type'])
                result.append(ChatContentMain(**item))
        return result


# 使用示例
def example_usage():
    """使用示例"""
    # 初始化CRUD对象
    conversation_crud = ConversationCRUD()
    chat_content_crud = ChatContentCRUD()

    # 创建会话
    conversation = Conversation(
        root_conversation_id=-1,
        conversation_id=1,
        character_id=100
    )
    created_conversation = conversation_crud.create(conversation)
    print(
        f"Created conversation: {created_conversation.conversation_id}, create_time: {created_conversation.create_time}")

    # 创建聊天内容
    chat_content = ChatContentMain(
        cid=str(uuid.uuid4()),
        conversation_id=1,
        role="user",
        content="Hello, how are you?",
        chat_type=ChatMessageType.NORMAL_MESSAGE_USER
    )
    created_content = chat_content_crud.create(chat_content)
    print(f"Created chat content: {created_content.cid}, create_time: {created_content.create_time}")

    # 查询示例
    conversations = conversation_crud.get_all()
    print(f"All conversations: {len(conversations)}")

    chat_contents = chat_content_crud.get_by_conversation_id(1)
    print(f"Chat contents for conversation 1: {len(chat_contents)}")

    # 更新示例
    updated_conversation = conversation_crud.update(1, {"character_id": 200})
    print(f"Updated conversation: {updated_conversation}")

    # 搜索示例
    search_results = chat_content_crud.search_content("hello")
    print(f"Search results: {len(search_results)}")


if __name__ == "__main__":
    example_usage()