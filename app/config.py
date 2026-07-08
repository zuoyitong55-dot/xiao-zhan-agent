"""
项目统一配置
"""

from pathlib import Path

# =========================
# 数据目录
# =========================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"

COLLECTION_NAME = "xiao_zhan_knowledge"


# =========================
# Embedding 模型
# =========================

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


# =========================
# GitHub Models
# =========================

DEFAULT_MODEL = "openai/gpt-4o-mini"

MODEL_OPTIONS = {
    "GPT-4o mini": "openai/gpt-4o-mini",
    "Phi-4": "microsoft/phi-4",
}


# =========================
# RAG 参数
# =========================

DEFAULT_TOP_K = 5

MAX_TOP_K = 10

CHUNK_SIZE = 800

CHUNK_OVERLAP = 150


# =========================
# Knowledge 分类
# =========================

CATEGORIES = [
    "interviews",
    "dramas",
    "movies",
    "music",
    "awards",
    "variety",
    "official",
    "general",
]
