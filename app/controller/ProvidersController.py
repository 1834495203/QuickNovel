import asyncio
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import random

from core.entity.Conversation import ChatContentMain, ChatContentMainResp
from core.entity.Models import ChatMessageType, ChatContent
from core.providers.Deepseek import DeepSeekChat
from core.providers.Grok import GrokChat
from core.service.ConvChatService import ChatContentService

providers_router = APIRouter(prefix="/api/providers", tags=["providers"])

# 初始化 GrokChat
# chat = GrokChat(model="grok-3-mini")  # 使用 grok-3-mini 模型，可根据需要更改
chat = DeepSeekChat(model="deepseek-chat")


def get_chat_content_service():
    return ChatContentService()


# 模拟的流式响应生成器函数
async def stream_llm_response_test(input_data: ChatContentMain) -> AsyncGenerator[str, None]:
    try:
        # 模拟不同类型的响应内容
        mock_responses = [
            "这是一个很有趣的问题。",
            "让我来详细解释一下这个概念。",
            "根据我的理解，这个问题可以从以下几个方面来分析：",
            "首先，我们需要考虑基本原理。",
            "其次，实际应用中还需要注意一些细节。",
            "总的来说，这是一个复杂但有意义的话题。",
            "希望这个回答对你有帮助。如果还有其他问题，请随时问我。"
        ]

        # 根据输入消息长度决定响应内容
        if len(input_data.content) < 10:
            responses = mock_responses[:3]
        elif len(input_data.content) < 50:
            responses = mock_responses[:5]
        else:
            responses = mock_responses

        # 如果输入包含特定关键词，提供相关响应
        if any(keyword in input_data.content.lower() for keyword in ['错误', 'error', '问题', 'bug']):
            responses = [
                "我理解你遇到了一些技术问题。",
                "让我帮你分析一下可能的原因。",
                "这类问题通常有几种解决方案：",
                "建议你先检查基本配置是否正确。",
                "如果问题仍然存在，可以尝试重启相关服务。"
            ]
        elif any(keyword in input_data.content.lower() for keyword in ['代码', 'code', '编程', 'python']):
            responses = [
                "关于编程问题，我可以为你提供一些建议。",
                "首先，确保你的代码逻辑是正确的。",
                "其次，注意变量名和函数名的规范性。",
                "最后，记得添加适当的错误处理和注释。",
                "如果需要具体的代码示例，请告诉我更多细节。"
            ]

        accumulated_content = ""

        # 模拟流式输出
        for i, response_part in enumerate(responses):
            # 模拟网络延迟
            await asyncio.sleep(random.uniform(0.1, 0.5))

            # 将每个响应部分分成更小的块来模拟真实的流式输出
            words = response_part.split()
            for j, word in enumerate(words):
                content = word + " "
                accumulated_content += content

                # 模拟偶尔的停顿
                if random.random() > 0.8:
                    await asyncio.sleep(random.uniform(0.05, 0.2))

                # 使用 .json() 方法直接生成 JSON 字符串
                response_obj = ChatContentMainResp(
                    cid=str(uuid.uuid4()),
                    conversation_id=1,
                    user_role_id=1,
                    role="assistant",
                    content=content,
                    is_partial=False,
                    is_complete=True,
                    chat_type=ChatMessageType.NORMAL_MESSAGE_ASSISTANT_PART
                )
                yield response_obj.model_dump_json() + "\n"

            # 在句子结束后稍作停顿
            await asyncio.sleep(random.uniform(0.2, 0.4))

        # 发送最终完整响应
        final_response = ChatContentMainResp(
            cid=str(uuid.uuid4()),
            conversation_id=1,
            user_role_id=1,
            role="assistant",
            content=accumulated_content,
            is_partial=True,
            is_complete=False,
            chat_type=ChatMessageType.NORMAL_MESSAGE_ASSISTANT
        )
        yield final_response.model_dump_json() + "\n"

    except Exception as e:
        error_response = ChatContentMainResp(
            cid=str(uuid.uuid4()),
            conversation_id=1,
            user_role_id=1,
            role="exception",
            content=str(e),
            is_partial=True,
            is_complete=False,
            chat_type=ChatMessageType.EXCLUDE_MESSAGE_EXCEPTION
        )
        yield error_response.model_dump_json() + "\n"


# 独立的 LLM API，供外部调用
@providers_router.post("/llm")
async def call_llm(message: ChatContentMainResp):
    chat_content_service: ChatContentService = Depends(get_chat_content_service)
    resp = chat_content_service.get_by_conversation_id(message.conversation_id)
    return StreamingResponse(stream_llm_response(message), media_type="text/event-stream")


# 抽取的流式响应生成器函数
async def stream_llm_response(input_data: ChatContentMain) -> AsyncGenerator[str, None]:
    try:
        # 准备消息
        api_messages = chat.prepare_messages(input_data.content)
        # 调用流式 API
        response = chat.call_api(api_messages, stream=True)
        accumulated_content = ""
        for chunk in response:
            chunk_data = chat.parse_chunk(chunk)
            content = chunk_data.get("content")
            if content:  # 仅发送非空内容
                accumulated_content += content
                # 使用 .json() 方法直接生成 JSON 字符串
                response_obj = ChatContentMainResp(
                    cid=str(uuid.uuid4()),
                    conversation_id=1,
                    user_role_id=1,
                    role="assistant",
                    content=content,
                    is_partial=False,
                    is_complete=True,
                    chat_type=ChatMessageType.NORMAL_MESSAGE_ASSISTANT_PART
                )
                yield response_obj.model_dump_json() + "\n"

        # 发送最终完整响应
        final_response = ChatContent(
            cid=str(uuid.uuid4()),
            conversation_id=1,
            user_role_id=1,
            role="assistant",
            content=accumulated_content,
            is_partial=True,
            is_complete=False,
            chat_type=ChatMessageType.NORMAL_MESSAGE_ASSISTANT
        )
        chat.chat.set_message(final_response)
        yield final_response.model_dump_json() + "\n"

    except Exception as e:
        print(f"错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

