import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 360, height: 800 },
  userAgent: "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36",
  deviceScaleFactor: 2,
});
const page = await context.newPage();

console.log(">>> Login page 360px");
await page.goto("https://app.combissportverein.org/", { waitUntil: "networkidle" });
await page.screenshot({ path: "test-results/mobile-360-login.png", fullPage: false });

console.log(">>> Login");
await page.fill('input[type="email"]', "admin@demo.org");
await page.fill('input[type="password"]', "Admin123!");
await page.click('button[type="submit"]');
await page.waitForURL("**/dashboard", { timeout: 15000 });
await page.waitForTimeout(1000);

console.log(">>> Dashboard 360px");
await page.screenshot({ path: "test-results/mobile-360-dashboard.png", fullPage: false });

await page.setViewportSize({ width: 412, height: 915 });
await page.waitForTimeout(500);
console.log(">>> Dashboard 412px");
await page.screenshot({ path: "test-results/mobile-412-dashboard.png", fullPage: false });

console.log(">>> Members 412px");
await page.goto("https://app.combissportverein.org/admin/members", { waitUntil: "networkidle" });
await page.waitForTimeout(500);
await page.screenshot({ path: "test-results/mobile-412-members.png", fullPage: false });

console.log(">>> Events 412px");
await page.goto("https://app.combissportverein.org/events", { waitUntil: "networkidle" });
await page.waitForTimeout(500);
await page.screenshot({ path: "test-results/mobile-412-events.png", fullPage: false });

await browser.close();
console.log("Done.");
