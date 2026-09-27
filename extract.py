import re
import requests

PAGE_URL = "https://www.showturk.com.tr/canli-yayin"
OUTPUT = "showturk.m3u8"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}

response = requests.get(
    PAGE_URL,
    headers=HEADERS,
    timeout=30
)

response.raise_for_status()
html = response.text

# M3U8 URL-lərini tap
urls = re.findall(
    r'https?://[^"\'<>\s]+\.m3u8(?:\?[^"\'<>\s]*)?',
    html,
    re.I
)

# Dublikatları sil
urls = list(dict.fromkeys(urls))

if not urls:
    raise RuntimeError("M3U8 link tapılmadı.")

# Keyfiyyətə görə qruplaşdır
qualities = {
    "1080": None,
    "720": None,
    "480": None
}

for url in urls:
    u = url.lower()

    if "1080" in u:
        qualities["1080"] = url

    elif "720" in u:
        qualities["720"] = url

    elif "480" in u:
        qualities["480"] = url


# Əgər keyfiyyət URL-də görünmürsə, tapılan ilk linki 1080 kimi istifadə et
if not any(qualities.values()):
    qualities["1080"] = urls[0]


# Faylı tamamilə sıfırdan yarat
with open(OUTPUT, "w", encoding="utf-8") as f:

    f.write("#EXTM3U\n")
    f.write("#EXT-X-VERSION:3\n")

    if qualities["1080"]:
        f.write(
            "#EXT-X-STREAM-INF:"
            "PROGRAM-ID=1,"
            "BANDWIDTH=3000000,"
            "RESOLUTION=1920x1080\n"
        )
        f.write(qualities["1080"] + "\n")

    if qualities["720"]:
        f.write(
            "#EXT-X-STREAM-INF:"
            "PROGRAM-ID=1,"
            "BANDWIDTH=1500000,"
            "RESOLUTION=1280x720\n"
        )
        f.write(qualities["720"] + "\n")

    if qualities["480"]:
        f.write(
            "#EXT-X-STREAM-INF:"
            "PROGRAM-ID=1,"
            "BANDWIDTH=900000,"
            "RESOLUTION=854x480\n"
        )
        f.write(qualities["480"] + "\n")

print("Yeni showturk.m3u8 yaradıldı.")
