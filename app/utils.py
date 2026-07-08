"""
工具函数
"""

from pathlib import Path
from datetime import datetime

from app.config import (
    KNOWLEDGE_DIR,
    VECTOR_DB_DIR,
)


def count_markdown_files():

    return len(list(KNOWLEDGE_DIR.rglob("*.md")))


def count_categories():

    result = {}

    for folder in KNOWLEDGE_DIR.iterdir():

        if folder.is_dir():

            result[folder.name] = len(
                list(folder.glob("*.md"))
            )

    return result


def vector_db_exists():

    return VECTOR_DB_DIR.exists()


def latest_update_time():

    latest = None

    for file in KNOWLEDGE_DIR.rglob("*.md"):

        t = file.stat().st_mtime

        if latest is None:

            latest = t

        else:

            latest = max(latest, t)

    if latest is None:

        return "暂无"

    return datetime.fromtimestamp(
        latest
    ).strftime("%Y-%m-%d %H:%M:%S")


def format_sources(results):

    sources = []

    seen = set()

    for item in results:

        source = item.get("source", "")

        if source in seen:

            continue

        seen.add(source)

        sources.append(source)

    return sources


def build_source_markdown(results):

    sources = format_sources(results)

    if len(sources) == 0:

        return "无"

    text = []

    for source in sources:

        text.append(f"- {source}")

    return "\n".join(text)
