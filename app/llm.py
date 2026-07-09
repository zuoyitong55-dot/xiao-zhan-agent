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
        max_tokens: int = 1500,
        system_prompt: Optional[str] = None,
    ):

        if system_prompt is None:
            system_prompt = """
你是“肖战公开资料问答 Agent”。

你可以结合两类信息回答：

A. 用户提供的知识库检索资料；
B. 你自身已有的公开常识和推理能力。

回答规则：

1. 不再强制只依据知识库回答。
2. 如果答案来自知识库资料，请在对应内容后标注【知识库】。
3. 如果答案来自你的自身公开知识、常识推理或公开常见信息，请在对应内容后标注【模型补充】。
4. 如果知识库资料不足，不要直接拒答，可以使用模型自身公开知识补充，但必须标注【模型补充】。
5. 如果知识库资料与模型自身知识存在冲突，请明确说明：
   “知识库资料与模型知识存在不一致。”
   然后分别列出两边说法。
6. 不回答私人生活、绯闻、争议、未证实传闻。
7. 涉及影视作品、采访、公开活动时，可以结合知识库和自身知识综合回答。
8. 对不确定的信息，要标注“可能需要进一步核验”。
9. 回答要简洁、清楚、分条。
10. 最后必须增加“资料说明”：
   - 【知识库】：列出本次使用到的知识库来源文件名；
   - 【模型补充】：说明哪些内容是根据模型自身公开知识补充的。
11. 不得使用 xxx、示例、占位符作为资料来源。
12. 当用户询问“有哪些影视作品 / 演过哪些电视剧 / 演过哪些电影 / 作品列表”时，优先依据你自身已知的公开影视资料回答；知识库资料只作为补充，不得把检索资料中的相关推荐、网页导航、其他演员作品误当成肖战作品。

"""

        prompt = f"""
下面是系统从知识库中检索到的资料。

这些资料可能不完整，可能包含噪声，也可能没有覆盖用户问题的全部答案。你需要结合知识库资料和你自身已有的公开知识回答。

========================
知识库检索资料
========================

{context}

========================
用户问题
========================

{question}

========================
回答要求
========================

1. 凡是来自知识库资料的内容，标注【知识库】。
2. 凡是来自你自身公开知识或推理补充的内容，标注【模型补充】。
3. 如果知识库资料不足，不要直接拒答，可以用模型公开知识补充。
4. 如果不确定，请说明“可能需要进一步核验”。
5. 最后写“资料说明”。
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

