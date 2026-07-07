from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = Path("knowledge")
DB_DIR = "vector_db"
COLLECTION_NAME = "xiao_zhan_knowledge"

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

for path in KNOWLEDGE_DIR.glob("*.md"):
    text = path.read_text(encoding="utf-8")

    chunk_size = 800
    overlap = 150

    start = 0
    chunk_id = 0

    while start < len(text):
        chunk = text[start:start + chunk_size].strip()

        if chunk:
            docs.append(chunk)
            ids.append(f"{path.stem}_{chunk_id}")
            metadatas.append({"source": path.name})

        start += chunk_size - overlap
        chunk_id += 1

if not docs:
    print("knowledge 文件夹中没有可索引的 Markdown 文件。")
    raise SystemExit

embeddings = model.encode(docs).tolist()

collection.add(
    documents=docs,
    ids=ids,
    metadatas=metadatas,
    embeddings=embeddings,
)

print(f"索引完成：共 {len(docs)} 个文本块")
