import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from fastapi.params import Query

from core.service.ConvChatService import ConversationService, ChatContentService
from core.entity.Conversation import Conversation, ChatContentMain
from core.entity.ResponseEntity import ResponseModel, success, error


conv_chat_router = APIRouter(prefix="/api/chat", tags=["对话管理"])


# 依赖注入
def get_conversation_service():
    return ConversationService()


def get_chat_content_service():
    return ChatContentService()


@conv_chat_router.post("/conversations", response_model=ResponseModel)
async def create_conversation(
        request: Conversation,
        conversation_service: ConversationService = Depends(get_conversation_service)):
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
        return success(data=Conversation(
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
        conversation_service: ConversationService = Depends(get_conversation_service)):
    """根据character_id读取会话"""
    try:
        response = conversation_service.get_by_character_id(character_id)
        if response.code != 200:
            raise HTTPException(status_code=500, detail=response.message)
        
        conversations = response.data
        return success([
            Conversation(
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


@conv_chat_router.get("/conversations", response_model=ResponseModel)
async def get_chats_by_conversation(
        conversation_id: Optional[int] = Query(None),
        chat_content_service: ChatContentService = Depends(get_chat_content_service),
        conversation_service: ConversationService = Depends(get_conversation_service)):
    """根据会话的id读取对应全部对话"""
    try:
        if conversation_id:
            # 验证会话是否存在
            chat_content_service.set_conversation_id(conversation_id)
            conversation_response = conversation_service.get_by_id(conversation_id)
            if conversation_response.code != 200:
                raise HTTPException(status_code=500, detail=conversation_response.message)

            if not conversation_response.data:
                raise HTTPException(status_code=404, detail=f"会话 {conversation_id} 不存在")

        chat_response = chat_content_service.get_by_conversation_id(conversation_id)
        if chat_response.code != 200:
            raise HTTPException(status_code=500, detail=chat_response.message)
        
        chat_contents = chat_response.data
        data = [
            ChatContentMain(
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
        return success(data, message="获取对话成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话失败: {str(e)}")


@conv_chat_router.delete("/conversations/chats", response_model=ResponseModel)
async def delete_chat_content_in_conversation(
        conversation_id: Optional[int] = Query(None),
        cid: str = Query(...),
        chat_content_service: ChatContentService = Depends(get_chat_content_service),
        conversation_service: ConversationService = Depends(get_conversation_service)):
    """在指定的会话中根据CID删除对话内容"""
    try:
        if conversation_id:
            # 会话模式下，检查是否有该会话
            resp = conversation_service.get_by_id(conversation_id)
            if resp.code != 200:
                return error(message=resp.message)
            chat_content_service.set_conversation_id(conversation_id)
        delete_response = chat_content_service.delete(cid)
        
        if delete_response.code != 200:
            # This implies a server-side issue with the service itself if code is not 200
            logging.error(delete_response.message)
            return error(code=500, message="删除对话内容时出错")

        if not delete_response.data:  # delete_response.data is False if CID not found
            return error(code=404, message=f"对话内容 {cid} 在会话 {conversation_id} 中未找到")
            
        return success(data=True, message=f"对话内容 {cid} 已成功从会话 {conversation_id} 中删除")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(str(e))
        return error(message="系统内部错误")


@conv_chat_router.put("/conversations/chats")
async def update_chat_content_in_conversation(
        chat_content: ChatContentMain,
        chat_content_service: ChatContentService = Depends(get_chat_content_service),
        conversation_service: ConversationService = Depends(get_conversation_service)):
    """
    在指定的会话中根据CID更新对话内容
    """
    print(chat_content)
    conversation_id = chat_content.conversation_id
    cid = chat_content.cid
    try:
        if conversation_id is not None:
            # 会话模式下，检查是否有该会话
            resp = conversation_service.get_by_id(conversation_id)
            if resp.code != 200:
                return error(message=resp.message)
            chat_content_service.set_conversation_id(conversation_id)

        update_response = chat_content_service.update(cid, chat_content)
        print(update_response)

        if update_response.code != 200:
            # This implies a server-side issue with the service itself if code is not 200
            logging.error(update_response.message)
            return error(code=500, message="更新对话内容时出错")

        if not update_response.data:  # delete_response.data is False if CID not found
            return error(code=404, message=f"对话内容 {cid} 在会话 {conversation_id} 中未找到")

        return success(data=True, message=f"对话内容 {cid} 已成功从会话 {conversation_id} 中更新")

    except HTTPException:
        raise
    except Exception as e:
        logging.error(str(e))
        return error(message="系统内部错误")