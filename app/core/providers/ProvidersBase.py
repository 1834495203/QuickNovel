from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import uuid4
import time
from dataclasses import dataclass

from core.entity.Models import ChatContent, ChatMessageType, Chat


# 用于存储单次token使用记录的数据类
@dataclass
class TokenUsage:
    conversation_id: str
    timestamp: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


# 修改后的 AbstractChat 类，使用成员变量存储token数据
class AbstractChat(ABC):
    def __init__(self, model: str):
        """
        初始化抽象聊天类
        """
        self.model = model
        self.chat = Chat(messages=[])

        self.client: Any = None
        self.conversation_id = str(uuid4())  # 为每个对话分配唯一ID
        self.token_usage_history: List[TokenUsage] = []  # 存储token使用历史
        self.total_token_usage: Dict[str, int] = {  # 统计累计token使用
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0
        }

    def prepare_messages(self, user_input: str, system_prompt: Optional[str] = None) -> List[Any]:
        """
        准备消息：将用户输入添加到聊天记录并转换为 API 格式
        """
        if system_prompt and not any(msg.role == "system" for msg in self.chat.messages):
            self.chat.messages.append(ChatContent(
                role="system",
                content=system_prompt,
                reasoning_content=None,
                tool_calls=None
            ))

        if user_input is not None:
            user_message = ChatContent(
                role="user",
                content=user_input,
                reasoning_content=None,
                tool_calls=None
            )
            self.chat.messages.append(user_message)

        messages = []
        for msg in self.chat.messages:
            messages.append({"role": msg.role, "content": msg.content,
                             "tool_call_id": msg.tool_call_id, "name": msg.name})
        return messages

    @abstractmethod
    def _create_client(self, api_key: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def call_api(self, messages: List[Dict[str, str]], stream: bool) -> Any:
        raise NotImplementedError('请创建调用api方式！')

    @abstractmethod
    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """
        解析API响应，提取内容和token使用数据
        """
        # 假设 response 是 OpenAI API 的返回对象，包含 usage 字段
        content = response.choices[0].message.content
        response_data = {
            "content": content,
            "reasoning_content": None,
            "tool_calls": None,
            "message": None,
            "finish_reason": response.choices[0].finish_reason
        }
        return response_data

    @staticmethod
    def _parse_token_usage(response_data: Dict[str, Any], response: Any) -> Optional[Dict[str, Any]]:
        usage = response.usage if hasattr(response, 'usage') else None
        if usage:
            response_data.update({
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            })
            return response_data
        return response_data

    @abstractmethod
    def parse_chunk(self, chunk: Any) -> Dict[str, Any]:
        pass

    async def chatting(self, user_input: str | List[str] = None,
                 stream: bool = False, system_prompt: Optional[str] = None) -> ChatContent:
        """
        与模型进行聊天，处理用户输入并返回模型响应，同时记录token使用
        """
        if self.client is None:
            raise ValueError("客户端未初始化")

        try:
            api_messages = self.prepare_messages(user_input, system_prompt)

            response = self.call_api(api_messages, stream)
            if stream:
                raise NotImplementedError("Streaming should be handled by ChatInteraction")
            else:
                response_data = self._parse_response(response)
                response_data = self._parse_token_usage(response_data, response)
                assistant_message = ChatContent(
                    role="assistant",
                    content=response_data.get("content"),
                    reasoning_content=response_data.get("reasoning_content"),
                    tool_calls=response_data.get("tool_calls"),
                    message=response_data.get("message"),
                    finish_reason=response_data.get("finish_reason"),
                )
                self.chat.messages.append(assistant_message)

            return assistant_message

        except Exception as e:
            raise ValueError(f"API 调用失败: {str(e)}")

    def print_current_response(self) -> None:
        if not self.chat.messages or self.chat.messages[-1].role != "assistant":
            print("当前没有模型响应可打印")
            return
        print(self.chat.messages[-1])
        print("-" * 50)

    def print_chat_history(self) -> None:
        if not self.chat.messages:
            print("聊天记录为空")
            return
        print("聊天记录:")
        for msg in self.chat.messages:
            print(msg)
            print("-" * 50)

    def add_system_message(self, system_content: str,
                           chat_type: ChatMessageType = ChatMessageType.SYSTEM_PROMPT) -> None:
        system_message = ChatContent(
            role="system",
            content=system_content,
            reasoning_content=None,
            tool_calls=None,
            chat_type=chat_type
        )
        self.chat.messages.append(system_message)

    def clear_chat_history(self) -> None:
        self.chat.messages = []
        self.token_usage_history = []  # 清空token使用历史
        self.total_token_usage = {  # 重置累计token使用量
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0
        }
        self.conversation_id = str(uuid4())  # 重置对话ID

    def whoami(self) -> str:
        return self.model

    def get_token_usage(self, conversation_id: Optional[str] = None) -> Dict[str, int]:
        """
        获取指定对话或所有对话的累计token使用量
        """
        if conversation_id:
            prompt_tokens = sum(usage.prompt_tokens for usage in self.token_usage_history
                                if usage.conversation_id == conversation_id)
            completion_tokens = sum(usage.completion_tokens for usage in self.token_usage_history
                                    if usage.conversation_id == conversation_id)
            total_tokens = sum(usage.total_tokens for usage in self.token_usage_history
                               if usage.conversation_id == conversation_id)
        else:
            prompt_tokens = self.total_token_usage["total_prompt_tokens"]
            completion_tokens = self.total_token_usage["total_completion_tokens"]
            total_tokens = self.total_token_usage["total_tokens"]
        return {
            "total_prompt_tokens": prompt_tokens,
            "total_completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

    def print_token_usage_history(self, conversation_id: Optional[str] = None) -> None:
        """
        打印token使用历史
        """
        history = [usage for usage in self.token_usage_history
                   if not conversation_id or usage.conversation_id == conversation_id]
        if not history:
            print("没有token使用记录")
            return
        print("Token使用历史:")
        for usage in history:
            print(f"对话ID: {usage.conversation_id}, 时间: {time.ctime(usage.timestamp)}")
            print(f"提示Token: {usage.prompt_tokens}, 完成Token: {usage.completion_tokens}, 总Token: {usage.total_tokens}")
            print("-" * 50)