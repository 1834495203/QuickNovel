from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from core.entity.Models import ChatContent
from core.providers.Deepseek import DeepSeekChat
from core.providers.Grok import GrokChat

providers_router = APIRouter(prefix="/api/providers", tags=["providers"])

# 初始化 GrokChat
# chat = GrokChat(model="grok-3-mini")  # 使用 grok-3-mini 模型，可根据需要更改
chat = DeepSeekChat(model="deepseek-chat")


# 定义 LLM API 输入模型
class LLMInput(BaseModel):
    message: str


# 抽取的流式响应生成器函数
async def stream_llm_response(input_data: LLMInput) -> AsyncGenerator[str, None]:
    try:
        # 准备消息
        api_messages = chat.prepare_messages(input_data.message)

        # 调用流式 API
        response = chat.call_api(api_messages, stream=True)

        accumulated_content = ""
        for chunk in response:
            chunk_data = chat.parse_chunk(chunk)
            content = chunk_data.get("content")
            if content:  # 仅发送非空内容
                accumulated_content += content
                yield json.dumps({
                    "role": "assistant",
                    "response": content,
                    "is_complete": True,
                    "is_partial": False
                }) + "\n"

        chat.chat.set_message(ChatContent(
            role="assistant",
            content=accumulated_content
        ))
        # 发送最终完整响应
        yield json.dumps({
            "role": "assistant",
            "response": accumulated_content,
            "is_complete": False,
            "is_partial": True
        }) + "\n"

    except Exception as e:
        yield json.dumps({
            "response": f"错误: {str(e)}",
            "is_partial": False
        }) + "\n"


# 独立的 LLM API，供外部调用
@providers_router.post("/llm")
async def call_llm(input_data: LLMInput):
    return StreamingResponse(stream_llm_response(input_data), media_type="text/event-stream")
