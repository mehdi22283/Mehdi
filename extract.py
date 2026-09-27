import re
import requests
from urllib.parse import urljoin

URL = "https://www.showturk.com.tr/canli-yayin"
OUTPUT = "showturk.m3u8"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}

session = requests.Session()

html = session.get(
    URL,
    headers=headers,
    timeout=30
).text

found = set()

# HTML daxilində olan m3u8 linkləri
patterns = [
    r'https?://[^"\'>\s]+\.m3u8(?:\?[^"\'>\s]*)?',
    r'//[^"\'>\s]+\.m3u8(?:\?[^"\'>\s]*)?',
]

for pattern in patterns:
    for match in re.findall(pattern, html, re.I):
        if match.startswith("//"):
            match = "https:" + match

        found.add(match)

# Escape olunmuş URL-lər
for match in re.findall(
    r'https?:\\?/\\?/[^"\'<>\s]+?\.m3u8(?:\\?[^"\'<>\s]*)?',
    html,
    re.I
):
    match = match.replace("\\/", "/")
    found.add(match)

if not found:
    print("M3U8 tapılmadı")
    print("Səhifədə JavaScript ilə yaradılan player ola bilər.")
else:
    print("Tapılan M3U8 linkləri:")

    for url in sorted(found):
        print(url)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for url in sorted(found):
            f.write("#EXTINF:-1,ShowTürk\n")
            f.write(url + "\n")

    print(f"\n{len(found)} link {OUTPUT} faylına yazıldı.")
