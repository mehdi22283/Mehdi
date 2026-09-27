const { chromium } = require("playwright");
const fs = require("fs");

const PAGE_URL = "https://www.atvavrupa.tv/canli-yayin";

(async () => {
    const browser = await chromium.launch({
        headless: true
    });

    const page = await browser.newPage();

    let foundM3U8 = null;

    // Bütün network sorğularını izlə
    page.on("request", request => {
        const url = request.url();

        if (
            url.includes(".m3u8") ||
            url.includes("m3u8")
        ) {
            console.log("M3U8 tapıldı:", url);
            foundM3U8 = url;
        }
    });

    page.on("response", response => {
        const url = response.url();

        if (
            url.includes(".m3u8") ||
            url.includes("m3u8")
        ) {
            console.log("M3U8 response:", url);
            foundM3U8 = url;
        }
    });

    try {
        await page.goto(PAGE_URL, {
            waitUntil: "domcontentloaded",
            timeout: 60000
        });

        // Playerin yüklənməsi üçün gözlə
        await page.waitForTimeout(30000);

        if (!foundM3U8) {
            console.log("M3U8 tapılmadı.");
            process.exitCode = 1;
            await browser.close();
            return;
        }

        // M3U8 faylını yaz
        fs.writeFileSync(
            "atv-avrupa.m3u8",
            `#EXTM3U\n#EXTINF:-1,ATV Avrupa\n${foundM3U8}\n`,
            "utf8"
        );

        console.log("Yazıldı:", foundM3U8);

    } catch (error) {
        console.error(error);
        process.exitCode = 1;
    }

    await browser.close();
})();
