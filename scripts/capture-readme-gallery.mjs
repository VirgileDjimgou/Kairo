import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { spawn } from "node:child_process";
import { chromium } from "../apps/web/node_modules/playwright/index.mjs";

const repoRoot = process.cwd();
const appRoot = path.join(repoRoot, "apps", "web");
const outputRoot = path.join(repoRoot, "docs", "github-demo", "role-gallery");
const galleryPort = process.env.KAIRO_DEMO_PORT || "4173";
const baseUrl = process.env.KAIRO_DEMO_BASE_URL || `http://127.0.0.1:${galleryPort}`;
const shouldStartWeb = !process.env.KAIRO_DEMO_BASE_URL;
const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";

const modules = {
  membership: true,
  contributions: true,
  policies: true,
  disciplinary: true,
  events: true,
  announcements: true,
  chat: true,
  notifications: true,
};

const demoTenant = {
  tenant_id: "tenant-demo-1",
  slug: "demo",
  name: "Acme Community Organization",
  branding: {
    primary_color: "#1f4f8f",
    logo_url: "",
  },
};

const secondaryTenant = {
  tenant_id: "tenant-riverdale-1",
  slug: "riverdale",
  name: "Riverdale Sports Union",
  branding: {
    primary_color: "#2f6f55",
    logo_url: "",
  },
};

const demoMembers = [
  buildMember(demoTenant, "member-1", "MEM-001", "Alice", "Johnson", "alice@demo.org"),
  buildMember(demoTenant, "member-2", "MEM-002", "Bob", "Smith", "bob@demo.org"),
  buildMember(demoTenant, "member-3", "TRE-001", "Carol", "Williams", "treasurer@demo.org"),
];

const demoContributions = [
  buildContribution(demoTenant, "contrib-1", "member-1", 2026, "120.00", "45.00", "partial"),
  buildContribution(demoTenant, "contrib-2", "member-2", 2026, "120.00", "120.00", "paid"),
];

const demoPayments = [
  buildPayment(demoTenant, "payment-1", "contrib-1", "45.00", "bank_transfer", "INV-001"),
  buildPayment(demoTenant, "payment-2", "contrib-2", "120.00", "cash", null),
];

const demoDocuments = [
  buildDocument(demoTenant, "doc-1", "Community Association Bylaws", "Official statutes and governance rules."),
  buildDocument(demoTenant, "doc-2", "Meeting Minutes - Q1 2026", "Board decisions and operational follow-up."),
  buildDocument(demoTenant, "doc-3", "Membership Fee Policy", "Reference material for dues and deadlines."),
];

const demoPolicies = [
  buildPolicy(demoTenant, "policy-1", "Membership Fee Policy", "finance"),
  buildPolicy(demoTenant, "policy-2", "Code of Conduct", "governance"),
];

const demoAnnouncements = [
  buildAnnouncement(demoTenant, "ann-1", "Summer assembly confirmed"),
  buildAnnouncement(demoTenant, "ann-2", "Registration desk opens next week"),
];

const demoEvents = [
  buildEvent(demoTenant, "evt-1", "Annual General Meeting", "2026-07-15T18:00:00Z", "Main hall"),
  buildEvent(demoTenant, "evt-2", "Volunteer induction evening", "2026-07-21T18:30:00Z", "Community room"),
];

const demoSportsEvents = [
  buildEvent(
    demoTenant,
    "sports-1",
    "Weekly training",
    "2026-07-10T18:00:00Z",
    "Pitch 1",
    {
      description: "Open training for registered players.",
      metadata_json: { workspace: "sports", sport_type: "training" },
    },
  ),
  buildEvent(
    demoTenant,
    "sports-2",
    "Club championship",
    "2026-07-20T18:00:00Z",
    "Main stadium",
    {
      description: "Evening match for the summer series.",
      metadata_json: { workspace: "sports", sport_type: "match" },
    },
  ),
];

const demoDisciplinaryRecords = [
  {
    id: "disc-1",
    tenant_id: demoTenant.tenant_id,
    membership_profile_id: "member-1",
    membership_display_name: "Alice Johnson",
    policy_record_id: "policy-2",
    policy_title: "Code of Conduct",
    title: "Late arrival warning",
    description: "Repeated late arrivals to the general assembly.",
    amount: "25.00",
    currency: "EUR",
    status: "under_review",
    recorded_by: "user-censor-1",
    recorded_at: "2026-06-30T08:30:00Z",
    created_at: "2026-06-30T08:30:00Z",
    updated_at: "2026-06-30T08:30:00Z",
  },
];

const demoAuditEvents = [
  buildAuditEvent(demoTenant, "audit-1", "documents", "upload", "document", "doc-1"),
  buildAuditEvent(demoTenant, "audit-2", "contributions", "record_payment", "payment", "payment-1"),
];

const demoChannels = [
  {
    channel: "email",
    display_name: "Email",
    description: "SMTP-backed provider placeholder for transactional or broadcast email.",
    configured: true,
    simulation_only: true,
    target_hint: "ops@example.org",
  },
  {
    channel: "telegram",
    display_name: "Telegram",
    description: "Bot-based provider placeholder for direct or channel-based Telegram messages.",
    configured: false,
    simulation_only: true,
    target_hint: "@association-channel",
  },
];

const riverdaleMembers = [
  buildMember(secondaryTenant, "r-member-1", "RSU-001", "Nina", "Rivera", "nina@riverdale.org"),
  buildMember(secondaryTenant, "r-member-2", "RSU-002", "Liam", "Patel", "liam@riverdale.org"),
];

const riverdaleContributions = [
  buildContribution(secondaryTenant, "r-contrib-1", "r-member-1", 2026, "80.00", "80.00", "paid"),
  buildContribution(secondaryTenant, "r-contrib-2", "r-member-2", 2026, "80.00", "50.00", "partial"),
];

const tenantData = {
  [demoTenant.tenant_id]: {
    tenant: demoTenant,
    members: demoMembers,
    contributions: demoContributions,
    payments: demoPayments,
    documents: demoDocuments,
    policies: demoPolicies,
    announcements: demoAnnouncements,
    events: demoEvents,
    sportsEvents: demoSportsEvents,
    disciplinaryRecords: demoDisciplinaryRecords,
    auditEvents: demoAuditEvents,
    channels: demoChannels,
    ingestionHealth: {
      queued_count: 1,
      processing_count: 0,
      failed_count: 0,
      completed_count: 6,
      retried_count: 1,
      recent_failures: [],
    },
  },
  [secondaryTenant.tenant_id]: {
    tenant: secondaryTenant,
    members: riverdaleMembers,
    contributions: riverdaleContributions,
    payments: [
      buildPayment(secondaryTenant, "r-payment-1", "r-contrib-2", "50.00", "bank_transfer", "RSU-050"),
    ],
    documents: [
      buildDocument(secondaryTenant, "r-doc-1", "Season Playbook", "Operational guide for coaches and teams."),
      buildDocument(secondaryTenant, "r-doc-2", "Volunteer Roster", "Contacts and shifts for match days."),
    ],
    policies: [buildPolicy(secondaryTenant, "r-policy-1", "Equipment Policy", "sports")],
    announcements: [buildAnnouncement(secondaryTenant, "r-ann-1", "Away game coach briefing")],
    events: [
      buildEvent(secondaryTenant, "r-evt-1", "League away fixture", "2026-07-19T14:00:00Z", "North Arena"),
    ],
    sportsEvents: [
      buildEvent(secondaryTenant, "r-sports-1", "Junior training camp", "2026-07-18T09:00:00Z", "Riverdale field", {
        metadata_json: { workspace: "sports", sport_type: "camp" },
      }),
    ],
    disciplinaryRecords: [],
    auditEvents: [buildAuditEvent(secondaryTenant, "r-audit-1", "events", "create", "event", "r-evt-1")],
    channels: demoChannels,
    ingestionHealth: {
      queued_count: 0,
      processing_count: 0,
      failed_count: 0,
      completed_count: 3,
      retried_count: 0,
      recent_failures: [],
    },
  },
};

const roleSessions = [
  {
    folder: "00-public-entry",
    title: "Public entry surface",
    note: "Commercial landing and login surface before authentication.",
    file: "01-public-entry.png",
    route: "/login",
    waitForText: "Private AI for organizations that need control, citations, and tenant boundaries.",
    setup: async () => {},
  },
  {
    folder: "01-tenant-picker",
    title: "Tenant picker",
    note: "A multi-tenant account chooses its active organization after sign-in.",
    file: "01-tenant-picker.png",
    route: "/login",
    waitForText: "Choose organization",
    setup: async (page) => {
      await installMockApi(page, {
        loginMode: "interactive",
        currentTenant: demoTenant,
        memberships: [
          makeMembership("principal_admin", demoTenant, "admin"),
          makeMembership("principal_admin", secondaryTenant, "admin"),
        ],
        user: makeUser("principal_admin", {
          email: "principal@demo.org",
          displayName: "Priya Principal",
          profileType: "admin",
          tenant: demoTenant,
          memberships: [
            makeMembership("principal_admin", demoTenant, "admin"),
            makeMembership("principal_admin", secondaryTenant, "admin"),
          ],
        }),
      });
      await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle" });
      await page.locator("#email").fill("principal@demo.org");
      await page.locator("#password").fill("Principal123!");
      await page.getByRole("button", { name: "Sign in" }).click();
    },
  },
  {
    folder: "02-member",
    title: "Member portal",
    note: "Read-first member workspace with personal contribution statement only.",
    file: "01-member-statement.png",
    route: "/members/profile",
    waitForText: "My profile and contribution statement",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("member", demoTenant, "member")],
        user: makeUser("member", {
          email: "alice@demo.org",
          displayName: "Alice Johnson",
          profileType: "member",
          tenant: demoTenant,
          memberships: [makeMembership("member", demoTenant, "member")],
        }),
      });
    },
  },
  {
    folder: "03-secretary-general",
    title: "Secretary general workspace",
    note: "Dedicated communication and records workspace without finance access.",
    file: "01-secretary-overview.png",
    route: "/secretary",
    waitForText: "Official records and communication workspace",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("secretary_general", demoTenant, "staff")],
        user: makeUser("secretary_general", {
          email: "secretary@demo.org",
          displayName: "Dana Secretary",
          profileType: "staff",
          tenant: demoTenant,
          memberships: [makeMembership("secretary_general", demoTenant, "staff")],
        }),
      });
    },
  },
  {
    folder: "04-treasurer",
    title: "Treasurer workspace",
    note: "Focused finance workspace with member balance lookup and payment context.",
    file: "01-treasurer-finance.png",
    route: "/finance",
    waitForText: "Treasury operations",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("treasurer", demoTenant, "staff")],
        user: makeUser("treasurer", {
          email: "treasurer@demo.org",
          displayName: "Carol Williams",
          profileType: "staff",
          tenant: demoTenant,
          memberships: [makeMembership("treasurer", demoTenant, "staff")],
        }),
      });
    },
    afterLoad: async (page) => {
      await page.locator("#finance-balance-member").selectOption({ label: "Alice Johnson (MEM-001)" });
      await page.waitForSelector('[data-testid="finance-member-balance"]', { timeout: 30000 });
    },
  },
  {
    folder: "05-auditor",
    title: "Auditor workspace",
    note: "Read-only finance oversight for controls and export readiness.",
    file: "01-auditor-finance.png",
    route: "/finance-audit",
    waitForText: "Read-only finance oversight",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("auditor", demoTenant, "staff")],
        user: makeUser("auditor", {
          email: "auditor@demo.org",
          displayName: "Evan Auditor",
          profileType: "staff",
          tenant: demoTenant,
          memberships: [makeMembership("auditor", demoTenant, "staff")],
        }),
      });
    },
  },
  {
    folder: "06-censor",
    title: "Censor workspace",
    note: "Disciplinary console with explicit privacy boundaries and audited mutations.",
    file: "01-censor-workspace.png",
    route: "/censor",
    waitForText: "Censor workspace",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("censor", demoTenant, "staff")],
        user: makeUser("censor", {
          email: "censor@demo.org",
          displayName: "Fiona Censor",
          profileType: "staff",
          tenant: demoTenant,
          memberships: [makeMembership("censor", demoTenant, "staff")],
        }),
      });
    },
  },
  {
    folder: "07-sports-manager",
    title: "Sports manager workspace",
    note: "Role-scoped sports operations surface separated from general administration.",
    file: "01-sports-workspace.png",
    route: "/sports",
    waitForText: "Sports workspace",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("sports_manager", demoTenant, "staff")],
        user: makeUser("sports_manager", {
          email: "sports@demo.org",
          displayName: "Gabe Sports",
          profileType: "staff",
          tenant: demoTenant,
          memberships: [makeMembership("sports_manager", demoTenant, "staff")],
        }),
      });
    },
  },
  {
    folder: "08-president",
    title: "President governance cockpit",
    note: "Executive oversight with finance-audit visibility and audit access.",
    file: "01-president-governance.png",
    route: "/governance",
    waitForText: "President governance cockpit",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("president", demoTenant, "staff")],
        user: makeUser("president", {
          email: "president@demo.org",
          displayName: "Hana President",
          profileType: "staff",
          tenant: demoTenant,
          memberships: [makeMembership("president", demoTenant, "staff")],
        }),
      });
    },
  },
  {
    folder: "09-vice-president",
    title: "Vice president governance cockpit",
    note: "Narrower executive oversight without audit-trail shortcut exposure.",
    file: "01-vice-president-governance.png",
    route: "/governance",
    waitForText: "Vice president governance cockpit",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("vice_president", demoTenant, "staff")],
        user: makeUser("vice_president", {
          email: "vice-president@demo.org",
          displayName: "Iris Vice President",
          profileType: "staff",
          tenant: demoTenant,
          memberships: [makeMembership("vice_president", demoTenant, "staff")],
        }),
      });
    },
  },
  {
    folder: "10-principal-admin",
    title: "Principal admin control plane",
    note: "Tenant-wide administrative oversight with operations, access, and settings posture.",
    file: "01-principal-admin-overview.png",
    route: "/admin",
    waitForText: "Principal admin overview",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [makeMembership("principal_admin", demoTenant, "admin")],
        user: makeUser("principal_admin", {
          email: "principal@demo.org",
          displayName: "Priya Principal",
          profileType: "admin",
          tenant: demoTenant,
          memberships: [makeMembership("principal_admin", demoTenant, "admin")],
        }),
      });
    },
  },
  {
    folder: "11-tenant-switcher",
    title: "Tenant switcher",
    note: "Authenticated multi-tenant shell showing organization switching in the compact top bar.",
    file: "01-tenant-switcher-open.png",
    route: "/dashboard",
    waitForText: "Welcome back, Priya Principal",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: demoTenant,
        memberships: [
          makeMembership("principal_admin", demoTenant, "admin"),
          makeMembership("principal_admin", secondaryTenant, "admin"),
        ],
        user: makeUser("principal_admin", {
          email: "principal@demo.org",
          displayName: "Priya Principal",
          profileType: "admin",
          tenant: demoTenant,
          memberships: [
            makeMembership("principal_admin", demoTenant, "admin"),
            makeMembership("principal_admin", secondaryTenant, "admin"),
          ],
        }),
      });
    },
    afterLoad: async (page) => {
      await page.locator(".tenant-switcher .dropdown-toggle").click();
      await page.waitForSelector(".tenant-switcher .dropdown-menu.show", { timeout: 30000 });
    },
  },
  {
    folder: "12-secondary-tenant",
    title: "Secondary tenant shell",
    note: "Second organization selected with distinct branding and tenant-scoped data.",
    file: "01-secondary-tenant-dashboard.png",
    route: "/dashboard",
    waitForText: "Riverdale Sports Union",
    setup: async (page) => {
      await installMockApi(page, {
        preAuth: true,
        currentTenant: secondaryTenant,
        memberships: [
          makeMembership("principal_admin", demoTenant, "admin"),
          makeMembership("principal_admin", secondaryTenant, "admin"),
        ],
        user: makeUser("principal_admin", {
          email: "principal@demo.org",
          displayName: "Priya Principal",
          profileType: "admin",
          tenant: secondaryTenant,
          memberships: [
            makeMembership("principal_admin", demoTenant, "admin"),
            makeMembership("principal_admin", secondaryTenant, "admin"),
          ],
        }),
        selectedTenantId: secondaryTenant.tenant_id,
      });
    },
  },
];

function buildMember(tenant, id, memberCode, firstName, lastName, email) {
  return {
    id,
    tenant_id: tenant.tenant_id,
    user_id: `user-${id}`,
    member_code: memberCode,
    first_name: firstName,
    last_name: lastName,
    display_name: `${firstName} ${lastName}`,
    email,
    phone: null,
    status: "active",
    joined_at: "2026-01-10T09:00:00Z",
    created_at: "2026-01-10T09:00:00Z",
    updated_at: "2026-01-10T09:00:00Z",
  };
}

function buildContribution(tenant, id, membershipProfileId, year, expectedAmount, paidAmount, status) {
  const balance = (Number(expectedAmount) - Number(paidAmount)).toFixed(2);
  return {
    id,
    tenant_id: tenant.tenant_id,
    membership_profile_id: membershipProfileId,
    year,
    expected_amount: expectedAmount,
    paid_amount: paidAmount,
    balance,
    currency: "EUR",
    status,
    due_date: null,
    created_at: "2026-03-01T10:00:00Z",
    updated_at: "2026-03-15T10:00:00Z",
  };
}

function buildPayment(tenant, id, contributionRecordId, amount, paymentMethod, reference) {
  return {
    id,
    tenant_id: tenant.tenant_id,
    contribution_record_id: contributionRecordId,
    amount,
    currency: "EUR",
    paid_at: "2026-03-15T10:00:00Z",
    payment_method: paymentMethod,
    reference,
    recorded_by: "user-treasurer-1",
    created_at: "2026-03-15T10:00:00Z",
  };
}

function buildDocument(tenant, id, title, description) {
  return {
    id,
    tenant_id: tenant.tenant_id,
    title,
    description,
    source_type: "upload",
    language: "en",
    access_scope: "members_only",
    allowed_role_ids: null,
    status: "ready",
    owner_user_id: null,
    created_at: "2026-07-01T09:00:00Z",
    current_version: null,
  };
}

function buildPolicy(tenant, id, title, category) {
  return {
    id,
    tenant_id: tenant.tenant_id,
    title,
    category,
    description: `${title} reference for the tenant.`,
    status: "published",
    document_id: null,
    created_at: "2026-02-01T09:00:00Z",
    updated_at: "2026-02-01T09:00:00Z",
  };
}

function buildAnnouncement(tenant, id, title) {
  return {
    id,
    tenant_id: tenant.tenant_id,
    title,
    body: `${title} for members and office roles.`,
    visibility_scope: "members_only",
    published_at: "2026-07-01T00:00:00Z",
    expires_at: null,
    created_by: "user-admin-1",
    created_at: "2026-07-01T00:00:00Z",
    updated_at: "2026-07-01T00:00:00Z",
  };
}

function buildEvent(tenant, id, title, startAt, location, overrides = {}) {
  return {
    id,
    tenant_id: tenant.tenant_id,
    title,
    description: overrides.description || `${title} scheduled for the tenant calendar.`,
    start_at: startAt,
    end_at: overrides.end_at || startAt,
    location,
    visibility_scope: overrides.visibility_scope || "members_only",
    status: overrides.status || "published",
    metadata_json: overrides.metadata_json || {},
    created_by: "user-admin-1",
    created_at: "2026-07-01T00:00:00Z",
    updated_at: "2026-07-01T00:00:00Z",
  };
}

function buildAuditEvent(tenant, id, moduleKey, action, entityType, entityId) {
  return {
    id,
    tenant_id: tenant.tenant_id,
    actor_user_id: "user-admin-1",
    module_key: moduleKey,
    action,
    entity_type: entityType,
    entity_id: entityId,
    details: {},
    created_at: "2026-07-01T00:00:00Z",
  };
}

function makeMembership(roleCode, tenant, profileType) {
  return {
    tenant_id: tenant.tenant_id,
    slug: tenant.slug,
    name: tenant.name,
    roles: [roleCode],
    branding: tenant.branding,
    modules,
    profile_type: profileType,
  };
}

function makeUser(roleCode, { email, displayName, profileType, tenant, memberships }) {
  return {
    id: `user-${roleCode}-1`,
    email,
    display_name: displayName,
    status: "active",
    tenant_id: tenant.tenant_id,
    roles: [roleCode],
    last_login_at: null,
    memberships,
    profile_type: profileType,
  };
}

function calculateSummary(contributions) {
  const totalCount = contributions.length;
  const totalExpected = contributions
    .reduce((sum, item) => sum + Number(item.expected_amount), 0)
    .toFixed(2);
  const totalPaid = contributions
    .reduce((sum, item) => sum + Number(item.paid_amount), 0)
    .toFixed(2);
  const totalBalance = contributions
    .reduce((sum, item) => sum + Number(item.balance), 0)
    .toFixed(2);

  return {
    total_count: totalCount,
    total_expected: totalExpected,
    total_paid: totalPaid,
    total_balance: totalBalance,
  };
}

function buildMemberStatement(data, memberEmail) {
  const profile = data.members.find((item) => item.email === memberEmail) || data.members[0];
  const contributions = data.contributions.filter(
    (item) => item.membership_profile_id === profile.id,
  );
  const summary = {
    profile,
    ...calculateSummary(contributions),
    contribution_count: contributions.length,
  };

  return {
    profile,
    summary,
    contributions,
  };
}

function buildMemberBalance(data, profileId) {
  const profile = data.members.find((item) => item.id === profileId);
  const contributions = data.contributions.filter((item) => item.membership_profile_id === profileId);
  return {
    profile,
    ...calculateSummary(contributions),
    contribution_count: contributions.length,
  };
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeManifest(dir, session) {
  const content = [
    `# ${session.title}`,
    "",
    `- Purpose: ${session.note}`,
    `- Route: \`${session.route}\``,
    `- Capture: \`${session.file}\``,
    "",
  ].join("\n");
  await fs.writeFile(path.join(dir, "SESSION.md"), content, "utf8");
}

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForServer(url) {
  for (let attempt = 0; attempt < 120; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok || response.status < 500) {
        return;
      }
    } catch {}
    await delay(1000);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

function startWebServer() {
  const command = `${npmCommand} run dev -- --host 127.0.0.1 --port ${galleryPort}`;
  const child = spawn(command, {
    cwd: appRoot,
    stdio: "inherit",
    shell: true,
  });
  return child;
}

async function installMockApi(
  page,
  {
    preAuth = false,
    loginMode = "none",
    currentTenant,
    memberships,
    user,
    selectedTenantId,
  },
) {
  if (preAuth) {
    await page.addInitScript(
      ({ tenantId }) => {
        window.localStorage.setItem("access_token", "playwright-gallery-token");
        if (tenantId) {
          window.localStorage.setItem("selected_tenant_id", tenantId);
        }
      },
      { tenantId: selectedTenantId || currentTenant.tenant_id },
    );
  }

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const pathname = url.pathname;
    const method = request.method();
    const activeTenantId = user.tenant_id;
    const data = tenantData[activeTenantId];

    const json = async (body, status = 200) => {
      await route.fulfill({
        status,
        contentType: "application/json",
        body: JSON.stringify(body),
      });
    };

    if (pathname.endsWith("/auth/login") && method === "POST" && loginMode === "interactive") {
      await json({
        access_token: "playwright-gallery-token",
        token_type: "bearer",
        expires_in: 3600,
        tenant_id: currentTenant.tenant_id,
        user_id: user.id,
      });
      return;
    }

    if (pathname.endsWith("/auth/me") && method === "GET") {
      await json(user);
      return;
    }

    if (pathname.endsWith("/auth/switch-tenant") && method === "POST") {
      const payload = request.postDataJSON();
      await json({
        access_token: "playwright-gallery-token",
        token_type: "bearer",
        expires_in: 3600,
        tenant_id: payload.tenant_id,
        user_id: user.id,
        memberships,
      });
      return;
    }

    if (pathname.endsWith("/documents") && method === "GET") {
      await json(data.documents);
      return;
    }

    if (pathname.endsWith("/memberships/me/statement") && method === "GET") {
      await json(buildMemberStatement(data, user.email));
      return;
    }

    if (pathname.endsWith("/memberships/") && method === "GET") {
      await json(data.members);
      return;
    }

    if (/\/memberships\/[^/]+\/balance$/.test(pathname) && method === "GET") {
      const profileId = pathname.split("/").slice(-2)[0];
      await json(buildMemberBalance(data, profileId));
      return;
    }

    if (pathname.endsWith("/contributions/summary") && method === "GET") {
      await json(calculateSummary(data.contributions));
      return;
    }

    if (pathname.endsWith("/contributions/payments") && method === "GET") {
      await json(data.payments);
      return;
    }

    if (pathname.endsWith("/contributions/report/export") && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "text/csv; charset=utf-8",
        body: "contribution_id,membership_profile_id,year\n",
      });
      return;
    }

    if (pathname.endsWith("/contributions/") && method === "GET") {
      await json(data.contributions);
      return;
    }

    if (pathname.endsWith("/policies/categories") && method === "GET") {
      await json({ categories: ["governance", "finance", "sports"] });
      return;
    }

    if (pathname.endsWith("/policies/") && method === "GET") {
      await json(data.policies);
      return;
    }

    if (pathname.endsWith("/announcements/active") && method === "GET") {
      await json(data.announcements);
      return;
    }

    if (pathname.endsWith("/announcements/") && method === "GET") {
      await json(data.announcements);
      return;
    }

    if (pathname.endsWith("/events/public") && method === "GET") {
      await json(data.events);
      return;
    }

    if (pathname.endsWith("/sports/events") && method === "GET") {
      await json(data.sportsEvents);
      return;
    }

    if (pathname.endsWith("/disciplinary/") && method === "GET") {
      await json(data.disciplinaryRecords);
      return;
    }

    if (pathname.includes("/admin/audit/events") && method === "GET") {
      await json(data.auditEvents);
      return;
    }

    if (pathname.endsWith("/notifications/channels") && method === "GET") {
      await json(data.channels);
      return;
    }

    if (pathname.endsWith("/admin/ingestion-jobs/health") && method === "GET") {
      await json(data.ingestionHealth);
      return;
    }

    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: `No gallery mock for ${method} ${pathname}` }),
    });
  });
}

async function waitForText(page, text) {
  await page.waitForFunction(
    (expected) => document.body?.innerText?.includes(expected),
    text,
    { timeout: 30000 },
  );
}

async function captureSession(browser, session) {
  const sessionDir = path.join(outputRoot, session.folder);
  await ensureDir(sessionDir);

  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
  });
  const page = await context.newPage();

  try {
    await session.setup(page);
    if (session.route !== "/login" || session.waitForText !== "Choose organization") {
      await page.goto(`${baseUrl}${session.route}`, { waitUntil: "networkidle" });
    }
    if (session.afterLoad) {
      await session.afterLoad(page);
    }
    if (session.waitForText) {
      await waitForText(page, session.waitForText);
    }
    await page.screenshot({
      path: path.join(sessionDir, session.file),
      fullPage: true,
    });
    await writeManifest(sessionDir, session);
  } finally {
    await context.close();
  }
}

async function run() {
  await ensureDir(outputRoot);
  let webServer;

  if (shouldStartWeb) {
    webServer = startWebServer();
    await waitForServer(`${baseUrl}/login`);
  }

  const browser = await chromium.launch({ headless: true });

  try {
    for (const session of roleSessions) {
      console.log(`Capturing ${session.folder}`);
      await captureSession(browser, session);
    }
  } finally {
    await browser.close();
    if (webServer && !webServer.killed) {
      webServer.kill("SIGTERM");
    }
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
