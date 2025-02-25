import requests
from bs4 import BeautifulSoup
from github import Github
import os

# GitHub Personal Access Token (GitHub API üçün lazım olacaq)
GITHUB_TOKEN = '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'  # GitHub tokeninizi burada daxil edin
g = Github(GITHUB_TOKEN)

# Repositori adınız
REPO_NAME = 'Mehdi'  # Zaten mövcud olan repositori adı
repo = g.get_user().get_repo(REPO_NAME)

# URL siyahısı
urls = [
    "https://yoda.az/tv/ntv",
    "https://yoda.az/tv/kanal35",
    "https://yoda.az/tv/qafkaz",
    "https://yoda.az/tv/eltv",
    "https://yoda.az/tv/tmb",
    "https://yoda.az/tv/showplus",
    "https://yoda.az/tv/bakutv"
]

# GitHub repositoriyasına M3U8 faylını əlavə etmək
def upload_m3u8_to_github(url):
    # URL'den ad alınır (məsələn, "ntv")
    file_name = url.split("/")[-1] + ".m3u8"
    
    # M3U8 faylını çəkmək
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # M3U8 linkini tapmaq
    m3u8_link = None
    for script in soup.find_all('script'):
        if 'm3u8' in script.text:
            m3u8_link = script.text.split('m3u8:')[1].split('"')[1]
            break
    
    if m3u8_link:
        # M3U8 faylını yaradın
        m3u8_content = f'#EXTM3U\n#EXTINF:-1,{file_name}\n{m3u8_link}\n'
        
        # GitHub-a fayl yükləyin
        try:
            # Fayl artıq varsa, onu yeniləyin
            contents = repo.get_contents(file_name)
            repo.update_file(contents.path, "Update M3U8 file", m3u8_content, contents.sha)
            print(f"{file_name} faylı yeniləndi.")
        except:
            # Fayl mövcud deyilsə, yeni fayl yaradın
            repo.create_file(file_name, "Add M3U8 file", m3u8_content)
            print(f"{file_name} faylı GitHub-a əlavə edildi.")
    else:
        print(f"M3U8 linki tapılmadı: {url}")

# Hər bir URL üçün M3U8 faylını çəkin və GitHub repositoriyasına yükləyin
for url in urls:
    upload_m3u8_to_github(url)
