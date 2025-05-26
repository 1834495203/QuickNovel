from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid

from core.service.ConvChatService import ConversationService, ChatContentService
from core.entity.Conversation import Conversation, ChatContentMain, ChatMessageType

conv_chat_router = APIRouter(prefix="/api/chat", tags=["对话管理"])

# 请求模型
class CreateConversationRequest(BaseModel):
    character_id: int
    root_conversation_id: Optional[int] = -1

class CreateChatContentRequest(BaseModel):
    conversation_id: int
    role: str
    user_role_id: int
    content: str
    reasoning_content: Optional[str] = None
    chat_type: ChatMessageType = ChatMessageType.NORMAL_MESSAGE_USER

# 响应模型
class ConversationResponse(BaseModel):
    conversation_id: int
    character_id: int
    root_conversation_id: int
    create_time: float

class ChatContentResponse(BaseModel):
    cid: str
    conversation_id: int
    user_role_id: int
    role: str
    content: str
    reasoning_content: Optional[str]
    chat_type: ChatMessageType
    create_time: float

class ConversationWithChatsResponse(BaseModel):
    conversation: ConversationResponse
    chats: List[ChatContentResponse]

# 依赖注入
def get_conversation_service():
    return ConversationService()

def get_chat_content_service():
    return ChatContentService()

@conv_chat_router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """根据character_id增加会话"""
    try:
        # 生成新的会话ID
        existing_conversations = conversation_service.get_all()
        max_id = max([c.conversation_id for c in existing_conversations], default=0)
        new_conversation_id = max_id + 1
        
        conversation = Conversation(
            conversation_id=new_conversation_id,
            character_id=request.character_id,
            root_conversation_id=request.root_conversation_id
        )
        
        created_conversation = conversation_service.create(conversation)
        
        return ConversationResponse(
            conversation_id=created_conversation.conversation_id,
            character_id=created_conversation.character_id,
            root_conversation_id=created_conversation.root_conversation_id,
            create_time=created_conversation.create_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")

@conv_chat_router.get("/conversations/character/{character_id}", response_model=List[ConversationResponse])
async def get_conversations_by_character(
    character_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """根据character_id读取会话"""
    try:
        conversations = conversation_service.get_by_character_id(character_id)
        
        return [
            ConversationResponse(
                conversation_id=conv.conversation_id,
                character_id=conv.character_id,
                root_conversation_id=conv.root_conversation_id,
                create_time=conv.create_time
            )
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话失败: {str(e)}")

@conv_chat_router.post("/conversations/{conversation_id}/chats", response_model=ChatContentResponse)
async def create_chat_content(
    conversation_id: int,
    request: CreateChatContentRequest,
    chat_content_service: ChatContentService = Depends(get_chat_content_service),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """根据会话id增加对话"""
    try:
        # 验证会话是否存在
        conversation = conversation_service.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"会话 {conversation_id} 不存在")
        
        # 确保请求中的conversation_id与URL中的一致
        if request.conversation_id != conversation_id:
            request.conversation_id = conversation_id
        
        chat_content = ChatContentMain(
            cid=str(uuid.uuid4()),
            conversation_id=request.conversation_id,
            user_role_id=request.user_role_id,
            role=request.role,
            content=request.content,
            reasoning_content=request.reasoning_content,
            chat_type=request.chat_type
        )
        
        created_content = chat_content_service.create(chat_content)
        
        return ChatContentResponse(
            cid=created_content.cid,
            conversation_id=created_content.conversation_id,
            user_role_id=created_content.user_role_id,
            role=created_content.role,
            content=created_content.content,
            reasoning_content=created_content.reasoning_content,
            chat_type=created_content.chat_type,
            create_time=created_content.create_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建对话失败: {str(e)}")

@conv_chat_router.get("/conversations/{conversation_id}/chats", response_model=List[ChatContentResponse])
async def get_chats_by_conversation(
    conversation_id: int,
    chat_content_service: ChatContentService = Depends(get_chat_content_service),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """根据会话的id读取对应全部对话"""
    try:
        # 验证会话是否存在
        conversation = conversation_service.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"会话 {conversation_id} 不存在")
        
        chat_contents = chat_content_service.get_by_conversation_id(conversation_id)
        
        return [
            ChatContentResponse(
                cid=chat.cid,
                conversation_id=chat.conversation_id,
                user_role_id=chat.user_role_id,
                role=chat.role,
                content=chat.content,
                reasoning_content=chat.reasoning_content,
                chat_type=chat.chat_type,
                create_time=chat.create_time
            )
            for chat in chat_contents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话失败: {str(e)}")

@conv_chat_router.get("/characters/{character_id}/conversations-with-chats", response_model=List[ConversationWithChatsResponse])
async def get_conversations_with_chats_by_character(
    character_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service),
    chat_content_service: ChatContentService = Depends(get_chat_content_service)
):
    """根据会话的character_id读取对应角色的对话，并根据会话的id分为不同的会话返回"""
    try:
        # 获取该角色的所有会话
        conversations = conversation_service.get_by_character_id(character_id)
        
        result = []
        for conversation in conversations:
            # 获取每个会话的所有对话
            chat_contents = chat_content_service.get_by_conversation_id(conversation.conversation_id)
            
            conversation_response = ConversationResponse(
                conversation_id=conversation.conversation_id,
                character_id=conversation.character_id,
                root_conversation_id=conversation.root_conversation_id,
                create_time=conversation.create_time
            )
            
            chat_responses = [
                ChatContentResponse(
                    cid=chat.cid,
                    conversation_id=chat.conversation_id,
                    user_role_id=chat.user_role_id,
                    role=chat.role,
                    content=chat.content,
                    reasoning_content=chat.reasoning_content,
                    chat_type=chat.chat_type,
                    create_time=chat.create_time
                )
                for chat in chat_contents
            ]
            
            result.append(ConversationWithChatsResponse(
                conversation=conversation_response,
                chats=chat_responses
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色对话失败: {str(e)}")
