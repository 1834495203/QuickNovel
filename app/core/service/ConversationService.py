import asyncio
from datetime import datetime
from typing import List, AsyncGenerator
from fastapi import Request
from fastapi.responses import StreamingResponse

from core.entity.ResponseEntity import ResponseModel, success
from core.entity.dto.ConversationDto import CreateConversationDto, ResponseConversationDto
from core.mapper.ConversationMapper import ConversationMapperInterface
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class ConversationService:
    def __init__(self, conversation_mapper: ConversationMapperInterface):
        self.conversation_mapper = conversation_mapper

    # 模拟 LLM 流式输出的异步生成器
    async def _generate_llm_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        模拟一个 LLM 的流式响应。
        实际应用中，这里会调用 LangChain 等库来获取 LLM 的逐块输出。
        """
        full_text = f"你问的是关于 '{prompt}' 的问题。这是一个很棒的话题！" \
                    "让我为你生成一些有趣的内容。第一句话，第二句话，第三句话，" \
                    "第四句话，第五句话，第六句话，第七句话，第八句话，第九句话，" \
                    "第十句话，结束。"

        words = full_text.split(" ")
        for word in words:
            yield word + " "  # 每次返回一个词，并加上空格
            await asyncio.sleep(0.1)  # 模拟生成延迟
        yield "[DONE]"  # 发送一个结束标记，前端可以据此判断流结束

    def create_conversation(self, request: Request, conversation: CreateConversationDto) -> StreamingResponse:
        conversation.create_time = datetime.now()
        conversation_id = self.conversation_mapper.create_conversation(conversation)

        # 记录日志
        logging.info(f"创建角对话成功，id为:{conversation_id}")

        async def event_generator():
            try:
                async for chunk in self._generate_llm_response(conversation.content):
                    if await request.is_disconnected():
                        print("客户端已断开连接。")
                        break

                    if chunk == "[DONE]":
                        # 发送一个表示结束的事件
                        yield f"event: end\ndata: {chunk}\n\n"
                        break
                    else:
                        # 发送普通的文本事件
                        yield f"data: {chunk}\n\n"
            except asyncio.CancelledError:
                print("请求被取消。")
            except Exception as e:
                print(f"流式生成过程中发生错误: {e}")
                # 可以在这里发送一个错误事件
                yield f"event: error\ndata: {str(e)}\n\n"

        # 使用 StreamingResponse 包装事件生成器
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    def get_conversation_by_scene_id(self, scene_id: str) -> ResponseModel[List[ResponseConversationDto]]:
        conversations = self.conversation_mapper.get_conversation_by_scene_id(scene_id)

        if not conversations or conversations == []:
            logging.warning(f"情景 ID 为{scene_id}的对话为空")

        logging.info(f"获取情景 ID 为{scene_id}的对话成功, 对话数量为{len(conversations)}")

        return success(message=f"情景 ID 为{scene_id}的对话为空", data=conversations)
