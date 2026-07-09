from pathlib import Path
import hashlib
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


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", text)
    return text.lower()


def content_hash(text: str) -> str:
    normalized = normalize_text(text[:8000])
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_meta_from_file(path: Path):
    url = ""
    h = ""

    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("来源："):
                url = line.replace("来源：", "").strip()
            elif line.startswith("内容指纹："):
                h = line.replace("内容指纹：", "").strip()
    except Exception:
        pass

    return url, h


def load_existing_records():
    urls = set()
    hashes = set()

    for path in OUTPUT_BASE_DIR.rglob("*.md"):
        url, h = extract_meta_from_file(path)

        if url:
            urls.add(url)

        if h:
            hashes.add(h)
        else:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                hashes.add(content_hash(text))
            except Exception:
                pass

    return urls, hashes


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

    if any(k in text for k in ["电影", "射雕英雄传", "侠之大者", "诛仙"]):
        return "movies"

    if any(k in text for k in ["音乐", "歌曲", "专辑"]):
        return "music"

    if any(k in text for k in ["获奖", "奖项", "荣誉"]):
        return "awards"

    if any(k in text for k in ["综艺", "节目"]):
        return "variety"

    if any(
        k in text
        for k in ["工作室", "官方", "央视", "CCTV", "人民网", "新华社", "人民日报"]
    ):
        return "official"

    return "general"


def extract_page(url: str):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "lxml")

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

    title = soup.title.get_text(strip=True) if soup.title else "未命名网页"
    body = soup.body if soup.body else soup

    markdown = md(str(body), heading_style="ATX")
    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    markdown = "\n".join(lines)

    return title, markdown


def main():
    if not URLS_FILE.exists():
        print("没有找到 crawler/urls.txt")
        return

    OUTPUT_BASE_DIR.mkdir(exist_ok=True)

    for category in CATEGORIES:
        (OUTPUT_BASE_DIR / category).mkdir(parents=True, exist_ok=True)

    urls = [
        line.strip()
        for line in URLS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    if not urls:
        print("urls.txt 为空。")
        return

    existing_urls, existing_hashes = load_existing_records()

    success = 0
    skipped = 0
    failed = 0

    print(f"开始爬取，共 {len(urls)} 个网页。")
    print(f"已有来源链接：{len(existing_urls)}")
    print(f"已有内容指纹：{len(existing_hashes)}\n")

    for index, url in enumerate(urls, start=1):
        if url in existing_urls:
            skipped += 1
            print(f"跳过 URL 重复：{url}")
            continue

        try:
            title, content = extract_page(url)
            h = content_hash(content)

            if h in existing_hashes:
                skipped += 1
                print(f"跳过 内容重复：{title}")
                continue

            category = classify_document(title, url, content)

            filename = f"{index:03d}_{safe_filename(title)}.md"
            output = OUTPUT_BASE_DIR / category / filename

            if output.exists():
                skipped += 1
                print(f"跳过 文件已存在：{filename}")
                continue

            output.write_text(
                f"# {title}\n\n"
                f"来源：{url}\n\n"
                f"分类：{category}\n\n"
                f"类型：公开网页资料\n\n"
                f"内容指纹：{h}\n\n"
                f"{content}\n",
                encoding="utf-8",
            )

            existing_urls.add(url)
            existing_hashes.add(h)

            success += 1
            print(f"✓ {filename}")

            time.sleep(1)

        except Exception as e:
            failed += 1
            print(f"✗ {url}")
            print(e)

    print("\n" + "=" * 60)
    print(f"新增成功：{success}")
    print(f"跳过重复：{skipped}")
    print(f"失败数量：{failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()



