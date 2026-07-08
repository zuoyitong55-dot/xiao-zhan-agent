"""
Sidebar UI
"""

import streamlit as st

from app.config import (
    MODEL_OPTIONS,
    DEFAULT_TOP_K,
    MAX_TOP_K,
)

from app.utils import (
    count_markdown_files,
    latest_update_time,
    vector_db_exists,
)


def render_sidebar():

    st.sidebar.title("🎤 肖战公开资料 Agent")

    st.sidebar.markdown("---")

    model_name = st.sidebar.selectbox(
        "大模型",
        list(MODEL_OPTIONS.keys()),
    )

    top_k = st.sidebar.slider(
        "Top-K 检索数量",
        min_value=1,
        max_value=MAX_TOP_K,
        value=DEFAULT_TOP_K,
    )

    st.sidebar.markdown("---")

    st.sidebar.subheader("📚 知识库")

    st.sidebar.metric(
        "Markdown 文件",
        count_markdown_files(),
    )

    st.sidebar.write(
        "Vector DB：",
        "✅ 已建立" if vector_db_exists() else "❌ 未建立",
    )

    st.sidebar.caption(
        "最后更新："
    )

    st.sidebar.caption(
        latest_update_time()
    )

    st.sidebar.markdown("---")

    update_clicked = st.sidebar.button(
        "🔄 更新知识库",
        use_container_width=True,
    )

    rebuild_clicked = st.sidebar.button(
        "🧠 重建向量库",
        use_container_width=True,
    )

    return {
        "model_name": model_name,
        "model_id": MODEL_OPTIONS[model_name],
        "top_k": top_k,
        "update_clicked": update_clicked,
        "rebuild_clicked": rebuild_clicked,
    }
