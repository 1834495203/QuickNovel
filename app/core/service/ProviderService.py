import asyncio
from typing import AsyncGenerator, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from core.mapper.NovelMapper import NovelMapperInterface


class ProviderService:
    def __init__(self,
                 novel_mapper: NovelMapperInterface,
                 model: str,
                 streaming: bool,
                 temperature: float = 1,
                 base_url: str = "https://api.deepseek.com"):
        self.novel_mapper = novel_mapper

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
        # 定义提示模板

        if novel_id is not None:
            prompts = self.generate_scene_prompts(novel_id=novel_id)

        prompt_template = ChatPromptTemplate.from_messages([
            ("user", "{prompt}")
        ])

        # 创建 LangChain 的链
        chain = prompt_template | self.llm

        # 流式生成响应
        async for chunk in chain.astream({"prompt": prompt}):
            # 提取 LLM 输出的内容
            content = chunk.content
            if content:
                yield content + " "  # 添加空格以模拟单词分隔
                await asyncio.sleep(0.1)  # 模拟生成延迟，保持与原代码一致
        yield "[DONE]"  # 发送结束标记

    def generate_scene_prompts(self, novel_id: int) -> List[str]:
        """
        将 ResponseAllNovelDto 对象转换为按情景划分的 prompt 列表。

        Args:
            novel_id: ResponseAllNovelDto 对象，包含小说、章节、情景和对话信息。

        Returns:
            List[str]: 按情景划分的 prompt 字符串列表。
        """
        novel = self.novel_mapper.get_novel_by_id(novel_id)

        prompts = []

        # 遍历章节和情景
        if novel.chapter:
            for chapter in novel.chapter:
                chapter_title = chapter.chapter_title or f"章节 {chapter.chapter_number}"
                chapter_desc = chapter.chapter_desc or "无描述"

                if chapter.scene:
                    for scene in chapter.scene:
                        # 构造单个情景的 prompt
                        prompt = f"### 情景 Prompt\n\n"
                        prompt += "#### 小说信息\n"
                        prompt += f"- **名字**: {novel.novel_name}\n"
                        prompt += f"- **描述**: {novel.novel_desc}\n\n"

                        prompt += "#### 章节信息\n"
                        prompt += f"- **章节**: {chapter_title}\n"
                        prompt += f"- **描述**: {chapter_desc}\n\n"

                        prompt += "#### 情景信息\n"
                        prompt += f"- **情景名称**: {scene.scene_name}\n"
                        prompt += f"- **情景描述**: {scene.scene_desc or '无描述'}\n"

                        # 对话信息
                        if scene.conversation:
                            prompt += "- **对话**:\n"
                            for conv in scene.conversation:
                                prompt += f"  - **角色**: {conv.role}, **内容**: \"{conv.content}\"\n"
                        else:
                            prompt += "- **对话**: 无\n"

                        prompts.append(prompt)

        return prompts
