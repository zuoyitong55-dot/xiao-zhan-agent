from pathlib import Path
import re
import time

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

URLS_FILE = Path("crawler/urls.txt")
OUTPUT_BASE_DIR = Path("knowledge")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/137 Safari/537.36"
    )
}

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


def safe_filename(text: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text[:80] or "untitled"


def classify_document(title: str, url: str, content: str) -> str:

    text = f"{title} {url} {content[:1000]}"

    if any(k in text for k in ["采访", "专访", "访谈", "对话"]):
        return "interviews"

    if any(
        k in text
        for k in [
            "电视剧",
            "剧集",
            "陈情令",
            "玉骨遥",
            "藏海传",
            "梦中的那片海",
            "骄阳伴我",
            "王牌部队",
        ]
    ):
        return "dramas"

    if any(
        k in text
        for k in [
            "电影",
            "射雕英雄传",
            "侠之大者",
            "诛仙",
        ]
    ):
        return "movies"

    if any(k in text for k in ["音乐", "歌曲", "专辑"]):
        return "music"

    if any(k in text for k in ["获奖", "奖项", "荣誉"]):
        return "awards"

    if any(k in text for k in ["综艺", "节目"]):
        return "variety"

    if any(
        k in text
        for k in [
            "工作室",
            "官方",
            "央视",
            "CCTV",
            "人民网",
            "新华社",
            "人民日报",
        ]
    ):
        return "official"

    return "general"


def extract_page(url: str):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
    )

    response.raise_for_status()

    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(
        response.text,
        "lxml",
    )

    for tag in soup(
        [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "iframe",
            "form",
        ]
    ):
        tag.decompose()

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else "未命名网页"
    )

    body = soup.body if soup.body else soup

    markdown = md(
        str(body),
        heading_style="ATX",
    )

    lines = [
        line.strip()
        for line in markdown.splitlines()
        if line.strip()
    ]

    markdown = "\n".join(lines)

    return title, markdown


def main():

    if not URLS_FILE.exists():

        print("没有找到 crawler/urls.txt")

        return

    OUTPUT_BASE_DIR.mkdir(exist_ok=True)

    for category in CATEGORIES:
        (OUTPUT_BASE_DIR / category).mkdir(
            parents=True,
            exist_ok=True,
        )

    urls = [
        line.strip()
        for line in URLS_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
        and not line.startswith("#")
    ]

    if not urls:

        print("urls.txt 为空。")

        return

    success = 0
    failed = 0

    print(f"开始爬取，共 {len(urls)} 个网页。\n")

    for index, url in enumerate(urls, start=1):

        try:

            title, content = extract_page(url)

            category = classify_document(
                title,
                url,
                content,
            )

            filename = (
                f"{index:03d}_"
                f"{safe_filename(title)}.md"
            )

            output = (
                OUTPUT_BASE_DIR
                / category
                / filename
            )

            if output.exists():

                print(f"跳过（已存在）：{filename}")

                continue

            output.write_text(
                f"# {title}\n\n"
                f"来源：{url}\n\n"
                f"分类：{category}\n\n"
                f"类型：公开网页资料\n\n"
                f"{content}\n",
                encoding="utf-8",
            )

            success += 1

            print(f"✓ {filename}")

            time.sleep(1)

        except Exception as e:

            failed += 1

            print(f"✗ {url}")

            print(e)

    print("\n" + "=" * 60)
    print(f"成功：{success}")
    print(f"失败：{failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()


