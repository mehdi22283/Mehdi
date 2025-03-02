import requests
import re
import base64
import json

# GitHub məlumatları
GITHUB_TOKEN = "TOKEN"
GITHUB_REPO = "Mehdi22283/Mehdi"
FILE_PATH = "playlist.m3u8"

# M3U8 linkini əldə etmə
URL = "https://yodaplayer.yodacdn.net/ntvpop/index.php"
headers = {"User-Agent": "Mozilla/5.0"}

def get_m3u8_link():
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        match = re.search(r'https?://.*?\.m3u8', response.text)
        return match.group(0) if match else None
    return None

def update_github_file(m3u8_link):
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # M3U8 faylını oxu (əgər mövcuddursa)
    response = requests.get(api_url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    # Yeni məzmunu yarat
    new_content = base64.b64encode(m3u8_link.encode()).decode()

    data = {
        "message": "Auto update M3U8 link",
        "content": new_content,
        "branch": "main",
    }
    
    if sha:
        data["sha"] = sha  # Mövcud faylı yenilə
    
    update_response = requests.put(api_url, headers=headers, data=json.dumps(data))
    return update_response.status_code == 200

# Prosesi işə sal
m3u8_link = get_m3u8_link()
if m3u8_link:
    success = update_github_file(m3u8_link)
    print("M3U8 yeniləndi!" if success else "GitHub yeniləmə uğursuz oldu.")
else:
    print("M3U8 link tapılmadı.")
