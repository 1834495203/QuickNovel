# Gemini 类
import os
from typing import Any, Dict, List, Optional

import yaml
from google import genai

from core.entity.Models import ChatContent, ChatMessageType
from core.providers.ProvidersBase import AbstractChat


class GeminiChat(AbstractChat):
    def __init__(self, model: str, api_key: Optional[str] = None):
        super().__init__(model)
        if api_key is None or api_key == '':
            BASE_DIR = os.path.dirname(__file__)  # 获取 当前文件 所在目录
            with open(f"{BASE_DIR}\config\\api.yml") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                api_key = config['resource']['gemini']['api']
        self.client = self._create_client(api_key)
        self.model = model

    def call_api(self, messages: List[ChatContent], stream: bool) -> Any:
        if stream:
            resp = self.client.models.generate_content_stream(
                model=self.model,
                contents=[msg.content for msg in messages],
            )
            return resp
        resp = self.client.models.generate_content(
            model=self.model,
            contents=[msg.content for msg in messages],
        ).text
        return resp

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        return {
            "content": response
        }

    def add_system_message(self, system_content: str,
                           chat_type: ChatMessageType = ChatMessageType.SYSTEM_PROMPT) -> None:
        self.chat.messages.append(
            ChatContent(
                role="system",
                content=system_content,
                chat_type=chat_type
            )
        )

    def prepare_messages(self, user_input: str, system_prompt: Optional[str] = None):
        messages = []
        for msg in self.chat.messages:
            messages.append(msg)
        messages.append(user_input)
        return messages

    def parse_chunk(self, chunk: Any) -> Dict[str, Any]:
        return {"content": chunk.text}

    def _create_client(self, api_key: str, **kwargs):
        return genai.Client(api_key=api_key)


class GeminiEmbeddingChat(GeminiChat):

    def prepare_messages(self, user_input: str, system_prompt: Optional[str] = None):
        return user_input

    def call_api(self, messages: List[Dict[str, str]], stream: bool) -> Any:
        print("使用嵌入模型")
        resp = self.client.models.embed_content(
            model=self.model,
            contents=messages,
        ).embeddings
        return resp[0].values