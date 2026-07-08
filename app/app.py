import os
from pathlib import Path

import chromadb
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

DB_DIR = "vector_db"
COLLECTION_NAME = "xiao_zhan_knowledge"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "openai/gpt-4o-mini"

st.set_page_config(page_title="肖战公开资料 Agent", layout="wide")

st.title("🎤 肖战公开资料 Agent")
st.caption("基于公开资料知识库回答，支持来源引用。")

github_token = os.getenv("GITHUB_TOKEN")

if not github_token:
    st.error("没有找到 GITHUB_TOKEN。请检查 .env 文件。")
    st.stop()

if not Path(DB_DIR).exists():
    st.error("没有找到 vector_db，需要先构建向量知识库。")

    st.code("python scripts/build_index.py")

    if st.button("一键构建向量知识库"):
        import subprocess
        import sys

        with st.spinner("正在构建向量知识库..."):
            result = subprocess.run(
                [sys.executable, "scripts/build_index.py"],
                capture_output=True,
                text=True,
            )

        if result.returncode == 0:
            st.success("向量知识库构建成功，请刷新页面。")
            st.text(result.stdout)
        else:
            st.error("构建失败。")
            st.text(result.stderr)

    st.stop()


@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)

def load_chroma_collection():
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_collection(COLLECTION_NAME)


@st.cache_resource
def load_llm_client():
    return OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=github_token,
    )

embedder = load_embedding_model()
collection = load_chroma_collection()
client = load_llm_client()

def retrieve_context(question: str, top_k: int = 5):
    query_embedding = embedder.encode([question]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []

    for doc, meta, distance in zip(docs, metadatas, distances):
        source = meta.get("source", "未知来源") if meta else "未知来源"
        retrieved.append(
            {
                "source": source,
                "text": doc,
                "distance": distance,
            }
        )

    return retrieved

def build_prompt(question: str, retrieved_docs):
    context_blocks = []

    for i, item in enumerate(retrieved_docs, start=1):
        context_blocks.append(
            f"【资料{i}】\n"
            f"来源文件：{item['source']}\n"
            f"内容：\n{item['text']}"
        )

    context = "\n\n".join(context_blocks)

    return f"""
你是“肖战公开资料问答 Agent”。

你的任务：
只根据下面提供的公开资料回答用户问题。

严格规则：
1. 只能基于资料回答，不得编造。
2. 如果资料中没有明确依据，回答：“现有公开资料库中未找到明确依据。”
3. 不回答私人生活、绯闻、争议、未证实传闻。
4. 用中文回答。
5. 回答后列出“资料来源”，写出使用到的来源文件名。
6. 如果多个资料内容相互矛盾，要说明“资料存在不一致”，不要自行判断。

用户问题：
{question}

检索到的资料：
{context}
"""

question = st.text_input("请输入问题：", placeholder="例如：肖战有哪些影视作品？")

top_k = st.sidebar.slider("检索资料数量 Top K", 1, 10, 5)
st.sidebar.divider()

if st.sidebar.button("一键更新知识库"):
    import subprocess
    import sys

    with st.spinner("正在运行爬虫并重建向量库..."):
        result = subprocess.run(
            [sys.executable, "scripts/update.py"],
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
         st.cache_resource.clear()
         st.sidebar.success("知识库更新完成，缓存已清理，请刷新页面后再提问。")
         st.sidebar.text(result.stdout[-1000:])

    else:
        st.sidebar.error("知识库更新失败。")
        st.sidebar.text(result.stderr[-1000:])

if st.button("发送") and question:
    with st.spinner("正在检索知识库..."):
        retrieved_docs = retrieve_context(question, top_k=top_k)

    if not retrieved_docs:
        st.write("现有公开资料库中未找到明确依据。")
        st.stop()

    with st.expander("查看检索到的资料"):
        for i, item in enumerate(retrieved_docs, start=1):
            st.markdown(f"### 资料 {i}")
            st.write(f"来源文件：{item['source']}")
            st.write(f"距离分数：{item['distance']}")
            st.write(item["text"][:1200])

    prompt = build_prompt(question, retrieved_docs)

    with st.spinner("正在生成回答..."):
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是严谨的中文资料问答助手，只能基于提供资料回答。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

    st.markdown(response.choices[0].message.content)





