import os
import time
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

URLS_FILE = "crawler/urls.txt"
OUTPUT_DIR = "knowledge"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; XiaoZhanPublicAgent/1.0)"
}

def clean_filename(name):
    keep = []
    for ch in name:
        if ch.isalnum() or ch in "-_":
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep)[:80]

def extract_page(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "untitled"
    body = soup.body if soup.body else soup

    content = md(str(body), heading_style="ATX")
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    content = "\n".join(lines)

    return title, content

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    for index, url in enumerate(urls, start=1):
        try:
            title, content = extract_page(url)
            filename = f"{index:03d}_{clean_filename(title)}.md"
            path = os.path.join(OUTPUT_DIR, filename)

            with open(path, "w", encoding="utf-8") as out:
                out.write(f"# {title}\n\n")
                out.write(f"来源：{url}\n\n")
                out.write("类型：公开网页资料\n\n")
                out.write(content)

            print(f"成功：{title}")
            time.sleep(2)

        except Exception as e:
            print(f"失败：{url}")
            print(e)

if __name__ == "__main__":
    main()
