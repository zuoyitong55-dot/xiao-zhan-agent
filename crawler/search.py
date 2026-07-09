from pathlib import Path
from urllib.parse import urlparse
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

KEYWORDS_FILE = Path("crawler/keywords.txt")
URLS_FILE = Path("crawler/urls.txt")

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

SEARCH_LIMIT_PER_KEYWORD = 8

BLOCK_DOMAINS = [
    "baidu.com",
    "tieba.baidu.com",
    "zhidao.baidu.com",
    "weibo.com",
    "douyin.com",
    "bilibili.com",
]


def is_valid_url(url: str) -> bool:
    if not url.startswith("http"):
        return False

    domain = urlparse(url).netloc.lower()

    for blocked in BLOCK_DOMAINS:
        if blocked in domain:
            return False

    return True


def read_keywords():
    if not KEYWORDS_FILE.exists():
        print("没有找到 crawler/keywords.txt")
        return []

    return [
        line.strip()
        for line in KEYWORDS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def read_existing_urls():
    if not URLS_FILE.exists():
        return []

    return [
        line.strip()
        for line in URLS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def search_serper(keyword: str):
    if not SERPER_API_KEY:
        raise RuntimeError("没有找到 SERPER_API_KEY，请检查 .env 文件。")

    response = requests.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "q": keyword,
            "num": SEARCH_LIMIT_PER_KEYWORD,
            "hl": "zh-cn",
            "gl": "cn",
        },
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    urls = []

    for item in data.get("organic", []):
        url = item.get("link", "").strip()

        if is_valid_url(url) and url not in urls:
            urls.append(url)

    return urls


def main():
    keywords = read_keywords()

    if not keywords:
        print("keywords.txt 为空。")
        return

    existing_urls = read_existing_urls()
    url_set = set(existing_urls)
    new_urls = []

    for keyword in keywords:
        print(f"\n搜索关键词：{keyword}")

        try:
            urls = search_serper(keyword)

            if not urls:
                print("  未找到结果。")

            for url in urls:
                if url not in url_set:
                    url_set.add(url)
                    new_urls.append(url)
                    print(f"  + {url}")

            time.sleep(1)

        except Exception as e:
            print(f"  搜索失败：{e}")

    final_urls = existing_urls + new_urls

    URLS_FILE.write_text(
        "\n".join(final_urls) + "\n",
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print(f"新增链接：{len(new_urls)}")
    print(f"总链接数：{len(final_urls)}")
    print("已写入 crawler/urls.txt")
    print("=" * 60)


if __name__ == "__main__":
    main()

