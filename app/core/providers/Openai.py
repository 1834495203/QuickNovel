# OpenAIChat 类（不变）
from typing import List, Dict, Any

from openai import OpenAI

from core.providers.ProvidersBase import AbstractChat


class OpenAIChat(AbstractChat):
    def __init__(self, api_key: str, model: str):
        super().__init__(model)
        self.client = self._create_client(api_key)
        self.tools = None

    def _create_client(self, api_key: str, **kwargs) -> OpenAI:
        return OpenAI(api_key=api_key)

    def use_tools(self, tools):
        self.tools = tools
        return self

    def call_api(self, messages: List[Dict[str, str]], stream: bool) -> Any:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            tools=self.tools,
        )

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        return {
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls,
            "finish_reason": response.choices[0].finish_reason,
            "message": response.choices[0].message
        }

    def parse_chunk(self, chunk: Any) -> Dict[str, Any]:
        return {
            "content": chunk.choices[0].delta.content,
            "tool_calls": chunk.choices[0].delta.tool_calls
        }
