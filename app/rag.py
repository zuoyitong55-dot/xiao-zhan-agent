"""
RAG 检索模块
负责：
1. ChromaDB 连接
2. Embedding
3. TopK 检索
4. Context 拼接
"""

from pathlib import Path
from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import (
    VECTOR_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    DEFAULT_TOP_K,
)


class RAGRetriever:

    def __init__(self):

        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR)
        )

        self.collection = self.client.get_collection(
            COLLECTION_NAME
        )

    def search(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> List[Dict]:

        embedding = self.embedder.encode(
            [question]
        ).tolist()[0]

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        output = []

        for doc, meta, distance in zip(
            docs,
            metas,
            distances,
        ):

            output.append(
                {
                    "content": doc,
                    "source": meta.get("source", ""),
                    "category": meta.get("category", ""),
                    "url": meta.get("url", ""),
                    "distance": float(distance),
                }
            )

        return output

    @staticmethod
    def build_context(results: List[Dict]):

        context = []

        for index, item in enumerate(results, start=1):

            context.append(
                f"""
====================
资料 {index}

来源：
{item["source"]}

分类：
{item["category"]}

链接：
{item["url"]}

正文：

{item["content"]}
"""
            )

        return "\n".join(context)


_retriever = None


def get_retriever():

    global _retriever

    if _retriever is None:
        _retriever = RAGRetriever()

    return _retriever
