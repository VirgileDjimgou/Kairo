import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({
  viewport: { width: 360, height: 800 },
  userAgent: "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36",
  deviceScaleFactor: 2,
});
const page = await ctx.newPage();

console.log(">>> 1. Login page 360px");
await page.goto("https://app.combissportverein.org/", { waitUntil: "networkidle" });
await page.screenshot({ path: "test-results/mobile-v2-360-login.png" });

console.log(">>> 2. Login");
await page.fill('input[type="email"]', "admin@demo.org");
await page.fill('input[type="password"]', "Admin123!");
await page.click('button[type="submit"]');
await page.waitForURL("**/dashboard", { timeout: 15000 });
await page.waitForTimeout(1000);

console.log(">>> 3. Dashboard 360px");
await page.screenshot({ path: "test-results/mobile-v2-360-dashboard.png" });

console.log(">>> 4. Dashboard 412px");
await page.setViewportSize({ width: 412, height: 915 });
await page.waitForTimeout(500);
await page.screenshot({ path: "test-results/mobile-v2-412-dashboard.png" });

console.log(">>> 5. Members 412px");
await page.goto("https://app.combissportverein.org/admin/members", { waitUntil: "networkidle" });
await page.waitForTimeout(500);
await page.screenshot({ path: "test-results/mobile-v2-412-members.png" });

console.log(">>> 6. Events 412px");
await page.goto("https://app.combissportverein.org/events", { waitUntil: "networkidle" });
await page.waitForTimeout(500);
await page.screenshot({ path: "test-results/mobile-v2-412-events.png" });

// DOM checks
console.log(">>> 7. DOM: Sidebar visible?");
const sidebarVisible = await page.evaluate(() => {
  const sidebar = document.querySelector(".desktop-sidebar");
  if (!sidebar) return "NOT FOUND";
  const style = window.getComputedStyle(sidebar);
  return `display=${style.display} width=${style.width} height=${style.height}`;
});
console.log("   Sidebar:", sidebarVisible);

console.log(">>> 8. DOM: RoleTopNavigation visible?");
const topNavVisible = await page.evaluate(() => {
  const nav = document.querySelector(".role-top-navigation");
  if (!nav) return "NOT FOUND";
  const style = window.getComputedStyle(nav);
  return `display=${style.display}`;
});
console.log("   RoleTopNav:", topNavVisible);

console.log(">>> 9. DOM: Bottom nav visible?");
const bottomNavVisible = await page.evaluate(() => {
  const nav = document.querySelector(".bottom-nav");
  if (!nav) return "NOT FOUND";
  const style = window.getComputedStyle(nav);
  return `display=${style.display} width=${style.width}`;
});
console.log("   BottomNav:", bottomNavVisible);

console.log(">>> 10. DOM: AppTopBar mobile visible?");
const topBarVisible = await page.evaluate(() => {
  const mobile = document.querySelector(".app-top-bar__mobile");
  const desktop = document.querySelector(".app-top-bar__desktop");
  if (!mobile || !desktop) return "NOT FOUND";
  return `mobile=${window.getComputedStyle(mobile).display} desktop=${window.getComputedStyle(desktop).display}`;
});
console.log("   TopBar:", topBarVisible);

console.log(">>> 11. DOM: Body overflow check");
const bodyOverflow = await page.evaluate(() => {
  const body = document.body;
  const style = window.getComputedStyle(body);
  return `overflowX=${style.overflowX} scrollWidth=${body.scrollWidth} clientWidth=${body.clientWidth}`;
});
console.log("   Body:", bodyOverflow);

await browser.close();
console.log("Done.");
