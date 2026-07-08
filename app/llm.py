"""
LLM 调用模块
统一管理 GitHub Models
"""

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.config import DEFAULT_MODEL

load_dotenv()


class LLMClient:

    def __init__(self):

        token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise RuntimeError(
                "没有找到 GITHUB_TOKEN，请检查 .env 文件。"
            )

        self.client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=token,
        )

    def chat(
        self,
        question: str,
        context: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.2,
        max_tokens: int = 1200,
        system_prompt: Optional[str] = None,
    ):

        if system_prompt is None:

            system_prompt = """
你是“肖战公开资料知识库 AI”。

你的回答必须遵守以下规则：

1. 只能依据提供的知识库回答。
2. 如果知识库中没有明确依据，请回答：
   "现有公开资料库中未找到明确依据。"
3. 不允许编造。
4. 不回答私人生活、绯闻、未证实消息。
5. 尽量使用中文。
6. 如果资料存在冲突，要说明资料存在不同说法。
7. 回答最后增加：

资料来源：
- xxx
- xxx
"""

        prompt = f"""
========================
知识库
========================

{context}

========================
用户问题
========================

{question}
"""

        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response.choices[0].message.content.strip()


_client = None


def get_llm():

    global _client

    if _client is None:
        _client = LLMClient()

    return _client
