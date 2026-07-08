import subprocess
import sys

import streamlit as st
from dotenv import load_dotenv

from app.config import MODEL_OPTIONS, DEFAULT_TOP_K, MAX_TOP_K
from app.rag import get_retriever
from app.llm import get_llm
from app.utils import (
    vector_db_exists,
    count_markdown_files,
    latest_update_time,
)

load_dotenv()

st.set_page_config(
    page_title="肖战公开资料 Agent",
    page_icon="🎤",
    layout="wide",
)

st.title("🎤 肖战公开资料 Agent")
st.caption("基于公开资料知识库的 RAG 问答系统。")

with st.sidebar:
    st.header("设置")

    model_name = st.selectbox(
        "选择模型",
        list(MODEL_OPTIONS.keys()),
    )

    model_id = MODEL_OPTIONS[model_name]

    top_k = st.slider(
        "检索资料数量 Top-K",
        min_value=1,
        max_value=MAX_TOP_K,
        value=DEFAULT_TOP_K,
    )

    st.divider()

    st.subheader("知识库状态")

    st.write(f"Markdown 文件数：{count_markdown_files()}")
    st.write(f"最后更新：{latest_update_time()}")

    if vector_db_exists():
        st.success("Vector DB 已建立")
    else:
        st.warning("Vector DB 未建立")

    if st.button("重建向量库"):
        with st.spinner("正在重建向量库..."):
            result = subprocess.run(
                [sys.executable, "scripts/build_index.py"],
                capture_output=True,
                text=True,
            )

        if result.returncode == 0:
            st.success("向量库重建成功，请刷新页面。")
            st.text(result.stdout[-1500:])
        else:
            st.error("向量库重建失败。")
            st.text(result.stderr[-1500:])

    if st.button("更新知识库"):
        with st.spinner("正在更新知识库..."):
            result = subprocess.run(
                [sys.executable, "scripts/update.py"],
                capture_output=True,
                text=True,
            )

        if result.returncode == 0:
            st.success("知识库更新成功，请刷新页面。")
            st.text(result.stdout[-1500:])
        else:
            st.error("知识库更新失败。")
            st.text(result.stderr[-1500:])

if not vector_db_exists():
    st.warning("尚未建立向量数据库。请先点击左侧“重建向量库”。")
    st.stop()

question = st.text_input(
    "请输入问题",
    placeholder="例如：肖战有哪些影视作品？",
)

if st.button("发送") and question:
    with st.spinner("正在检索知识库..."):
        retriever = get_retriever()
        results = retriever.search(question, top_k=top_k)
        context = retriever.build_context(results)

    with st.expander("查看检索到的资料"):
        for i, item in enumerate(results, start=1):
            st.markdown(f"### 资料 {i}")
            st.write("来源：", item.get("source", ""))
            st.write("分类：", item.get("category", ""))
            st.write("链接：", item.get("url", ""))
            st.write("距离：", item.get("distance", ""))
            st.code(item.get("content", "")[:1200], language="markdown")

    with st.spinner("正在生成回答..."):
        llm = get_llm()
        answer = llm.chat(
            question=question,
            context=context,
            model=model_id,
        )

    st.markdown(answer)







