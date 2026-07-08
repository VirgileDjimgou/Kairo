import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "../apps/web/node_modules/playwright/index.mjs";

const repoRoot = process.cwd();
const baseUrl = process.env.KAIRO_WEB_BASE_URL || "http://localhost:5173";
const outputRoot = path.join(
  repoRoot,
  "apps",
  "web",
  "artifacts",
  "manual-role-checks",
  "2026-07-07-live-audit",
);

const roles = [
  {
    folder: "00-login-fr",
    label: "Login page in French",
    locale: "fr",
    account: null,
    password: null,
    route: "/login",
    capture: "login-fr.png",
    kind: "login",
  },
  {
    folder: "01-login-en",
    label: "Login page in English",
    locale: "en",
    account: null,
    password: null,
    route: "/login",
    capture: "login-en.png",
    kind: "login",
  },
  {
    folder: "02-login-de",
    label: "Login page in German",
    locale: "de",
    account: null,
    password: null,
    route: "/login",
    capture: "login-de.png",
    kind: "login",
  },
  {
    folder: "03-member-fr",
    label: "Member workspace in French",
    locale: "fr",
    account: "alice@demo.org",
    password: "Member123!",
    route: "/members/profile",
    capture: "member-profile-fr.png",
    kind: "workspace",
  },
  {
    folder: "04-treasurer-fr",
    label: "Treasurer workspace in French",
    locale: "fr",
    account: "treasurer@demo.org",
    password: "Treasurer123!",
    route: "/finance",
    capture: "treasurer-finance-fr.png",
    kind: "workspace",
  },
  {
    folder: "05-auditor-fr",
    label: "Auditor workspace in French",
    locale: "fr",
    account: "auditor@demo.org",
    password: "Auditor123!",
    route: "/finance-audit",
    capture: "auditor-audit-fr.png",
    kind: "workspace",
  },
  {
    folder: "06-censor-fr",
    label: "Censor workspace in French",
    locale: "fr",
    account: "censor@demo.org",
    password: "Censor123!",
    route: "/censor",
    capture: "censor-workspace-fr.png",
    kind: "workspace",
  },
  {
    folder: "07-sports-fr",
    label: "Sports manager workspace in French",
    locale: "fr",
    account: "sports@demo.org",
    password: "Sports123!",
    route: "/sports",
    capture: "sports-workspace-fr.png",
    kind: "workspace",
  },
  {
    folder: "08-secretary-de",
    label: "Secretary general workspace in German",
    locale: "de",
    account: "secretary@demo.org",
    password: "Secretary123!",
    route: "/secretary",
    capture: "secretary-workspace-de.png",
    kind: "workspace",
  },
  {
    folder: "09-president-en",
    label: "President governance cockpit in English",
    locale: "en",
    account: "president@demo.org",
    password: "President123!",
    route: "/governance",
    capture: "president-governance-en.png",
    kind: "workspace",
  },
  {
    folder: "10-vice-president-en",
    label: "Vice president governance cockpit in English",
    locale: "en",
    account: "vice-president@demo.org",
    password: "VicePresident123!",
    route: "/governance",
    capture: "vice-president-governance-en.png",
    kind: "workspace",
  },
  {
    folder: "11-principal-admin-en",
    label: "Principal admin overview in English",
    locale: "en",
    account: "principal@demo.org",
    password: "Principal123!",
    route: "/admin",
    capture: "principal-admin-overview-en.png",
    kind: "workspace",
  },
  {
    folder: "12-member-chat-fr",
    label: "Member chat authorization checks in French",
    locale: "fr",
    account: "alice@demo.org",
    password: "Member123!",
    route: "/chat",
    capture: "member-chat-fr.png",
    kind: "member-chat",
  },
  {
    folder: "13-secretary-chat-de",
    label: "Secretary publication chat in German",
    locale: "de",
    account: "secretary@demo.org",
    password: "Secretary123!",
    route: "/chat",
    capture: "secretary-chat-de.png",
    kind: "chat",
  },
  {
    folder: "14-president-chat-en",
    label: "President governance chat in English",
    locale: "en",
    account: "president@demo.org",
    password: "President123!",
    route: "/chat",
    capture: "president-chat-en.png",
    kind: "chat",
  },
  {
    folder: "15-principal-admin-chat-en",
    label: "Principal admin chat in English",
    locale: "en",
    account: "principal@demo.org",
    password: "Principal123!",
    route: "/chat",
    capture: "principal-admin-chat-en.png",
    kind: "chat",
  },
  {
    folder: "16-auditor-chat-fr",
    label: "Auditor finance chat in French",
    locale: "fr",
    account: "auditor@demo.org",
    password: "Auditor123!",
    route: "/chat",
    capture: "auditor-chat-fr.png",
    kind: "chat",
  },
  {
    folder: "17-censor-chat-fr",
    label: "Censor disciplinary chat in French",
    locale: "fr",
    account: "censor@demo.org",
    password: "Censor123!",
    route: "/chat",
    capture: "censor-chat-fr.png",
    kind: "chat",
  },
  {
    folder: "18-sports-chat-fr",
    label: "Sports manager schedule chat in French",
    locale: "fr",
    account: "sports@demo.org",
    password: "Sports123!",
    route: "/chat",
    capture: "sports-chat-fr.png",
    kind: "chat",
  },
  {
    folder: "19-treasurer-chat-fr",
    label: "Treasurer finance chat in French",
    locale: "fr",
    account: "treasurer@demo.org",
    password: "Treasurer123!",
    route: "/chat",
    capture: "treasurer-chat-fr.png",
    kind: "chat",
  },
];

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeSessionManifest(dir, session, capturedFiles) {
  const lines = [
    `# ${session.label}`,
    "",
    `- Locale: \`${session.locale}\``,
    session.account ? `- Account: \`${session.account}\`` : "- Account: login page",
    `- Route: \`${session.route}\``,
    "",
    "## Captures",
    ...capturedFiles.map((file) => `- ${file}`),
    "",
  ];
  await fs.writeFile(path.join(dir, "SESSION.md"), lines.join("\n"), "utf8");
}

async function selectLocale(page, locale) {
  const select = page.locator("select").first();
  await select.selectOption(locale);
  await page.waitForFunction(
    (expected) => document.documentElement.lang === expected,
    locale,
    { timeout: 15000 },
  );
}

async function login(page, locale, email, password) {
  await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle" });
  await selectLocale(page, locale);
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(password);
  await page.locator("button[type='submit']").click();
  await page.waitForTimeout(4000);
}

async function captureLogin(page, locale) {
  await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle" });
  await selectLocale(page, locale);
  await page.waitForTimeout(400);
}

async function captureWorkspace(page, route) {
  await page.goto(`${baseUrl}${route}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
}

async function sendChatQuestion(page, question) {
  await page.locator("textarea").waitFor({ state: "visible", timeout: 30000 });
  await page.locator("textarea").fill(question);
  await page.locator("button[type='submit']").click();
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1500);
}

async function captureSession(page, sessionDir, session) {
  const capturedFiles = [];
  console.log(`Capturing ${session.folder}`);

  if (session.kind === "login") {
    await captureLogin(page, session.locale);
    const target = path.join(sessionDir, session.capture);
    await page.screenshot({ path: target, fullPage: true });
    capturedFiles.push(session.capture);
    await writeSessionManifest(sessionDir, session, capturedFiles);
    return;
  }

  if (!session.account || !session.password) {
    throw new Error(`Missing credentials for ${session.folder}`);
  }

  await login(page, session.locale, session.account, session.password);

  if (session.kind === "workspace") {
    await captureWorkspace(page, session.route);
    const target = path.join(sessionDir, session.capture);
    await page.screenshot({ path: target, fullPage: true });
    capturedFiles.push(session.capture);
    await writeSessionManifest(sessionDir, session, capturedFiles);
    return;
  }

  await page.goto(`${baseUrl}${session.route}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(2000);

  switch (session.folder) {
    case "12-member-chat-fr":
      await sendChatQuestion(page, "What is my balance?");
      await page.waitForTimeout(400);
      await sendChatQuestion(page, "What is another member's balance?");
      break;
    case "13-secretary-chat-de":
      await sendChatQuestion(page, "Show the official publication context.");
      break;
    case "14-president-chat-en":
      await sendChatQuestion(page, "Give me a governance summary.");
      break;
    case "15-principal-admin-chat-en":
      await sendChatQuestion(page, "Give me a governance summary.");
      break;
    case "16-auditor-chat-fr":
      await sendChatQuestion(page, "Give me a finance summary.");
      break;
    case "17-censor-chat-fr":
      await sendChatQuestion(page, "Give me a disciplinary summary.");
      break;
    case "18-sports-chat-fr":
      await sendChatQuestion(page, "Show the sports schedule.");
      break;
    case "19-treasurer-chat-fr":
      await sendChatQuestion(page, "Give me a finance summary.");
      break;
    default:
      break;
  }

  const target = path.join(sessionDir, session.capture);
  await page.screenshot({ path: target, fullPage: true });
  capturedFiles.push(session.capture);
  await writeSessionManifest(sessionDir, session, capturedFiles);
}

async function run() {
  await ensureDir(outputRoot);
  const browser = await chromium.launch({ headless: true });
  try {
    for (const session of roles) {
      const sessionDir = path.join(outputRoot, session.folder);
      await ensureDir(sessionDir);
      const context = await browser.newContext({
        viewport: { width: 1440, height: 1100 },
      });
      const page = await context.newPage();
      try {
        await captureSession(page, sessionDir, session);
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
