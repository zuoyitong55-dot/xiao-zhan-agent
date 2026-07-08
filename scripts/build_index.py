from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = Path("knowledge")
DB_DIR = "vector_db"
COLLECTION_NAME = "xiao_zhan_knowledge"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

print("正在加载 Embedding 模型...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.PersistentClient(path=DB_DIR)

try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

collection = client.create_collection(name=COLLECTION_NAME)

docs = []
ids = []
metadatas = []

markdown_count = 0

for path in KNOWLEDGE_DIR.rglob("*.md"):

    markdown_count += 1

    text = path.read_text(encoding="utf-8")

    category = path.parent.name

    url = ""

    for line in text.splitlines():

        if line.startswith("来源："):
            url = line.replace("来源：", "").strip()
            break

    safe_id = (
        str(path.relative_to(KNOWLEDGE_DIR))
        .replace("/", "_")
        .replace("\\", "_")
    )

    start = 0
    chunk_id = 0

    while start < len(text):

        chunk = text[start:start + CHUNK_SIZE].strip()

        if chunk:

            docs.append(chunk)

            ids.append(f"{safe_id}_{chunk_id}")

            metadatas.append(
                {
                    "source": str(path.relative_to(KNOWLEDGE_DIR)),
                    "category": category,
                    "url": url,
                    "chunk": chunk_id,
                }
            )

        start += CHUNK_SIZE - CHUNK_OVERLAP
        chunk_id += 1

if not docs:

    print("knowledge 文件夹中没有 Markdown 文件。")
    raise SystemExit

print("正在计算 Embedding...")

embeddings = model.encode(
    docs,
    show_progress_bar=True,
).tolist()

print("正在写入 ChromaDB...")

collection.add(
    documents=docs,
    ids=ids,
    metadatas=metadatas,
    embeddings=embeddings,
)

print()
print("=" * 60)
print("✅ 向量数据库构建完成")
print(f"Markdown 文件数 : {markdown_count}")
print(f"文本块数量      : {len(docs)}")
print(f"Collection      : {COLLECTION_NAME}")
print(f"数据库目录      : {DB_DIR}")
print("=" * 60)

