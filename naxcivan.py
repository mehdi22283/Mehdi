import requests
import re
from github import Github
import os

# GitHub Token (Secret-dən oxuyuruq)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "Mehdi22283/Mehdi"
FILE_PATH = "naxcivan.m3u8"  # Faylın adı "naxcivan.m3u8"
COMMIT_MESSAGE = "M3U8 linkini yenilədi"

# M3U8 linkini əldə edən funksiya
def get_m3u8_link():
    url = "https://yoda.az/tv/ntv/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        match = re.search(r'https://.*?\.m3u8', response.text)
        if match:
            return match.group(0)
    return None

# GitHub-da faylı yeniləyən funksiya
def update_github_file(m3u8_link):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    try:
        file = repo.get_contents(FILE_PATH)
        repo.update_file(FILE_PATH, COMMIT_MESSAGE, m3u8_link, file.sha)
    except:
        repo.create_file(FILE_PATH, COMMIT_MESSAGE, m3u8_link)

# Əsas proses
m3u8_link = get_m3u8_link()
if m3u8_link:
    update_github_file(m3u8_link)
    print(f"Yeniləndi: {m3u8_link}")
else:
    print("M3U8 linki tapılmadı!")
