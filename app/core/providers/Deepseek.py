# DeepSeekChat 类（不变）
import os
from typing import Any, Dict, Optional

import yaml
from openai import OpenAI

from core.providers.Openai import OpenAIChat


class DeepSeekChat(OpenAIChat):
    def __init__(self, model: str, api_key: Optional[str] = None, conversation_id=-1):
        if api_key is None:
            BASE_DIR = os.path.dirname(__file__)  # 获取 当前文件 所在目录
            with open(f"{BASE_DIR}\config\\api.yml") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                api_key = config['resource']['deepseek']['api']
        super().__init__(api_key, model, conversation_id=conversation_id)
        if model not in ["deepseek-reasoner", "deepseek-chat"]:
            raise ValueError("模型必须是 'deepseek-reasoner' 或 'deepseek-chat'")

    def _create_client(self, api_key: str, **kwargs) -> OpenAI:
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        return {
            "content": response.choices[0].message.content,
            "reasoning_content": getattr(response.choices[0].message, "reasoning_content", None)
        }

    def parse_chunk(self, chunk: Any) -> Dict[str, Any]:
        return {
            "content": chunk.choices[0].delta.content,
            "reasoning_content": getattr(chunk.choices[0].delta, "reasoning_content", None)
        }
