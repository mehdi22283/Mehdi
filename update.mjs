import { chromium } from 'playwright';
import fs from 'fs';

const PAGE = 'https://www.atvavrupa.tv/canli-yayin';
const OUT = 'atv-avrupa.m3u8';
const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';

const browser = await chromium.launch();
const ctx = await browser.newContext({ userAgent: UA, locale: 'tr-TR' });
const page = await ctx.newPage();

// Player yüklənəndə şəbəkə sorğularından .m3u8 linkini tuturuq
const found = [];
page.on('request', (r) => {
  const u = r.url();
  if (/\.m3u8(\?|$)/.test(u) && !found.includes(u)) found.push(u);
});

await page.goto(PAGE, { waitUntil: 'domcontentloaded', timeout: 60000 });
for (let i = 0; i < 30 && !found.length; i++) await page.waitForTimeout(1000);
await browser.close();

if (!found.length) throw new Error('m3u8 linki tapılmadı');

const master = found[0];
const headers = { 'User-Agent': UA, Referer: PAGE, Origin: 'https://www.atvavrupa.tv' };
const text = await (await fetch(master, { headers })).text();

let out;
if (text.includes('#EXT-X-STREAM-INF')) {
  // Master playlist: nisbi linkləri tam linkə çevir, token yoxdursa əlavə et
  const base = new URL(master);
  out =
    text
      .split('\n')
      .map((l) => {
        l = l.trim();
        if (!l || l.startsWith('#')) return l;
        const u = new URL(l, base);
        if (!u.search) u.search = base.search;
        return u.href;
      })
      .join('\n') + '\n';
} else {
  out =
    '#EXTM3U\n#EXT-X-VERSION:3\n' +
    '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1500000,RESOLUTION=1920x1080\n' +
    master +
    '\n';
}

fs.writeFileSync(OUT, out);
console.log('Yeniləndi:\n' + out);
