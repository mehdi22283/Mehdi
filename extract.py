import asyncio
from playwright.async_api import async_playwright

PAGE = "https://www.showturk.com.tr/canli-yayin"
OUTPUT = "showturk.m3u8"


async def main():

    found = None

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            )
        )

        async def response_handler(response):
            nonlocal found

            url = response.url

            if ".m3u8" in url.lower() and found is None:
                found = url
                print("M3U8 TAPILDI:")
                print(url)

        page.on("response", response_handler)

        print("ShowTürk açılır...")

        await page.goto(
            PAGE,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Player-in yüklənməsi üçün gözlə
        await page.wait_for_timeout(30000)

        if found:

            # Köhnə faylı sil
            try:
                import os
                os.remove(OUTPUT)
            except FileNotFoundError:
                pass

            # Yeni faylı yarat
            with open(OUTPUT, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write("#EXT-X-VERSION:3\n")
                f.write(
                    "#EXT-X-STREAM-INF:"
                    "PROGRAM-ID=1,"
                    "BANDWIDTH=3000000,"
                    "RESOLUTION=1920x1080\n"
                )
                f.write(found + "\n")

            print("showturk.m3u8 yaradıldı.")

        else:
            print("M3U8 tapılmadı.")
            raise Exception("M3U8 URL tapılmadı.")

        await browser.close()


asyncio.run(main())
