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

        # 多取一些，再做二次排序
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=max(top_k * 4, 20),
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

            item = {
                "content": doc,
                "source": meta.get("source", ""),
                "category": meta.get("category", ""),
                "url": meta.get("url", ""),
                "chunk": meta.get("chunk", ""),
                "credibility_score": meta.get("credibility_score", 0),
                "credibility_level": meta.get("credibility_level", ""),
                "distance": float(distance),
            }

            item["keyword_score"] = self.keyword_score(
                question,
                item,
            )

            output.append(item)

        output.sort(
            key=lambda x: (
                -int(x.get("keyword_score", 0)),
                -int(x.get("credibility_score", 0)),
                x.get("distance", 999),
            )
        )

        return output[:top_k]

    @staticmethod
    def keyword_score(question: str, item: Dict) -> int:

        q = question.lower()

        text = (
            item.get("source", "")
            + " "
            + item.get("category", "")
            + " "
            + item.get("content", "")[:1200]
        ).lower()

        score = 0

        # 影视作品类问题
        if any(k in q for k in ["影视作品", "作品", "电视剧", "电影", "演过", "出演"]):

            for k in [
                "影视作品",
                "作品列表",
                "电视剧",
                "电影",
                "陈情令",
                "玉骨遥",
                "藏海传",
                "梦中的那片海",
                "骄阳伴我",
                "王牌部队",
                "射雕英雄传",
                "诛仙",
            ]:
                if k.lower() in text:
                    score += 5

            if item.get("category") in ["dramas", "movies"]:
                score += 8

            if "影视作品列表" in item.get("source", ""):
                score += 20

        # 采访类问题
        if any(k in q for k in ["采访", "专访", "访谈", "谈到", "表演"]):

            for k in ["采访", "专访", "访谈", "对话", "表演", "演员"]:
                if k.lower() in text:
                    score += 5

            if item.get("category") == "interviews":
                score += 8

        # 官方资料类问题
        if any(k in q for k in ["官方", "工作室", "央视", "人民网"]):

            for k in ["官方", "工作室", "央视", "人民网", "新华社", "人民日报"]:
                if k.lower() in text:
                    score += 5

            if item.get("category") == "official":
                score += 8

        return score

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

可信度：
{item["credibility_level"]}

关键词匹配分：
{item.get("keyword_score", 0)}

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


