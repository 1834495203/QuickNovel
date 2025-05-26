import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.entity.Conversation import Conversation, ChatContentMain, ChatMessageType
from core.utils.JsonlStorage import JSONLStorage
from core.entity.ResponseEntity import ResponseModel, success, error

# 存储地址配置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 存储会话
CONVERSATION_DB_PATH = f'{CURRENT_DIR}/db/conversations.jsonl'
# 存储对话
CHAT_CONTENT_DB_PATH = f'{CURRENT_DIR}/db/chat_contents.jsonl'


class ConversationService:
    """会话CRUD操作类"""

    def __init__(self, db_path: str = CONVERSATION_DB_PATH):
        self.storage = JSONLStorage(db_path)

    def create(self, conversation: Conversation) -> ResponseModel[Conversation]:
        """创建会话"""
        try:
            # 检查conversation_id是否已存在
            existing = self.get_by_id(conversation.conversation_id)
            if existing.data:
                return error(400, f"Conversation with ID {conversation.conversation_id} already exists")

            # 如果你需要 UTC 时间戳
            utc_datetime = datetime.now()
            conversation.create_time = utc_datetime.timestamp()

            # 添加到文件
            self.storage.append(conversation)
            return success(conversation, "会话创建成功")
        except Exception as e:
            return error(500, f"创建会话失败: {str(e)}")

    def get_by_id(self, conversation_id: int) -> ResponseModel[Optional[Conversation]]:
        """根据ID获取会话"""
        try:
            data = self.storage.read_all()
            for item in data:
                if item.get('conversation_id') == conversation_id:
                    return success(Conversation(**item), "获取会话成功")
            return success(None, "未找到指定会话")
        except Exception as e:
            return error(500, f"获取会话失败: {str(e)}")

    def get_all(self) -> ResponseModel[List[Conversation]]:
        """获取所有会话"""
        try:
            data = self.storage.read_all()
            conversations = [Conversation(**item) for item in data]
            return success(conversations, "获取所有会话成功")
        except Exception as e:
            return error(500, f"获取所有会话失败: {str(e)}")

    def get_by_root_id(self, root_conversation_id: int) -> ResponseModel[List[Conversation]]:
        """根据根会话ID获取子会话"""
        try:
            data = self.storage.read_all()
            conversations = [Conversation(**item) for item in data
                            if item.get('root_conversation_id') == root_conversation_id]
            return success(conversations, "获取子会话成功")
        except Exception as e:
            return error(500, f"获取子会话失败: {str(e)}")

    def get_by_character_id(self, character_id: int) -> ResponseModel[List[Conversation]]:
        """根据角色ID获取会话"""
        try:
            data = self.storage.read_all()
            conversations = [Conversation(**item) for item in data
                            if item.get('character_id') == character_id]
            return success(conversations, "根据角色ID获取会话成功")
        except Exception as e:
            return error(500, f"根据角色ID获取会话失败: {str(e)}")

    def update(self, conversation_id: int, updates: Dict[str, Any]) -> ResponseModel[Optional[Conversation]]:
        """更新会话"""
        try:
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
                    return success(updated_conversation, "会话更新成功")
            return success(None, "未找到指定会话")
        except Exception as e:
            return error(500, f"更新会话失败: {str(e)}")

    def delete(self, conversation_id: int) -> ResponseModel[bool]:
        """删除会话"""
        try:
            data = self.storage.read_all()
            original_len = len(data)
            data = [item for item in data if item.get('conversation_id') != conversation_id]

            if len(data) < original_len:
                self.storage.write_all(data)
                return success(True, "会话删除成功")
            return success(False, "未找到指定会话")
        except Exception as e:
            return error(500, f"删除会话失败: {str(e)}")

    def get_root_conversations(self) -> ResponseModel[List[Conversation]]:
        """获取所有根会话（root_conversation_id = -1）"""
        try:
            data = self.storage.read_all()
            conversations = [Conversation(**item) for item in data
                            if item.get('root_conversation_id') == -1]
            return success(conversations, "获取根会话成功")
        except Exception as e:
            return error(500, f"获取根会话失败: {str(e)}")


class ChatContentService:
    """聊天内容CRUD操作类"""

    def __init__(self, db_path: str = CHAT_CONTENT_DB_PATH):
        self.storage = JSONLStorage(db_path)

    def create(self, chat_content: ChatContentMain) -> ResponseModel[ChatContentMain]:
        """创建聊天内容"""
        try:
            # 检查cid是否已存在
            existing = self.get_by_cid(chat_content.cid)
            if existing.data:
                return error(400, f"Chat content with CID {chat_content.cid} already exists")

            # 添加到文件
            utc_datetime = datetime.now()
            chat_content.create_time = utc_datetime.timestamp()
            self.storage.append(chat_content)
            return success(chat_content, "聊天内容创建成功")
        except Exception as e:
            return error(500, f"创建聊天内容失败: {str(e)}")

    def get_by_cid(self, cid: str) -> ResponseModel[Optional[ChatContentMain]]:
        """根据CID获取聊天内容"""
        try:
            data = self.storage.read_all()
            for item in data:
                if item.get('cid') == cid:
                    # 处理enum反序列化
                    if 'chat_type' in item and isinstance(item['chat_type'], int):
                        item['chat_type'] = ChatMessageType(item['chat_type'])
                    return success(ChatContentMain(**item), "获取聊天内容成功")
            return success(None, "未找到指定聊天内容")
        except Exception as e:
            return error(500, f"获取聊天内容失败: {str(e)}")

    def get_all(self) -> ResponseModel[List[ChatContentMain]]:
        """获取所有聊天内容"""
        try:
            data = self.storage.read_all()
            result = []
            for item in data:
                # 处理enum反序列化
                if 'chat_type' in item and isinstance(item['chat_type'], int):
                    item['chat_type'] = ChatMessageType(item['chat_type'])
                result.append(ChatContentMain(**item))
            return success(result, "获取所有聊天内容成功")
        except Exception as e:
            return error(500, f"获取所有聊天内容失败: {str(e)}")

    def get_by_conversation_id(self, conversation_id: int) -> ResponseModel[List[ChatContentMain]]:
        """根据会话ID获取聊天内容"""
        try:
            data = self.storage.read_all()
            result = []
            for item in data:
                if item.get('conversation_id') == conversation_id:
                    # 处理enum反序列化
                    if 'chat_type' in item and isinstance(item['chat_type'], int):
                        item['chat_type'] = ChatMessageType(item['chat_type'])
                    result.append(ChatContentMain(**item))
            return success(result, "根据会话ID获取聊天内容成功")
        except Exception as e:
            return error(500, f"根据会话ID获取聊天内容失败: {str(e)}")

    def get_by_role(self, role: str) -> ResponseModel[List[ChatContentMain]]:
        """根据角色获取聊天内容"""
        try:
            data = self.storage.read_all()
            result = []
            for item in data:
                if item.get('role') == role:
                    # 处理enum反序列化
                    if 'chat_type' in item and isinstance(item['chat_type'], int):
                        item['chat_type'] = ChatMessageType(item['chat_type'])
                    result.append(ChatContentMain(**item))
            return success(result, "根据角色获取聊天内容成功")
        except Exception as e:
            return error(500, f"根据角色获取聊天内容失败: {str(e)}")

    def get_by_chat_type(self, chat_type: ChatMessageType) -> ResponseModel[List[ChatContentMain]]:
        """根据聊天类型获取聊天内容"""
        try:
            data = self.storage.read_all()
            result = []
            for item in data:
                if item.get('chat_type') == chat_type.value:
                    # 处理enum反序列化
                    item['chat_type'] = chat_type
                    result.append(ChatContentMain(**item))
            return success(result, "根据聊天类型获取聊天内容成功")
        except Exception as e:
            return error(500, f"根据聊天类型获取聊天内容失败: {str(e)}")

    def update(self, cid: str, updates: Dict[str, Any]) -> ResponseModel[Optional[ChatContentMain]]:
        """更新聊天内容"""
        try:
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
                    return success(updated_content, "聊天内容更新成功")
            return success(None, "未找到指定聊天内容")
        except Exception as e:
            return error(500, f"更新聊天内容失败: {str(e)}")

    def delete(self, cid: str) -> ResponseModel[bool]:
        """删除聊天内容"""
        try:
            data = self.storage.read_all()
            original_len = len(data)
            data = [item for item in data if item.get('cid') != cid]

            if len(data) < original_len:
                self.storage.write_all(data)
                return success(True, "聊天内容删除成功")
            return success(False, "未找到指定聊天内容")
        except Exception as e:
            return error(500, f"删除聊天内容失败: {str(e)}")

    def delete_by_conversation_id(self, conversation_id: int) -> ResponseModel[int]:
        """根据会话ID删除所有相关聊天内容"""
        try:
            data = self.storage.read_all()
            original_len = len(data)
            data = [item for item in data if item.get('conversation_id') != conversation_id]

            deleted_count = original_len - len(data)
            if deleted_count > 0:
                self.storage.write_all(data)
            return success(deleted_count, f"成功删除 {deleted_count} 条聊天内容")
        except Exception as e:
            return error(500, f"根据会话ID删除聊天内容失败: {str(e)}")

    def search_content(self, keyword: str) -> ResponseModel[List[ChatContentMain]]:
        """搜索聊天内容"""
        try:
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
            return success(result, f"搜索到 {len(result)} 条匹配内容")
        except Exception as e:
            return error(500, f"搜索聊天内容失败: {str(e)}")


# 使用示例
def example_usage():
    """使用示例"""
    # 初始化CRUD对象
    conversation_crud = ConversationService()
    chat_content_crud = ChatContentService()

    # 创建会话
    conversation = Conversation(
        root_conversation_id=-1,
        conversation_id=1,
        character_id=100
    )
    created_response = conversation_crud.create(conversation)
    if created_response.code == 200:
        print(f"Created conversation: {created_response.data.conversation_id}, create_time: {created_response.data.create_time}")
    else:
        print(f"Error: {created_response.message}")

    # 创建聊天内容
    chat_content = ChatContentMain(
        cid=str(uuid.uuid4()),
        conversation_id=1,
        user_role_id=1,
        role="user",
        content="Hello, how are you?",
        chat_type=ChatMessageType.NORMAL_MESSAGE_USER
    )
    created_content_response = chat_content_crud.create(chat_content)
    if created_content_response.code == 200:
        print(f"Created chat content: {created_content_response.data.cid}, create_time: {created_content_response.data.create_time}")
    else:
        print(f"Error: {created_content_response.message}")

    # 查询示例
    conversations_response = conversation_crud.get_all()
    if conversations_response.code == 200:
        print(f"All conversations: {len(conversations_response.data)}")

    chat_contents_response = chat_content_crud.get_by_conversation_id(1)
    if chat_contents_response.code == 200:
        print(f"Chat contents for conversation 1: {len(chat_contents_response.data)}")

    # 更新示例
    updated_response = conversation_crud.update(1, {"character_id": 200})
    if updated_response.code == 200:
        print(f"Updated conversation: {updated_response.data}")

    # 搜索示例
    search_response = chat_content_crud.search_content("hello")
    if search_response.code == 200:
        print(f"Search results: {len(search_response.data)}")


if __name__ == "__main__":
    example_usage()