"""
网页正文提取
"""

import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/137 Safari/537.36"
    )
}


def safe_filename(text: str):

    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text)

    return text[:100]


def download(url: str):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
    )

    response.raise_for_status()

    response.encoding = response.apparent_encoding

    return response.text


def clean_html(html: str):

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    for tag in soup([
        "script",
        "style",
        "header",
        "footer",
        "nav",
        "aside",
        "iframe",
        "form",
    ]):
        tag.decompose()

    return soup


def html_to_markdown(soup):

    body = soup.body if soup.body else soup

    markdown = md(
        str(body),
        heading_style="ATX",
    )

    lines = []

    for line in markdown.splitlines():

        line = line.strip()

        if not line:
            continue

        lines.append(line)

    return "\n".join(lines)


def extract(url: str):

    html = download(url)

    soup = clean_html(html)

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else "未命名网页"
    )

    markdown = html_to_markdown(soup)

    return title, markdown
