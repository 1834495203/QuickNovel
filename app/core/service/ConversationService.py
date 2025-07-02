import asyncio
from datetime import datetime
from typing import List
from fastapi import Request
from fastapi.responses import StreamingResponse

from core.entity.ResponseEntity import ResponseModel, success
from core.entity.dto.ConversationDto import CreateConversationDto, ResponseConversationDto
from core.mapper.ConversationMapper import ConversationMapperInterface
from core.service.ProviderService import ProviderService
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class ConversationService:
    def __init__(self, conversation_mapper: ConversationMapperInterface, providerService: ProviderService):
        self.conversation_mapper = conversation_mapper
        self.provider_service = providerService

    def create_conversation(self, request: Request, conversation: CreateConversationDto) -> StreamingResponse:
        conversation.create_time = datetime.now()
        conversation_id = self.conversation_mapper.create_conversation(conversation)

        # 记录日志
        logging.info(f"创建角对话成功，id为:{conversation_id}")

        content = ""

        async def event_generator(content: str):
            try:
                async for chunk in self.provider_service.generate_llm_response(conversation.content, conversation.novel):
                    if await request.is_disconnected():
                        print("客户端已断开连接。")
                        break

                    if chunk == "[DONE]":
                        # 发送一个表示结束的事件
                        conversation_id = self.conversation_mapper.create_conversation(CreateConversationDto(
                            content=content,
                            role="assistant",
                            create_time=datetime.now(),
                            scene=conversation.scene,
                        ))
                        # 记录日志
                        logging.info(f"保存llm对话成功，id为:{conversation_id}")
                        yield f"event: end\ndata: {chunk}\n\n"
                        break
                    else:
                        # 发送普通的文本事件
                        content += chunk
                        yield f"data: {chunk}\n\n"
            except asyncio.CancelledError:
                logging.error("请求被取消。")
            except Exception as e:
                logging.error(f"流式生成过程中发生错误: {str(e)}")
                yield f"error: 流式生成失败: {str(e)}"

        # 使用 StreamingResponse 包装事件生成器
        return StreamingResponse(event_generator(content), media_type="text/event-stream")

    def get_conversation_by_scene_id(self, scene_id: str) -> ResponseModel[List[ResponseConversationDto]]:
        conversations = self.conversation_mapper.get_conversation_by_scene_id(scene_id)

        if not conversations or conversations == []:
            logging.warning(f"情景 ID 为{scene_id}的对话为空")

        logging.info(f"获取情景 ID 为{scene_id}的对话成功, 对话数量为{len(conversations)}")

        return success(message=f"情景 ID 为{scene_id}的对话为空", data=conversations)
