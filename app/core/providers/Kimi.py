# KimiChat 类
import os
from typing import Any, Dict, Optional

import yaml
from openai import OpenAI

from commands.Regisrty import CommandRegistry
from providers.Openai import OpenAIChat


class KimiChat(OpenAIChat):
    def __init__(self, model: str, api_key: Optional[str] = None):
        if api_key is None:
            BASE_DIR = os.path.dirname(__file__)  # 获取 当前文件 所在目录
            with open(f"{BASE_DIR}\config\\api.yml") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                api_key = config['resource']['kimi']['api']
        super().__init__(api_key, model)
        if model not in ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k", "moonshot-v1-auto"]:
            raise ValueError("模型必须是 moonshot-v1-8k moonshot-v1-32k moonshot-v1-128k moonshot-v1-auto")

    def _create_client(self, api_key: str, **kwargs) -> OpenAI:
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")


