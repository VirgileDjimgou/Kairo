import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 360, height: 800 },
  deviceScaleFactor: 2,
});
const page = await context.newPage();

// Login once
await page.goto("https://app.combissportverein.org/", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(800);
const email = page.locator('input[type="email"]').first();
if (await email.isVisible({ timeout: 5000 })) {
  await email.fill("admin@demo.org");
  await page.locator('input[type="password"]').first().fill("Admin123!");
  await page.locator('button[type="submit"]').first().click();
  await page.waitForURL("**/dashboard", { timeout: 20000 });
  await page.waitForTimeout(800);
}
console.log("Logged in. Current URL:", page.url());

const viewports = [
  [320, 568, "320px Android"],
  [360, 800, "360px Android"],
  [412, 915, "412px Pixel7"],
  [430, 932, "430px big Android"],
  [768, 1024, "768px iPad"],
  [1280, 720, "1280px desktop"],
  [1440, 900, "1440px desktop"],
];
const routes = [
  ["/dashboard", "dashboard"],
  ["/admin/members", "admin/members"],
  ["/admin/contributions", "admin/contrib"],
  ["/admin/events", "admin/events"],
  ["/events", "events"],
];

let total = 0, passed = 0, failed = 0;

for (const [w, h, label] of viewports) {
  await page.setViewportSize({ width: w, height: h });
  await page.waitForTimeout(300);

  for (const [route, name] of routes) {
    total++;
    await page.goto(`https://app.combissportverein.org${route}`, { waitUntil: "domcontentloaded", timeout: 15000 });
    await page.waitForTimeout(500);

    const result = await page.evaluate(() => {
      const docEl = document.documentElement;
      return {
        scrollWidth: Math.max(docEl.scrollWidth, document.body.scrollWidth),
        clientWidth: docEl.clientWidth,
      };
    });

    const overflowPx = result.scrollWidth - result.clientWidth;
    const ok = overflowPx <= 1;
    if (ok) { passed++; } else { failed++; }
    console.log(`${ok ? "OK " : "XX "}${label.padEnd(18)} ${name.padEnd(18)} scroll=${result.scrollWidth} client=${result.clientWidth} overflow=${overflowPx}`);
  }
}

await browser.close();
console.log(`\n=== ${passed}/${total} passed, ${failed} failed ===`);
