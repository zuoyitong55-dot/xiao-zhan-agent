from pathlib import Path
from urllib.parse import urlparse

import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = Path("knowledge")
DB_DIR = "vector_db"
COLLECTION_NAME = "xiao_zhan_knowledge"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def get_credibility(url: str, source: str, category: str):
    text = f"{url} {source} {category}".lower()

    high_sources = [
        "xinhuanet.com",
        "people.com.cn",
        "cctv.com",
        "cntv.cn",
        "china.com.cn",
        "gov.cn",
        "央视",
        "新华社",
        "人民网",
        "人民日报",
    ]

    official_sources = [
        "studio",
        "official",
        "工作室",
        "官方",
    ]

    platform_sources = [
        "iqiyi.com",
        "qq.com",
        "youku.com",
        "mgtv.com",
        "tencent",
        "爱奇艺",
        "腾讯",
        "优酷",
    ]

    encyclopedia_sources = [
        "wikipedia.org",
        "baike",
        "百科",
    ]

    if any(k in text for k in high_sources):
        return 5, "★★★★★ 权威媒体/官方机构"

    if any(k in text for k in official_sources):
        return 5, "★★★★★ 官方来源"

    if any(k in text for k in platform_sources):
        return 4, "★★★★☆ 平台/剧方资料"

    if any(k in text for k in encyclopedia_sources):
        return 3, "★★★☆☆ 百科类资料"

    if category in ["interviews", "dramas", "movies", "official"]:
        return 3, "★★★☆☆ 一般公开资料"

    return 2, "★★☆☆☆ 普通网页资料"


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
    source = str(path.relative_to(KNOWLEDGE_DIR))
    url = ""

    for line in text.splitlines():
        if line.startswith("来源："):
            url = line.replace("来源：", "").strip()
            break

    credibility_score, credibility_level = get_credibility(
        url=url,
        source=source,
        category=category,
    )

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
                    "source": source,
                    "category": category,
                    "url": url,
                    "chunk": chunk_id,
                    "credibility_score": credibility_score,
                    "credibility_level": credibility_level,
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
print("已写入字段      : source / category / url / chunk / credibility_score / credibility_level")
print("=" * 60)


