const { chromium } = require("playwright");
const fs = require("fs");

const PAGE_URL = "https://www.atvavrupa.tv/canli-yayin";
const OUTPUT = "atvavrupa.m3u8";

function absoluteUrl(url, base) {
    try {
        return new URL(url, base).href;
    } catch {
        return url;
    }
}

function parseAttributes(line) {
    const result = {};

    const regex = /([A-Z0-9-]+)=("[^"]*"|[^,]*)/g;
    let match;

    while ((match = regex.exec(line)) !== null) {
        result[match[1]] = match[2].replace(/^"|"$/g, "");
    }

    return result;
}

async function main() {
    const browser = await chromium.launch({
        headless: true
    });

    const context = await browser.newContext({
        userAgent:
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/140.0.0.0 Safari/537.36"
    });

    const page = await context.newPage();

    const m3u8Responses = [];

    page.on("response", async response => {
        const url = response.url();

        if (!/\.m3u8(\?|$)/i.test(url)) {
            return;
        }

        console.log("M3U8 TAPILDI:", url);

        try {
            const body = await response.text();

            m3u8Responses.push({
                url,
                body
            });
        } catch (e) {
            console.log("Playlist oxuna bilmədi:", url);
        }
    });

    console.log("ATV Avrupa açılır...");

    await page.goto(PAGE_URL, {
        waitUntil: "domcontentloaded",
        timeout: 60000
    });

    // Player-in iframe və JS-lərinin yüklənməsi üçün gözlə
    await page.waitForTimeout(15000);

    // Bəzi playerlər yayını yalnız video elementindən sonra başladır
    try {
        await page.locator("video").first().click({
            position: { x: 10, y: 10 },
            timeout: 5000
        });
    } catch {}

    await page.waitForTimeout(10000);

    console.log(
        `Tapılan M3U8 sayı: ${m3u8Responses.length}`
    );

    if (!m3u8Responses.length) {
        await browser.close();
        throw new Error("Heç bir M3U8 linki tapılmadı.");
    }

    // BANDWIDTH olan master playlist-i üstün tuturuq
    let master = m3u8Responses.find(x =>
        /#EXT-X-STREAM-INF/i.test(x.body)
    );

    // Master tapılmasa son tapılan M3U8
    if (!master) {
        master = m3u8Responses[m3u8Responses.length - 1];
    }

    console.log("İstifadə edilən playlist:");
    console.log(master.url);

    const lines = master.body
        .split(/\r?\n/)
        .map(x => x.trim())
        .filter(Boolean);

    const output = [
        "#EXTM3U",
        "#EXT-X-VERSION:3"
    ];

    for (let i = 0; i < lines.length; i++) {

        const line = lines[i];

        if (!line.startsWith("#EXT-X-STREAM-INF:")) {
            continue;
        }

        const attributes = parseAttributes(
            line.replace("#EXT-X-STREAM-INF:", "")
        );

        // Növbəti sətir variant URL-dir
        let variant = lines[i + 1];

        if (!variant || variant.startsWith("#")) {
            continue;
        }

        variant = absoluteUrl(variant, master.url);

        let bandwidth =
            attributes.BANDWIDTH ||
            "0";

        let resolution =
            attributes.RESOLUTION ||
            "";

        let width = "";
        let height = "";

        if (resolution.includes("x")) {
            [width, height] = resolution.split("x");
        }

        let name = attributes.NAME;

        if (!name) {
            if (height) {
                name = `${height}p`;
            } else {
                name = "stream";
            }
        }

        output.push(
            `#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=${bandwidth},NAME=${name},RESOLUTION=${resolution}`
        );

        output.push(variant);
    }

    // Əgər master playlist parse olunmadısa
    if (output.length <= 2) {
        console.log("Master playlist variantları tapılmadı.");

        // Birbaşa M3U8-i yaz
        output.push(master.url);
    }

    output.push("");

    fs.writeFileSync(
        OUTPUT,
        output.join("\n"),
        "utf8"
    );

    console.log("\n===== YARADILAN FAYL =====\n");
    console.log(output.join("\n"));

    await browser.close();
}

main().catch(error => {
    console.error(error);
    process.exit(1);
});
