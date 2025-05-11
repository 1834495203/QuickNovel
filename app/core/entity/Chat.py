from typing import Optional, List

from core.entity.Models import ChatMessageType, ChatContent


# 原始的 Chat 类（移除数据库相关逻辑）
class Chat:
    def __init__(self,
                 messages: Optional[List[ChatContent]] = None,):
        self.messages: List[ChatContent] = messages or []

    def set_message(self, messages: ChatContent):
        self.messages.append(messages)
        return self

    def set_messages(self, messages: List[ChatContent]):
        for msg_ in messages:
            self.set_message(msg_)
        return self

    def get_messages_by_type(self, message_type: ChatMessageType) -> List[ChatContent]:
        """
        根据指定的 ChatMessageType 返回对应类型的消息列表

        Args:
            message_type: 要筛选的消息类型

        Returns:
            List[ChatContent]: 指定类型的消息列表
        """
        return [message for message in self.messages if message.chat_type == message_type]

    def get_messages_by_types(self, message_types: List[ChatMessageType]) -> List[ChatContent]:
        """
        根据指定的多个 ChatMessageType 返回对应类型的消息列表

        Args:
            message_types: 要筛选的消息类型列表

        Returns:
            List[ChatContent]: 符合指定类型之一的消息列表
        """
        return [message for message in self.messages if message.chat_type in message_types]

    def has_message_type(self, message_type: ChatMessageType) -> bool:
        """
        检查是否存在指定类型的消息

        Args:
            message_type: 要检查的消息类型

        Returns:
            bool: 如果存在指定类型的消息则返回 True，否则返回 False
        """
        return any(message.chat_type == message_type for message in self.messages)

    def count_by_type(self, message_type: ChatMessageType) -> int:
        """
        统计指定类型消息的数量

        Args:
            message_type: 要统计的消息类型

        Returns:
            int: 指定类型的消息数量
        """
        return sum(1 for message in self.messages if message.chat_type == message_type)

    def merge_messages(self, threshold: int, core_count: int, kk:int) -> int:
        """
        合并消息的核心算法
        1. 当消息数超过阈值时，从最后3条开始尝试合并
        2. 合并策略分多个层级，优先合并低层级的消息
        3. 保证合并后消息数不会低于核心保留数
        """
        while len(self.messages) > threshold:
            merged = False

            start_idx = 0
            while True:
                # 基础校验条件
                if len(self.messages) < 3:
                    break

                # 预计算合并后的消息数量
                potential_length = len(self.messages) - 2
                if potential_length < core_count:
                    break

                # 检查最后三条消息
                # start_idx = len(self.messages) - 3
                candidates = self.messages[start_idx:start_idx + 3]

                # 判断是否符合当前合并层级的条件
                if all(msg.merge_count == kk for msg in candidates):
                    # 执行合并操作
                    merged_content = self._create_merged_message(candidates, kk + 1)
                    self.messages = self.messages[:start_idx] + [merged_content] + self.messages[start_idx+3:]
                    merged = True
                    break
                elif start_idx <= len(self.messages) - core_count - 3:
                    start_idx += 1
                else:
                    # 提升合并层级
                    kk += 1
                    merged = True
                    break

            if not merged:
                break  # 无法进行更多合并
        return kk

    @staticmethod
    def _create_merged_message(messages: List[ChatContent], new_merge_count: int) -> ChatContent:
        """创建合并后的消息对象"""
        # 这里假装调用了一个总结API，实际应该替换为真实逻辑
        summarized_content = f"[合并消息 x{len(messages)}]\n" + "\n".join(
            str(msg.content) for msg in messages
        )

        return ChatContent(
            role="system",
            content=summarized_content,
            merge_count=new_merge_count,
            chat_type=ChatMessageType.SYSTEM_PROMPT,
            user_card=messages[-1].user_card if messages else None,
            # 其他字段保持默认值或取最后一条消息的值
        )


if __name__ == "__main__":
    # 初始化对话历史
    chat = Chat()

    # 添加测试消息（假设都是merge_count=0的消息）
    k = 0
    for i in range(40):
        chat.messages.append(ChatContent(
            role="user",
            content=f"消息{i}",
            merge_count=0
        ))
        # 执行合并（阈值=10，核心保留=5）
        k = chat.merge_messages(threshold=10, core_count=5, kk=k)

    print(f"最终消息数: {len(chat.messages)}")
    for msg in chat.messages:
        print(f"[合并次数{msg.merge_count}] {msg.content}")