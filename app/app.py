import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="肖战公开资料 Agent")
st.title("🎤 肖战公开资料 Agent")

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
)

def load_docs():
    docs = []
    for path in Path("knowledge").glob("*.md"):
        docs.append({
            "name": path.name,
            "text": path.read_text(encoding="utf-8")
        })
    return docs

def search_docs(question, docs):
    q = question.lower()
    hits = []
    for doc in docs:
        text = doc["text"]
        score = 0
        for word in q.replace("？", "").replace("?", "").split():
            if word.lower() in text.lower():
                score += 1
        if "example domain" in q and "example domain" in text.lower():
            score += 10
        if score > 0:
            hits.append((score, doc))
    hits.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in hits[:3]]

docs = load_docs()
question = st.text_input("请输入问题：")

if st.button("发送") and question:
    related_docs = search_docs(question, docs)

    if not related_docs:
        st.write("现有公开资料库中未找到明确依据。")
        st.stop()

    context = "\n\n".join(
        f"文件名：{doc['name']}\n{doc['text'][:4000]}"
        for doc in related_docs
    )

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "你是中文资料问答助手。只能根据提供的资料回答，用中文简洁回答。",
            },
            {
                "role": "user",
                "content": f"资料：\n{context}\n\n问题：{question}",
            },
        ],
    )

    st.write(response.choices[0].message.content)




