import asyncio
from typing import AsyncGenerator, List

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

from core.mapper.CharacterNovelMapper import CharacterNovelMapperInterface
from core.mapper.NovelMapper import NovelMapperInterface
from core.utils.LogConfig import get_logger

logging = get_logger(__name__)


class ProviderService:
    def __init__(self,
                 novel_mapper: NovelMapperInterface,
                 character_novel_mapper: CharacterNovelMapperInterface,
                 model: str,
                 streaming: bool,
                 temperature: float = 1,
                 base_url: str = "https://api.deepseek.com/"):
        self.novel_mapper = novel_mapper
        self.character_novel_mapper = character_novel_mapper

        self.llm = ChatOpenAI(
            model=model,
            streaming=streaming,
            temperature=temperature,
            base_url=base_url,
        )

    async def generate_llm_response(self, prompt: str, novel_id: int = None) -> AsyncGenerator[str, None]:
        """
        使用 LangChain 的 LLM 生成流式响应。
        """
        # 定义提示模板（这里不需要 {novel} 和 {prompt} 占位符，而是直接构建消息列表）
        # system_message 和 user_message 会在构建 messages 列表时直接传入

        # 不需要 prompt_template 了，直接构建消息列表

        novel_messages = []
        characters_info = []
        if novel_id is not None:
            novel_messages = self.generate_scene_messages(novel_id)  # 修改这里，返回消息列表
            characters_info = self.generate_character_messages(novel_id)

        # 构建最终的 messages 列表
        messages = [
            SystemMessage(content="""
你是一个交互式小说系统，负责扮演故事中的所有角色，并生成对应的交互和场景描述。
- 每个角色的知识有限，没有角色能完全了解其他角色或事件的真相。
- 用户可以扮演任何角色，也可以作为上帝视角。
- 角色应保持一致的性格，展现多样化的情感和反应，避免单一化刻画。
- 场景描述应包括环境细节、氛围和感官体验，以营造沉浸感。
- 角色应具有清晰的关系网络和互动模式。
- 对话应反映每个角色的独特语言风格、词汇习惯和思维方式。
- 角色应有自己的目标、恐惧和动机，这些会影响他们的决策。
- 场景应具有连贯性，角色反应需考虑过往互动和个人背景。
- 对话字数不能过少，时刻注意章节和情景设定，事件之间不能自相矛盾。
            """)
        ]

        # 添加角色信息
        messages.extend(characters_info)

        # 添加历史小说消息
        messages.extend(novel_messages)

        logging.info(f"添加历史小说消息:{novel_messages}")
        logging.info(f"用户消息:{prompt}")

        async for chunk in self.llm.astream(messages):
            # 提取 LLM 输出的内容
            content = chunk.content
            if content:
                yield content
                await asyncio.sleep(0.1)  # 模拟生成延迟，保持与原代码一致
        yield "[DONE]"  # 发送结束标记

    def generate_scene_messages(self, novel_id: int) -> List[AIMessage | HumanMessage]:  # 修改返回类型
        """
        将 ResponseAllNovelDto 对象转换为 LangChain 消息列表。

        Args:
            novel_id: ResponseAllNovelDto 对象，包含小说、章节、情景和对话信息。

        Returns:
            List[BaseMessage]: 历史对话的 LangChain 消息列表。
        """
        novel = self.novel_mapper.get_novel_by_id(novel_id)

        messages = []

        # 遍历章节和情景
        if novel.chapter:
            for chapter in novel.chapter:
                chapter_title = chapter.chapter_title or f"章节 {chapter.chapter_number}"
                chapter_desc = chapter.chapter_desc or "无描述"

                # 添加章节和小说信息作为系统消息或特定的 HumanMessage
                # 为了简洁，这里直接将它们作为 HumanMessage 的一部分，或者合并到情景描述中
                # 也可以考虑更复杂的处理方式，例如将它们作为单独的 SystemMessage

                if chapter.scene:
                    chapter_info = f"### 情景信息\n" \
                                     f"#### 小说信息\n" \
                                     f"- **名字**: {novel.novel_name}\n" \
                                     f"- **描述**: {novel.novel_desc}\n\n" \
                                     f"#### 章节信息\n" \
                                     f"- **章节**: {chapter_title}\n" \
                                     f"- **描述**: {chapter_desc}\n\n"

                    messages.append(HumanMessage(content=chapter_info))  # 将章节信息作为一条用户消息

                    for scene in chapter.scene:
                        # 情景信息作为 HumanMessage 的一部分
                        scene_info = f"#### 情景信息\n" \
                                     f"- **情景名称**: {scene.scene_name}\n" \
                                     f"- **情景描述**: {scene.scene_desc or '无描述'}\n"

                        messages.append(HumanMessage(content=scene_info))  # 将情景信息作为一条用户消息

                        # 对话信息转换为 LangChain 消息对象
                        if scene.conversation:
                            for conv in scene.conversation:
                                if conv.role == "user":
                                    messages.append(HumanMessage(content=conv.content))
                                elif conv.role == "assistant":
                                    messages.append(AIMessage(content=conv.content))
                                # 还可以处理其他角色，例如 "system" 角色
                                # else:
                                #     messages.append(HumanMessage(content=f"{conv.role}: {conv.content}"))

        return messages

    def generate_character_messages(self, novel_id: int) -> List[HumanMessage]:
        characters = self.character_novel_mapper.get_connect_characters_by_novel_id(novel_id)
        messages = []
        for character in characters:
            prompt = f"角色名称: {character.name}\n"

            prompt += f"描述: {character.description}\n\n"

            prompt += "背景故事:\n"
            prompt += f"{character.background_story}\n\n"

            prompt += "性格特征:\n"
            for trait in character.trait:
                prompt += f"- {trait.label}: {trait.description}\n"
            prompt += "\n"

            prompt += "标志性特征:\n"
            for distinctive in character.distinctive:
                prompt += f"- {distinctive.name}: {distinctive.content}\n"
            prompt += "\n"

            prompt += "对话示例:\n"
            for speak in character.speak:
                prompt += f"{speak.role}: {speak.content}\n"
                prompt += f"回复: {speak.reply}\n"

            messages.append(HumanMessage(content=prompt))
        return messages

