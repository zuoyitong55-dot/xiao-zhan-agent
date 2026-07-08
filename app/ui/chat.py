"""
聊天界面
"""

import streamlit as st


def init_chat():

    if "messages" not in st.session_state:
        st.session_state.messages = []


def show_history():

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_question():

    return st.chat_input(
        "请输入问题，例如：肖战有哪些影视作品？"
    )


def add_user_message(question):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)


def add_assistant_message(answer):

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)
