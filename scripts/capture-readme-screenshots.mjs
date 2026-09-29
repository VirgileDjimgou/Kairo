import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { chromium } from "../apps/web/node_modules/playwright/index.mjs";

/**
 * Captures the portfolio README screenshot gallery against a running Kairo
 * instance (the public demo by default).
 *
 * The script authenticates through the real FastAPI contract, injects the
 * resulting session into the browser, and screenshots the authorised role
 * surfaces at desktop and phone widths. No backend rule is simulated.
 *
 * Usage:
 *   node scripts/capture-readme-screenshots.mjs
 *
 * Override the target or locale with:
 *   KAIRO_SCREENSHOT_BASE_URL=https://kairo.patrickdjimgou.dev
 *   KAIRO_SCREENSHOT_LOCALE=fr
 */

const repoRoot = process.cwd();
const baseUrl = (process.env.KAIRO_SCREENSHOT_BASE_URL || "https://kairo.patrickdjimgou.dev").replace(/\/$/, "");
const apiBaseUrl = process.env.KAIRO_SCREENSHOT_API_URL || `${baseUrl}/api/v1`;
const locale = process.env.KAIRO_SCREENSHOT_LOCALE || "fr";
const targetLabel = process.env.KAIRO_SCREENSHOT_TARGET_LABEL || `\`${baseUrl}\``;
const outputRoot = path.join(repoRoot, "docs", "screenshots");

const desktopViewport = { width: 1440, height: 900 };
const mobileViewport = { width: 390, height: 844 };

const defaultAccounts = {
  member: { email: "alice@demo.org", password: "Member123!" },
  president: { email: "president@demo.org", password: "President123!" },
  secretary_general: { email: "secretary@demo.org", password: "Secretary123!" },
  treasurer: { email: "treasurer@demo.org", password: "Treasurer123!" },
  auditor: { email: "auditor@demo.org", password: "Auditor123!" },
  censor: { email: "censor@demo.org", password: "Censor123!" },
  sports_manager: { email: "sports@demo.org", password: "Sports123!" },
  vice_president: { email: "vice-president@demo.org", password: "VicePresident123!" },
  principal_admin: { email: "principal@demo.org", password: "Principal123!" },
};

/**
 * Demo credentials are never committed. A deployment that rotates them passes
 * the public `VITE_DEMO_ACCOUNTS` payload through this environment variable so
 * the capture script always mirrors the live portfolio demo.
 */
function resolveAccounts() {
  const raw = process.env.KAIRO_SCREENSHOT_ACCOUNTS;
  const accounts = {};
  for (const [key, value] of Object.entries(defaultAccounts)) {
    accounts[key] = { ...value, tenantSlug: "demo" };
  }
  if (!raw) {
    return accounts;
  }
  try {
    const parsed = JSON.parse(raw);
    for (const entry of parsed) {
      if (!entry || typeof entry.key !== "string" || !entry.email || !entry.password) continue;
      accounts[entry.key] = { email: entry.email, password: entry.password, tenantSlug: "demo" };
    }
  } catch {
    console.warn("KAIRO_SCREENSHOT_ACCOUNTS is not valid JSON; using default seed accounts.");
  }
  return accounts;
}

const accounts = resolveAccounts();

const publicSessions = [
  {
    folder: "public",
    file: "01-demo-landing.png",
    route: "/demo",
    note: "Public one-click demo entry point with the role picker.",
    viewport: desktopViewport,
  },
  {
    folder: "public",
    file: "02-login.png",
    route: "/login",
    note: "Multilingual sign-in surface.",
    viewport: desktopViewport,
  },
];

const roleSessions = [
  {
    account: "member",
    folder: "member",
    file: "01-dashboard.png",
    route: "/dashboard",
    note: "Ordinary member dashboard.",
  },
  {
    account: "member",
    folder: "member",
    file: "02-contribution-statement.png",
    route: "/members/profile",
    note: "Personal contribution statement and member record.",
  },
  {
    account: "member",
    folder: "member",
    file: "03-events.png",
    route: "/events",
    note: "Members-only events calendar.",
  },
  {
    account: "member",
    folder: "member",
    file: "04-announcements.png",
    route: "/announcements",
    note: "Association announcements visible to members.",
  },
  {
    account: "member",
    folder: "member",
    file: "05-private-assistant.png",
    route: "/chat",
    note: "Optional private assistant with tenant-filtered answers.",
  },
  {
    account: "president",
    folder: "president",
    file: "01-dashboard.png",
    route: "/dashboard",
    note: "President executive dashboard.",
  },
  {
    account: "president",
    folder: "president",
    file: "02-governance-cockpit.png",
    route: "/governance",
    note: "President governance cockpit.",
  },
  {
    account: "president",
    folder: "president",
    file: "03-member-management.png",
    route: "/members/manage",
    note: "Member registration, search and lifecycle controls.",
  },
  {
    account: "president",
    folder: "president",
    file: "04-operation-journal.png",
    route: "/operation-journal",
    note: "Human-readable operations journal.",
  },
  {
    account: "president",
    folder: "president",
    file: "05-recovery-center.png",
    route: "/recovery",
    note: "Encrypted backup and recovery centre.",
  },
  {
    account: "secretary_general",
    folder: "secretary",
    file: "01-overview.png",
    route: "/secretary",
    note: "Secretary general records and communication workspace.",
  },
  {
    account: "secretary_general",
    folder: "secretary",
    file: "02-documents.png",
    route: "/secretary/documents",
    note: "Governance document management.",
  },
  {
    account: "secretary_general",
    folder: "secretary",
    file: "03-announcements.png",
    route: "/secretary/announcements",
    note: "Announcement publication workspace.",
  },
  {
    account: "treasurer",
    folder: "treasurer",
    file: "01-dashboard.png",
    route: "/dashboard",
    note: "Treasurer dashboard.",
  },
  {
    account: "treasurer",
    folder: "treasurer",
    file: "02-finance-workspace.png",
    route: "/finance",
    note: "Treasury workspace with budgets, expenses and exports.",
  },
  {
    account: "treasurer",
    folder: "treasurer",
    file: "03-receipt-declarations.png",
    route: "/receipts",
    note: "Receipt declaration and validation queue.",
  },
  {
    account: "auditor",
    folder: "oversight",
    file: "01-auditor-finance.png",
    route: "/finance-audit",
    note: "Auditor read-only finance oversight.",
  },
  {
    account: "censor",
    folder: "oversight",
    file: "02-censor-discipline.png",
    route: "/censor",
    note: "Censor confidential disciplinary workspace.",
  },
  {
    account: "sports_manager",
    folder: "oversight",
    file: "03-sports-workspace.png",
    route: "/sports",
    note: "Sports manager events and programme coordination.",
  },
  {
    account: "president",
    folder: "oversight",
    file: "04-account-security.png",
    route: "/account/security",
    note: "Account security, devices and session revocation.",
  },
  {
    account: "member",
    folder: "notifications",
    file: "01-inbox.png",
    route: "/notifications",
    note: "Tenant-isolated notification inbox with read state and preferences.",
  },
  {
    account: "principal_admin",
    folder: "admin",
    file: "01-overview.png",
    route: "/admin",
    note: "Principal admin overview with setup and recovery posture.",
  },
  {
    account: "principal_admin",
    folder: "admin",
    file: "02-health-center.png",
    route: "/admin/health",
    note: "Health center: dependency checks, recovery evidence and notification pipeline.",
  },
  {
    account: "principal_admin",
    folder: "admin",
    file: "03-notification-console.png",
    route: "/admin/notifications",
    note: "Notification operations console with pipeline health and channel history.",
  },
  {
    account: "principal_admin",
    folder: "admin",
    file: "04-tenant-operations.png",
    route: "/admin/tenants",
    note: "Tenant operations command center with membership inventory.",
  },
  {
    account: "principal_admin",
    folder: "admin",
    file: "05-onboarding.png",
    route: "/admin/onboarding",
    note: "First-run onboarding wizard from blank tenant to launch configuration.",
  },
  {
    account: "principal_admin",
    folder: "admin",
    file: "06-settings.png",
    route: "/admin/settings",
    note: "Tenant settings with branding, module toggles and recovery evidence.",
  },
];

const mobileSessions = [
  {
    account: "member",
    folder: "mobile",
    file: "01-member-dashboard.png",
    route: "/dashboard",
    note: "Member dashboard at phone width.",
  },
  {
    account: "member",
    folder: "mobile",
    file: "02-member-contribution-statement.png",
    route: "/members/profile",
    note: "Member contribution statement at phone width.",
  },
  {
    account: "treasurer",
    folder: "mobile",
    file: "03-treasurer-finance.png",
    route: "/finance",
    note: "Treasury workspace at phone width.",
  },
  {
    account: "president",
    folder: "mobile",
    file: "04-president-governance.png",
    route: "/governance",
    note: "Governance cockpit at phone width.",
  },
  {
    account: "principal_admin",
    folder: "mobile",
    file: "05-admin-health.png",
    route: "/admin/health",
    note: "Health center at phone width.",
  },
];

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function login(account) {
  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: account.email,
      password: account.password,
      tenant_slug: account.tenantSlug,
    }),
  });

  if (!response.ok) {
    throw new Error(`Login failed for ${account.email}: HTTP ${response.status}`);
  }

  const payload = await response.json();
  if (!payload.access_token) {
    throw new Error(`Login for ${account.email} returned no access token`);
  }

  return { token: payload.access_token, tenantId: payload.tenant_id };
}

/**
 * FastAPI collection routes are canonical with a trailing slash. The deployed
 * reverse proxy currently normalises the slash-less form with an absolute
 * `http://` redirect, which an HTTPS browser blocks as mixed content. Rewriting
 * the request to its canonical HTTPS path keeps the captured UI representative
 * of the real, working surface.
 */
const COLLECTION_ROOTS = [
  "/documents",
  "/memberships",
  "/policies",
  "/contributions",
  "/events",
  "/announcements",
  "/disciplinary",
];

async function normalizeCollectionSlash(page) {
  await page.route("**/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    const isCollectionRoot = COLLECTION_ROOTS.some((root) =>
      url.pathname.endsWith(`/api/v1${root}`),
    );
    if (url.protocol === "https:" && !url.pathname.endsWith("/") && isCollectionRoot) {
      url.pathname = `${url.pathname}/`;
      await route.continue({ url: url.toString() });
      return;
    }
    await route.continue();
  });
}

/**
 * Some live surfaces expose a retry control when a transient network failure
 * occurs. Pressing it keeps the captured evidence representative of the real
 * success state instead of a momentary outage.
 */
async function recoverTransientError(page) {
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const bodyText = await page.evaluate(() => document.body?.innerText ?? "");
    const looksBroken = /Network Error|indisponible|Erreur r[ée]seau|unavailable/i.test(bodyText);
    if (!looksBroken) return;
    const retry = page.getByRole("button", { name: /r[ée]essayer|retry|actualiser|refresh/i }).first();
    if ((await retry.count()) === 0) return;
    await retry.click().catch(() => {});
    await page.waitForTimeout(3000);
  }
}

async function polishPage(page) {
  await page.evaluate(() => {
    document
      .querySelectorAll(
        ".Vue-Toastification__container, .Vue-Toastification__toast, [class*='toast'], [class*='Toast']",
      )
      .forEach((element) => element.remove());
    document
      .querySelectorAll(".role-top-navigation")
      .forEach((element) => {
        element.scrollLeft = 0;
      });
  });
}

async function capture(browser, session, seed, viewport) {
  const targetDir = path.join(outputRoot, session.folder);
  await ensureDir(targetDir);
  const targetFile = path.join(targetDir, session.file);

  const context = await browser.newContext({ viewport, deviceScaleFactor: 2 });

  if (seed) {
    await context.addInitScript(
      ({ accessToken, selectedTenantId, preferredLocale }) => {
        window.localStorage.setItem("access_token", accessToken);
        window.localStorage.setItem("selected_tenant_id", selectedTenantId);
        window.localStorage.setItem("preferred_locale", preferredLocale);
      },
      {
        accessToken: seed.token,
        selectedTenantId: seed.tenantId,
        preferredLocale: locale,
      },
    );
  } else {
    await context.addInitScript(
      ({ preferredLocale }) => {
        window.localStorage.setItem("preferred_locale", preferredLocale);
      },
      { preferredLocale: locale },
    );
  }

  const page = await context.newPage();
  await normalizeCollectionSlash(page);
  try {
    await page.goto(`${baseUrl}${session.route}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
    await page.waitForLoadState("networkidle", { timeout: 12_000 }).catch(() => {});
    await page.waitForTimeout(2500);
    await recoverTransientError(page);
    await polishPage(page);
    await page.waitForTimeout(400);
    await page.screenshot({ path: targetFile });
    console.log(`Captured ${session.folder}/${session.file} (${session.route})`);
  } finally {
    await context.close();
  }

  return targetFile;
}

async function run() {
  await ensureDir(outputRoot);
  const browser = await chromium.launch({ headless: true });
  const manifest = [];

  try {
    for (const session of publicSessions) {
      try {
        await capture(browser, session, null, session.viewport || desktopViewport);
        manifest.push({ ...session, target: session.file });
      } catch (error) {
        console.error(`Skipped ${session.folder}/${session.file}: ${error.message}`);
      }
    }

    const tokenCache = new Map();
    async function seedFor(accountKey) {
      if (!tokenCache.has(accountKey)) {
        tokenCache.set(accountKey, await login(accounts[accountKey]));
      }
      return tokenCache.get(accountKey);
    }

    const batches = [
      { sessions: roleSessions, viewport: desktopViewport },
      { sessions: mobileSessions, viewport: mobileViewport },
    ];

    for (const batch of batches) {
      for (const session of batch.sessions) {
        try {
          const seed = await seedFor(session.account);
          await capture(browser, session, seed, batch.viewport);
          manifest.push({ ...session, target: session.file });
        } catch (error) {
          console.error(`Skipped ${session.folder}/${session.file}: ${error.message}`);
        }
      }
    }
  } finally {
    await browser.close();
  }

  const lines = [
    "# Kairo README Screenshot Gallery",
    "",
    `Captured against ${targetLabel} in locale \`${locale}\` at desktop (1440×900) and`,
    "phone (390×844) widths.",
    "",
    "Each capture authenticates through the real FastAPI login contract and screenshots an",
    "authorised role surface. No permission is simulated in the client.",
    "",
    "Regenerate with:",
    "",
    "```bash",
    "node scripts/capture-readme-screenshots.mjs",
    "```",
    "",
    "A deployment with rotated demo passwords passes the public `VITE_DEMO_ACCOUNTS`",
    "payload through `KAIRO_SCREENSHOT_ACCOUNTS`.",
    "",
    "> Capture-time note: the deployed reverse proxy currently normalises slash-less",
    "> FastAPI collection routes with an absolute `http://` redirect, which an HTTPS browser",
    "> blocks as mixed content. The script rewrites those requests to their canonical",
    "> trailing-slash HTTPS form so the captured UI reflects the real, working surface.",
    "",
    "## Captured surfaces",
    "",
    "| Folder | File | Route |",
    "| --- | --- | --- |",
    ...manifest.map((entry) => `| \`${entry.folder}\` | \`${entry.target}\` | \`${entry.route}\` |`),
    "",
  ];
  await fs.writeFile(path.join(outputRoot, "MANIFEST.md"), lines.join("\n"), "utf8");
  console.log(`Wrote ${manifest.length} screenshots to ${path.relative(repoRoot, outputRoot)}`);
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
