from pathlib import Path
import re
import time
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

URLS_FILE = Path("crawler/urls.txt")
OUTPUT_DIR = Path("knowledge")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; XiaoZhanPublicAgent/1.0)"
}

def safe_filename(text: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text[:80] or "untitled"

def extract_page(url: str):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "未命名网页"
    body = soup.body if soup.body else soup

    markdown = md(str(body), heading_style="ATX")
    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    markdown = "\n".join(lines)

    return title, markdown

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    urls = [
        line.strip()
        for line in URLS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not urls:
        print("crawler/urls.txt 里没有可爬取的链接。")
        return

    for index, url in enumerate(urls, start=1):
        try:
            title, content = extract_page(url)
            filename = f"{index:03d}_{safe_filename(title)}.md"
            output_path = OUTPUT_DIR / filename

            output_path.write_text(
                f"# {title}\n\n"
                f"来源：{url}\n\n"
                f"类型：公开网页资料\n\n"
                f"{content}\n",
                encoding="utf-8",
            )

            print(f"成功：{output_path}")
            time.sleep(2)

        except Exception as e:
            print(f"失败：{url}")
            print(e)

if __name__ == "__main__":
    main()
