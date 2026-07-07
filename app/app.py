import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="肖战公开资料 Agent")

st.title("🎤 肖战公开资料 Agent")
st.caption("当前版本：基于 knowledge 文件夹中的 Markdown 资料回答。")

github_token = os.getenv("GITHUB_TOKEN")

if not github_token:
    st.error("没有找到 GITHUB_TOKEN。请检查 .env 文件。")
    st.stop()

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=github_token,
)

def load_knowledge():
    knowledge_dir = Path("knowledge")
    docs = []

    for path in knowledge_dir.glob("*.md"):
        docs.append(f"\n\n---\n文件名：{path.name}\n\n{path.read_text(encoding='utf-8')}")

    return "\n".join(docs)

knowledge = load_knowledge()

question = st.text_input("请输入问题：", placeholder="例如：这个 Agent 的目标是什么？")

if st.button("发送") and question:
    if not knowledge.strip():
        st.warning("knowledge 文件夹里还没有 Markdown 资料。")
        st.stop()

    with st.spinner("正在检索资料并生成回答..."):
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
你是“肖战公开资料问答 Agent”。

你只能根据提供的知识库内容回答。
如果知识库中没有明确依据，必须回答：
“现有公开资料库中未找到明确依据。”

禁止编造。
禁止回答私人生活、绯闻、争议、未证实传闻。
回答时尽量说明依据来自哪个文件或哪类资料。
""",
                },
                {
                    "role": "user",
                    "content": f"""
以下是知识库内容：

{knowledge}

用户问题：
{question}

请只基于知识库回答。
""",
                },
            ],
        )

        st.write(response.choices[0].message.content)


