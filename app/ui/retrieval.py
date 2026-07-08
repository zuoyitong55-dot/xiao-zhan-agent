"""
检索结果展示
"""

import streamlit as st


def show_retrieval_results(results):

    if not results:
        return

    with st.expander("🔍 查看检索结果", expanded=False):

        for i, item in enumerate(results, start=1):

            st.markdown(f"### 资料 {i}")

            col1, col2 = st.columns([3, 1])

            with col1:

                st.write("**来源：**", item.get("source", ""))

                st.write("**分类：**", item.get("category", ""))

                url = item.get("url", "")

                if url:
                    st.write("**链接：**", url)

            with col2:

                distance = item.get("distance", 0)

                st.metric(
                    "Distance",
                    f"{distance:.4f}",
                )

            st.code(
                item.get("content", "")[:1200],
                language="markdown",
            )

            st.divider()


def show_sources(results):

    st.subheader("📚 本次回答引用资料")

    sources = []

    for item in results:

        source = item.get("source", "")

        if source and source not in sources:

            sources.append(source)

    if not sources:

        st.info("无引用资料。")

        return

    for source in sources:

        st.markdown(f"- {source}")
