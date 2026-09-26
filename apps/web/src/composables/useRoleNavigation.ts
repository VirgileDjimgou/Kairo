import { computed } from "vue";
import { useAuthStore } from "@/stores/auth.store";
import { useTenantStore } from "@/stores/tenant.store";
import { useLocaleStore } from "@/stores/locale.store";
import {
  CAP_BACKUP_CREATE,
  CAP_BACKUP_RESTORE_REQUEST,
  CAP_DISCIPLINARY_OVERSIGHT_READ,
  CAP_DISCIPLINARY_WRITE,
  CAP_DOCUMENTS_WRITE,
  CAP_EVENTS_SPORTS_WRITE,
  CAP_FINANCE_AUDIT,
  CAP_FINANCE_EXPENSES_WRITE,
  CAP_FINANCE_WRITE,
  CAP_GOVERNANCE_COCKPIT_READ,
  CAP_MEMBERSHIP_TENANT_READ,
  CAP_TENANT_ADMINISTRATION,
} from "@/config/capabilities";

export type NavItem = {
  label: string;
  to: string;
  icon: string;
};

export type NavSection = {
  label: string;
  items: NavItem[];
};

export function useRoleNavigation() {
  const authStore = useAuthStore();
  const tenantStore = useTenantStore();
  const localeStore = useLocaleStore();
  const roles = computed(() => authStore.user?.roles ?? []);
  const capabilities = computed(() => authStore.capabilities);
  const can = (capability: string) => capabilities.value.includes(capability);

  const isMember = computed(() => !can(CAP_MEMBERSHIP_TENANT_READ));
  const isPrincipalAdmin = computed(() => roles.value.includes("principal_admin"));
  const isAdmin = computed(() => roles.value.includes("admin"));
  const isTreasurer = computed(() => can(CAP_FINANCE_EXPENSES_WRITE));
  const isSecretaryGeneral = computed(
    () => can(CAP_DOCUMENTS_WRITE) && !can(CAP_TENANT_ADMINISTRATION),
  );
  const isAuditor = computed(
    () => can(CAP_FINANCE_AUDIT) && !can(CAP_BACKUP_CREATE),
  );
  const isPresident = computed(
    () => can(CAP_BACKUP_RESTORE_REQUEST) && !can(CAP_DOCUMENTS_WRITE),
  );
  const isVicePresident = computed(
    () =>
      capabilities.value.includes("identity:access_recovery") &&
      !can(CAP_BACKUP_RESTORE_REQUEST),
  );
  const isCensor = computed(
    () => can(CAP_DISCIPLINARY_WRITE) && !can(CAP_TENANT_ADMINISTRATION),
  );
  const isSportsManager = computed(
    () => can(CAP_EVENTS_SPORTS_WRITE) && !can(CAP_TENANT_ADMINISTRATION),
  );

  const showFinanceWorkspace = computed(
    () =>
      can(CAP_FINANCE_WRITE) &&
      tenantStore.isModuleEnabled("membership") &&
      tenantStore.isModuleEnabled("contributions"),
  );

  const showFinanceAuditWorkspace = computed(
    () =>
      can(CAP_FINANCE_AUDIT) &&
      tenantStore.isModuleEnabled("membership") &&
      tenantStore.isModuleEnabled("contributions"),
  );

  const showSecretaryWorkspace = computed(() => can(CAP_DOCUMENTS_WRITE));

  const showGovernanceCockpit = computed(() => can(CAP_GOVERNANCE_COCKPIT_READ));

  const showCensorWorkspace = computed(
    () =>
      can(CAP_DISCIPLINARY_OVERSIGHT_READ) &&
      tenantStore.isModuleEnabled("disciplinary"),
  );

  const showSportsWorkspace = computed(
    () =>
      (can(CAP_EVENTS_SPORTS_WRITE) || can(CAP_TENANT_ADMINISTRATION)) &&
      tenantStore.isModuleEnabled("events"),
  );

  const appNavigation = computed<NavSection[]>(() => {
    const sections: NavSection[] = [
      {
        label: localeStore.t("layout.personal"),
        items: [
          {
            label: localeStore.t("nav.dashboard"),
            to: "/dashboard",
            icon: "bi-grid-1x2",
          },
          {
            label: localeStore.t("nav.myProfile"),
            to: "/members/profile",
            icon: "bi-person-badge",
          },
          {
            label: localeStore.t("nav.accountSecurity"),
            to: "/account/security",
            icon: "bi-shield-check",
          },
          {
            label: localeStore.t("nav.chat"),
            to: "/chat",
            icon: "bi-chat-dots",
          },
        ].filter(
          (item) => item.to !== "/chat" || tenantStore.isModuleEnabled("chat"),
        ),
      },
    ];

    if (isMember.value) {
      sections.push({
        label: localeStore.t("layout.read"),
        items: [
          {
            label: localeStore.t("nav.events"),
            to: "/events",
            icon: "bi-calendar-event",
          },
          {
            label: localeStore.t("nav.announcements"),
            to: "/announcements",
            icon: "bi-megaphone",
          },
          {
            label: localeStore.t("nav.policies"),
            to: "/policies",
            icon: "bi-journal-text",
          },
        ].filter((item) => tenantStore.isModuleEnabled(item.to.slice(1))),
      });
      return sections;
    }

    const workspaceItems: NavItem[] = [];

    if (showSecretaryWorkspace.value) {
      workspaceItems.push({
        label: localeStore.t("nav.secretaryWorkspace"),
        to: "/secretary",
        icon: "bi-journal-richtext",
      });
    }
    const isElectedOfficeHolder =
      can(CAP_MEMBERSHIP_TENANT_READ) && !can(CAP_TENANT_ADMINISTRATION);
    if (isElectedOfficeHolder) {
      workspaceItems.push({
        label: localeStore.t("nav.members"),
        to: "/members/manage",
        icon: "bi-people",
      });
      workspaceItems.push({
        label: localeStore.t("nav.operationJournal"),
        to: "/operation-journal",
        icon: "bi-journal-check",
      });
    }
    if (can(CAP_BACKUP_RESTORE_REQUEST)) {
      workspaceItems.push({
        label: localeStore.currentLocale === 'de' ? 'Sicherung & Wiederherstellung' : localeStore.currentLocale === 'en' ? 'Backup & recovery' : 'Sauvegarde et récupération',
        to: "/recovery",
        icon: "bi-safe2",
      });
    }
    if (!isMember.value) {
      workspaceItems.push({
        label: localeStore.currentLocale === 'de' ? 'Zahlungen melden' : localeStore.currentLocale === 'en' ? 'Report receipts' : 'Déclarer un encaissement',
        to: "/receipts",
        icon: "bi-cash-coin",
      });
    }
    if (showFinanceWorkspace.value) {
      workspaceItems.push({
        label: localeStore.t("nav.financeWorkspace"),
        to: "/finance",
        icon: "bi-cash-coin",
      });
    }
    if (showFinanceAuditWorkspace.value) {
      workspaceItems.push({
        label: localeStore.t("nav.financeAudit"),
        to: "/finance-audit",
        icon: "bi-clipboard-data",
      });
    }
    if (showGovernanceCockpit.value) {
      workspaceItems.push({
        label: localeStore.t("nav.governanceCockpit"),
        to: "/governance",
        icon: "bi-diagram-3",
      });
    }
    if (showCensorWorkspace.value) {
      workspaceItems.push({
        label: localeStore.t("nav.disciplinaryConsole"),
        to: "/censor",
        icon: "bi-shield-lock",
      });
    }
    if (showSportsWorkspace.value) {
      workspaceItems.push({
        label: localeStore.t("nav.sportsWorkspace"),
        to: "/sports",
        icon: "bi-trophy",
      });
    }
    if (isPrincipalAdmin.value || isAdmin.value) {
      workspaceItems.push({
        label: isPrincipalAdmin.value
          ? localeStore.t("nav.principalAdminPlane")
          : localeStore.t("nav.adminPlane"),
        to: "/admin",
        icon: "bi-shield-lock",
      });
    }

    if (workspaceItems.length) {
      sections.push({
        label: localeStore.t("layout.workspaces"),
        items: workspaceItems,
      });
    }

    const communityItems: NavItem[] = [
      {
        label: localeStore.t("nav.events"),
        to: "/events",
        icon: "bi-calendar-event",
      },
      {
        label: localeStore.t("nav.announcements"),
        to: "/announcements",
        icon: "bi-megaphone",
      },
      {
        label: localeStore.t("nav.policies"),
        to: "/policies",
        icon: "bi-journal-text",
      },
    ].filter((item) => tenantStore.isModuleEnabled(item.to.slice(1)));

    if (communityItems.length) {
      sections.push({
        label: localeStore.t("layout.community"),
        items: communityItems,
      });
    }

    return sections;
  });

  const adminNavigation = computed<NavSection[]>(() => {
    const sections: NavSection[] = [
      {
        label: localeStore.t("layout.overview"),
        items: [
          {
            label: localeStore.t("nav.overview"),
            to: "/admin",
            icon: "bi-speedometer2",
          },
          {
            label: localeStore.t("nav.onboardingWizard"),
            to: "/admin/onboarding",
            icon: "bi-stars",
          },
          {
            label: localeStore.t("nav.healthCenter"),
            to: "/admin/health",
            icon: "bi-heart-pulse",
          },
          {
            label: localeStore.t("nav.tenantOperations"),
            to: "/admin/tenants",
            icon: "bi-diagram-3",
          },
        ],
      },
    ];

    const operations: NavItem[] = [];
    if (tenantStore.isModuleEnabled("membership")) {
      operations.push({
        label: localeStore.t("nav.members"),
        to: "/admin/members",
        icon: "bi-people",
      });
    }
    if (tenantStore.isModuleEnabled("contributions")) {
      operations.push({
        label: localeStore.t("nav.contributions"),
        to: "/admin/contributions",
        icon: "bi-cash-stack",
      });
    }
    if (tenantStore.isModuleEnabled("policies")) {
      operations.push({
        label: localeStore.t("nav.policies"),
        to: "/admin/policies",
        icon: "bi-journal-text",
      });
    }
    if (tenantStore.isModuleEnabled("disciplinary")) {
      operations.push({
        label: localeStore.t("nav.disciplinary"),
        to: "/admin/disciplinary",
        icon: "bi-shield-lock",
      });
    }
    operations.push({
      label: localeStore.t("nav.access"),
      to: "/admin/access",
      icon: "bi-person-plus",
    });
    operations.push({
      label: localeStore.t("nav.documents"),
      to: "/admin/documents",
      icon: "bi-file-earmark-text",
    });

    if (operations.length) {
      sections.push({
        label: localeStore.t("layout.operations"),
        items: operations,
      });
    }

    const governance: NavItem[] = [
      {
        label: localeStore.t("nav.auditTrail"),
        to: "/admin/audit",
        icon: "bi-shield-check",
      },
    ];
    if (tenantStore.isModuleEnabled("chat")) {
      governance.push({
        label: localeStore.t("nav.chatAudit"),
        to: "/admin/chat-queries",
        icon: "bi-journal-text",
      });
    }
    if (tenantStore.isModuleEnabled("events")) {
      governance.push({
        label: localeStore.t("nav.events"),
        to: "/admin/events",
        icon: "bi-calendar-event",
      });
    }
    if (tenantStore.isModuleEnabled("announcements")) {
      governance.push({
        label: localeStore.t("nav.announcements"),
        to: "/admin/announcements",
        icon: "bi-megaphone",
      });
    }
    if (tenantStore.isModuleEnabled("notifications")) {
      governance.push({
        label: localeStore.t("nav.channels"),
        to: "/admin/notifications",
        icon: "bi-broadcast-pin",
      });
    }

    sections.push({
      label: localeStore.t("layout.governance"),
      items: governance,
    });
    sections.push({
      label: localeStore.t("layout.settings"),
      items: [
        {
          label: localeStore.t("nav.settings"),
          to: "/admin/settings",
          icon: "bi-gear",
        },
      ],
    });

    return sections;
  });

  const appHomeLabel = computed(() => {
    if (isMember.value) return localeStore.t("home.memberPortal");
    if (isSecretaryGeneral.value)
      return localeStore.t("home.secretaryWorkspace");
    if (isTreasurer.value) return localeStore.t("home.financeWorkspace");
    if (isAuditor.value) return localeStore.t("home.financeAudit");
    if (isCensor.value) return localeStore.t("home.disciplinaryConsole");
    if (isSportsManager.value) return localeStore.t("home.sportsWorkspace");
    if (showGovernanceCockpit.value)
      return localeStore.t("home.governanceCockpit");
    return isPrincipalAdmin.value
      ? localeStore.t("home.principalAdminPlane")
      : localeStore.t("home.organizationPortal");
  });

  const personalRouteIds = new Set([
    "/members/profile",
    "/account/security",
    "/chat",
  ]);

  const moduleNavigation = computed<NavItem[]>(() =>
    appNavigation.value
      .flatMap((section) => section.items)
      .filter((item) => !personalRouteIds.has(item.to)),
  );

  const adminModuleNavigation = computed<NavItem[]>(() =>
    adminNavigation.value.flatMap((section) => section.items),
  );

  const adminConsoleLabel = computed(() =>
    isPrincipalAdmin.value
      ? localeStore.t("layout.principalAdminConsole")
      : localeStore.t("layout.adminConsole"),
  );

  // The /more destination is a real navigation catalog grouped by domain.
  // It never forwards to a workspace; every entry lists only destinations the
  // role is already allowed to open.
  const moreAccountRoutes = new Set(["/members/profile", "/account/security"]);
  const moreCommunityRoutes = new Set(["/events", "/announcements", "/chat"]);
  const moreGovernancePrefixes = [
    "/policies",
    "/censor",
    "/governance",
    "/operation-journal",
    "/recovery",
    "/admin",
  ];

  const moreNavigation = computed<NavSection[]>(() => {
    const sourceItems = [
      ...appNavigation.value.flatMap((section) => section.items),
      ...(isAdmin.value || isPrincipalAdmin.value
        ? adminNavigation.value.flatMap((section) => section.items)
        : []),
    ];
    const seen = new Set<string>();
    const buckets = {
      management: [] as NavItem[],
      governance: [] as NavItem[],
      community: [] as NavItem[],
      account: [] as NavItem[],
    };
    for (const item of sourceItems) {
      if (seen.has(item.to) || item.to === "/dashboard") continue;
      seen.add(item.to);
      if (moreAccountRoutes.has(item.to)) {
        buckets.account.push(item);
      } else if (moreCommunityRoutes.has(item.to)) {
        buckets.community.push(item);
      } else if (
        moreGovernancePrefixes.some(
          (prefix) => item.to === prefix || item.to.startsWith(`${prefix}/`),
        )
      ) {
        buckets.governance.push(item);
      } else {
        buckets.management.push(item);
      }
    }
    const sections: NavSection[] = [];
    const push = (key: string, items: NavItem[]) => {
      if (items.length) sections.push({ label: localeStore.t(key), items });
    };
    push("more.management", buckets.management);
    push("more.governance", buckets.governance);
    push("more.community", buckets.community);
    push("more.account", buckets.account);
    return sections;
  });

  return {
    roles,
    isMember,
    isPrincipalAdmin,
    showFinanceWorkspace,
    showFinanceAuditWorkspace,
    showSecretaryWorkspace,
    showGovernanceCockpit,
    showCensorWorkspace,
    showSportsWorkspace,
    appNavigation,
    adminNavigation,
    moduleNavigation,
    adminModuleNavigation,
    moreNavigation,
    appHomeLabel,
    adminConsoleLabel,
  };
}
