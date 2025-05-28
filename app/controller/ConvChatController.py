from fastapi import APIRouter, HTTPException, Depends, Path
import uuid

from core.service.ConvChatService import ConversationService, ChatContentService
from core.entity.Conversation import Conversation, ChatContentMain, CreateConversationRequest, ConversationResponse, \
    ChatContentResponse, CreateChatContentRequest
from core.entity.ResponseEntity import ResponseModel, success

conv_chat_router = APIRouter(prefix="/api/chat", tags=["对话管理"])


# 依赖注入
def get_conversation_service():
    return ConversationService()


def get_chat_content_service(conversation_id: int = Path(...)):
    return ChatContentService(conversation_id)


@conv_chat_router.post("/conversations", response_model=ResponseModel)
async def create_conversation(
    request: CreateConversationRequest,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """根据character_id增加会话"""
    try:
        # 生成新的会话ID
        existing_response = conversation_service.get_all()
        if existing_response.code != 200:
            raise HTTPException(status_code=500, detail=existing_response.message)
        
        existing_conversations = existing_response.data
        max_id = max([c.conversation_id for c in existing_conversations], default=0)
        new_conversation_id = max_id + 1
        
        conversation = Conversation(
            conversation_id=new_conversation_id,
            character_id=request.character_id,
            root_conversation_id=request.root_conversation_id
        )
        
        create_response = conversation_service.create(conversation)
        if create_response.code != 200:
            if create_response.code == 400:
                raise HTTPException(status_code=400, detail=create_response.message)
            else:
                raise HTTPException(status_code=500, detail=create_response.message)
        
        created_conversation = create_response.data
        return success(data=ConversationResponse(
            conversation_id=created_conversation.conversation_id,
            character_id=created_conversation.character_id,
            root_conversation_id=created_conversation.root_conversation_id,
            create_time=created_conversation.create_time
        ))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")

@conv_chat_router.get("/conversations/character/{character_id}", response_model=ResponseModel)
async def get_conversations_by_character(
    character_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """根据character_id读取会话"""
    try:
        response = conversation_service.get_by_character_id(character_id)
        if response.code != 200:
            raise HTTPException(status_code=500, detail=response.message)
        
        conversations = response.data
        return success([
            ConversationResponse(
                conversation_id=conv.conversation_id,
                character_id=conv.character_id,
                root_conversation_id=conv.root_conversation_id,
                create_time=conv.create_time
            )
            for conv in conversations
        ], message="根据角色获取会话成功")
    except HTTPException:
        raise
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
        conversation_response = conversation_service.get_by_id(conversation_id)
        if conversation_response.code != 200:
            raise HTTPException(status_code=500, detail=conversation_response.message)
        
        if not conversation_response.data:
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
        
        create_response = chat_content_service.create(chat_content)
        if create_response.code != 200:
            if create_response.code == 400:
                raise HTTPException(status_code=400, detail=create_response.message)
            else:
                raise HTTPException(status_code=500, detail=create_response.message)
        
        created_content = create_response.data
        return success(data=ChatContentResponse(
            cid=created_content.cid,
            conversation_id=created_content.conversation_id,
            user_role_id=created_content.user_role_id,
            role=created_content.role,
            content=created_content.content,
            reasoning_content=created_content.reasoning_content,
            chat_type=created_content.chat_type,
            create_time=created_content.create_time
        ))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建对话失败: {str(e)}")


@conv_chat_router.get("/conversations/{conversation_id}/chats", response_model=ResponseModel)
async def get_chats_by_conversation(
    conversation_id: int,
    chat_content_service: ChatContentService = Depends(get_chat_content_service),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """根据会话的id读取对应全部对话"""
    try:
        # 验证会话是否存在
        conversation_response = conversation_service.get_by_id(conversation_id)
        if conversation_response.code != 200:
            raise HTTPException(status_code=500, detail=conversation_response.message)
        
        if not conversation_response.data:
            raise HTTPException(status_code=404, detail=f"会话 {conversation_id} 不存在")
        
        chat_response = chat_content_service.get_by_conversation_id(conversation_id)
        if chat_response.code != 200:
            raise HTTPException(status_code=500, detail=chat_response.message)
        
        chat_contents = chat_response.data
        return success([
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
        ], message="获取对话成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话失败: {str(e)}")
