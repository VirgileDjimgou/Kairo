import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "../apps/web/node_modules/playwright/index.mjs";

const repoRoot = process.cwd();
const baseUrl = process.env.KAIRO_DEMO_BASE_URL || "http://localhost:5173";
const outputRoot = path.join(repoRoot, "docs", "github-demo", "sessions");

const sessions = [
  {
    folder: "00-admin",
    label: "Admin",
    account: "admin@demo.org",
    password: "Admin123!",
    note:
      "Platform administrator walkthrough using the seeded admin account.",
    steps: [
      { route: "/login", file: "01-login.png", waitFor: "Sign in to your organization" },
      { route: "/admin", file: "02-admin-overview.png", waitFor: "Admin overview" },
      { route: "/admin/members", file: "03-admin-members.png", waitFor: "Members" },
      { route: "/admin/documents", file: "04-admin-documents.png", waitFor: "Documents" },
    ],
  },
  {
    folder: "01-member-alice",
    label: "Member Alice",
    account: "alice@demo.org",
    password: "Member123!",
    note:
      "Standard member journey including profile, balance, and an answered AI chat.",
    steps: [
      { route: "/dashboard", file: "01-member-dashboard.png", waitFor: "Welcome back" },
      { route: "/members/profile", file: "02-member-profile.png", waitFor: "Contribution Balance" },
      { route: "/chat", file: "03-member-chat-answer.png", waitFor: "Membership Fee Policy (RAG Demo)", chatQuestion: "How much are the annual membership fees?" },
      { route: "/announcements", file: "04-member-announcements.png", waitFor: "Announcements" },
    ],
  },
  {
    folder: "02-member-bob",
    label: "Member Bob",
    account: "bob@demo.org",
    password: "Member123!",
    note:
      "Second member journey focused on operational use: dashboard, balance, and events.",
    steps: [
      { route: "/dashboard", file: "01-member-dashboard.png", waitFor: "Welcome back" },
      { route: "/members/profile", file: "02-member-profile.png", waitFor: "Contribution Balance" },
      { route: "/events", file: "03-member-events.png", waitFor: "Events" },
    ],
  },
  {
    folder: "03-treasurer",
    label: "Treasurer",
    account: "treasurer@demo.org",
    password: "Treasurer123!",
    note:
      "Treasurer walkthrough focused on the role-aware dashboard, finance workspace, and account security surface.",
    steps: [
      { route: "/dashboard", file: "01-treasurer-dashboard.png", waitFor: "Welcome back" },
      {
        route: "/finance",
        file: "02-treasurer-finance-workspace.png",
        waitFor: "Treasury operations",
        financeMemberLabel: "Alice Johnson (MEM-001)",
      },
      { route: "/account/security", file: "03-treasurer-security.png", waitFor: "Account Security" },
    ],
  },
  {
    folder: "04-president",
    label: "President Persona",
    account: "admin@demo.org",
    password: "Admin123!",
    note:
      "Association president persona mapped to the current admin role in Kairo. This session emphasizes policy and event governance.",
    steps: [
      { route: "/admin/policies", file: "01-president-policies.png", waitFor: "Policy administration" },
      { route: "/admin/events", file: "02-president-events.png", waitFor: "Events" },
      { route: "/admin/chat-queries", file: "03-president-chat-audit.png", waitFor: "Chat traceability" },
    ],
  },
  {
    folder: "05-secretary",
    label: "Secretary Persona",
    account: "admin@demo.org",
    password: "Admin123!",
    note:
      "Association secretary persona mapped to the current admin role in Kairo. This session emphasizes announcements, documents, and audit visibility.",
    steps: [
      { route: "/admin/announcements", file: "01-secretary-announcements.png", waitFor: "Announcements" },
      { route: "/admin/documents", file: "02-secretary-documents.png", waitFor: "Documents" },
      { route: "/admin/audit", file: "03-secretary-audit.png", waitFor: "Audit trail" },
    ],
  },
];

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeSessionManifest(dir, session, capturedFiles) {
  const lines = [
    `# ${session.label}`,
    "",
    `- Account: \`${session.account}\``,
    `- Purpose: ${session.note}`,
    "",
    "## Captures",
    ...capturedFiles.map((file) => `- ${file}`),
    "",
  ];
  await fs.writeFile(path.join(dir, "SESSION.md"), lines.join("\n"), "utf8");
}

async function login(page, email, password) {
  await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle" });
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(password);
  await Promise.all([
    page.waitForURL((url) => !url.pathname.endsWith("/login"), { timeout: 30000 }),
    page.locator("button[type='submit']").click(),
  ]);
  await page.waitForLoadState("networkidle");
}

async function waitForText(page, text) {
  await page.waitForFunction(
    (expected) => document.body?.innerText?.includes(expected),
    text,
    { timeout: 30000 },
  );
}

async function captureStep(page, sessionDir, step) {
  console.log(`Capturing ${path.basename(sessionDir)} -> ${step.route} -> ${step.file}`);
  await page.goto(`${baseUrl}${step.route}`, { waitUntil: "networkidle" });

  if (step.financeMemberLabel) {
    await page.locator("#finance-balance-member").selectOption({ label: step.financeMemberLabel });
    await page.waitForSelector('[data-testid="finance-member-balance"]', { timeout: 30000 });
  }

  if (step.chatQuestion) {
    await page.locator("textarea").fill(step.chatQuestion);
    await page.getByRole("button", { name: "Ask question" }).click();
  }

  if (step.waitFor) {
    await waitForText(page, step.waitFor);
  }

  const target = path.join(sessionDir, step.file);
  await page.screenshot({ path: target, fullPage: true });
  return step.file;
}

async function run() {
  await ensureDir(outputRoot);
  const browser = await chromium.launch({ headless: true });

  try {
    for (const session of sessions) {
      const sessionDir = path.join(outputRoot, session.folder);
      await ensureDir(sessionDir);

      const context = await browser.newContext({
        viewport: { width: 1440, height: 1100 },
      });
      const page = await context.newPage();
      const capturedFiles = [];
      let isAuthenticated = false;

      try {
        for (const step of session.steps) {
          if (step.route === "/login") {
            console.log(`Capturing ${session.folder} -> ${step.route} -> ${step.file}`);
            await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle" });
            if (step.waitFor) {
              await waitForText(page, step.waitFor);
            }
            const target = path.join(sessionDir, step.file);
            await page.screenshot({ path: target, fullPage: true });
            capturedFiles.push(step.file);
            continue;
          }

          if (!isAuthenticated) {
            await login(page, session.account, session.password);
            isAuthenticated = true;
          }

          capturedFiles.push(await captureStep(page, sessionDir, step));
        }

        await writeSessionManifest(sessionDir, session, capturedFiles);
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
