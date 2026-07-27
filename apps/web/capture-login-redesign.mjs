import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });

// Test at 360px (smallest Android)
for (const [w, h, label] of [[360, 800, "360"], [412, 915, "412"], [390, 844, "390"]]) {
  const ctx = await browser.newContext({
    viewport: { width: w, height: h },
    userAgent: "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36",
    deviceScaleFactor: 2,
  });
  const page = await ctx.newPage();

  await page.goto("https://app.combissportverein.org/", { waitUntil: "networkidle" });
  await page.waitForTimeout(500);

  // Screenshot
  await page.screenshot({ path: `test-results/login-redesign-${label}.png` });

  // DOM checks
  const checks = await page.evaluate(() => {
    const mobile = document.querySelector(".login-mobile");
    const desktop = document.querySelector(".login-desktop");
    const header = document.querySelector(".login-mobile__header");
    const footer = document.querySelector(".login-mobile__footer");
    const lang = document.querySelector(".login-mobile__header select");
    const form = document.querySelector(".login-mobile__form");
    const body = document.body;

    return {
      mobileDisplay: mobile ? getComputedStyle(mobile).display : "NOT FOUND",
      desktopDisplay: desktop ? getComputedStyle(desktop).display : "NOT FOUND",
      headerVisible: header ? getComputedStyle(header).display : "NOT FOUND",
      footerVisible: footer ? getComputedStyle(footer).display : "NOT FOUND",
      langVisible: lang ? "YES" : "NO",
      formVisible: form ? getComputedStyle(form).display : "NOT FOUND",
      bodyScrollH: body.scrollHeight,
      bodyClientH: body.clientHeight,
      viewportH: window.innerHeight,
      contentFits: body.scrollHeight <= body.clientHeight + 2,
    };
  });

  console.log(`\n=== ${label}px (Android) ===`);
  console.log("Mobile layout:", checks.mobileDisplay);
  console.log("Desktop layout:", checks.desktopDisplay);
  console.log("Header:", checks.headerVisible);
  console.log("Footer:", checks.footerVisible);
  console.log("Language selector:", checks.langVisible);
  console.log("Form:", checks.formVisible);
  console.log(`Body: scrollH=${checks.bodyScrollH} clientH=${checks.bodyClientH} fits=${checks.contentFits}`);

  await ctx.close();
}

// Desktop check
const ctx2 = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page2 = await ctx2.newPage();
await page2.goto("https://app.combissportverein.org/", { waitUntil: "networkidle" });
await page2.waitForTimeout(500);
await page2.screenshot({ path: "test-results/login-redesign-desktop.png" });

const desktopChecks = await page2.evaluate(() => {
  const mobile = document.querySelector(".login-mobile");
  const desktop = document.querySelector(".login-desktop");
  return {
    mobileDisplay: mobile ? getComputedStyle(mobile).display : "NOT FOUND",
    desktopDisplay: desktop ? getComputedStyle(desktop).display : "NOT FOUND",
  };
});
console.log("\n=== Desktop 1280px ===");
console.log("Mobile:", desktopChecks.mobileDisplay, "| Desktop:", desktopChecks.desktopDisplay);

await browser.close();
console.log("\nDone.");
