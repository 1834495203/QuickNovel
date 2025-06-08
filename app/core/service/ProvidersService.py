import asyncio
import random
import uuid
from typing import Optional, AsyncGenerator

from core.entity.CharacterCard import CharacterCard
from core.entity.Conversation import ChatContentMainResp, ChatMessageType
from core.providers.Deepseek import DeepSeekChat


# 抽取的流式响应生成器函数
async def stream_llm_response(input_data: ChatContentMainResp,
                              character: Optional[CharacterCard] = None) -> AsyncGenerator[str, None]:
    chat = DeepSeekChat(model="deepseek-chat", conversation_id=input_data.conversation_id)
    # 准备消息
    sys_prompt = None
    if character:
        sys_prompt = f"在对话中请严格扮演以下角色进行对话: \n {character}"
    api_messages = chat.prepare_messages(input_data.to_chat_content_main(), system_prompt=sys_prompt)

    print(api_messages)

    # 调用流式 API
    response = chat.call_api(api_messages, stream=True)
    accumulated_content = ""
    for chunk in response:
        chunk_data = chat.parse_chunk(chunk)
        content = chunk_data.get("content")
        if content:  # 仅发送非空内容
            # 模拟偶尔的停顿
            if random.random() > 0.8:
                await asyncio.sleep(random.uniform(0.05, 0.2))

            accumulated_content += content
            # 使用 .json() 方法直接生成 JSON 字符串
            response_obj = ChatContentMainResp(
                cid=str(uuid.uuid4()),
                conversation_id=input_data.conversation_id,
                user_role_id=input_data.user_role_id,
                role="assistant",
                content=content,
                chat_type=ChatMessageType.NORMAL_MESSAGE_ASSISTANT_PART
            )
            yield response_obj.model_dump_json() + "\n"

    # 发送最终完整响应
    final_response = ChatContentMainResp(
        cid=str(uuid.uuid4()),
        conversation_id=input_data.conversation_id,
        user_role_id=input_data.user_role_id,
        role="assistant",
        content=accumulated_content,
        chat_type=ChatMessageType.NORMAL_MESSAGE_ASSISTANT
    )

    chat.chat.set_message(final_response, is_save=True)
    yield final_response.model_dump_json() + "\n"