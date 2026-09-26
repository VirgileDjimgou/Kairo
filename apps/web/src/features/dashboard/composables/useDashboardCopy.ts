import { computed, type ComputedRef } from 'vue'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import type { DashboardRoleFlags } from './useDashboardRoles'

export interface DashboardCopy {
  welcomeBack: string
  setupMode: string
  operational: string
  loadingTitle: string
  loadingBody: string
  firstRunChecklist: string
  complete: string
  nextBestAction: string
  completed: string
  pending: string
  tenantSnapshot: string
  liveUsageSignals: string
  refresh: string
  currentTenant: string
  tenant: string
  role: string
  checklistComplete: string
  lastRefresh: string
  justLoaded: string
  quickActions: string
}

export function useDashboardCopy(roles: DashboardRoleFlags): {
  copy: ComputedRef<DashboardCopy>
  dashboardKicker: ComputedRef<string>
  dashboardLead: ComputedRef<string>
} {
  const localeStore = useLocaleStore()
  const tenantStore = useTenantStore()

  const copy = computed<DashboardCopy>(() => {
    if (localeStore.currentLocale === 'de') {
      return {
        welcomeBack: 'Willkommen zurück',
        setupMode: 'Einrichtungsmodus',
        operational: 'Betriebsbereit',
        loadingTitle: 'Tenant-Startleitfaden wird geladen',
        loadingBody: 'Dokumente, Mitglieder, Ankuendigungen und Veranstaltungen werden geprueft, damit die Checkliste den echten Tenant-Stand widerspiegelt.',
        firstRunChecklist: 'Erststart-Checkliste',
        complete: 'abgeschlossen',
        nextBestAction: 'Beste naechste Aktion',
        completed: 'Abgeschlossen',
        pending: 'Offen',
        tenantSnapshot: 'Tenant-Ueberblick',
        liveUsageSignals: 'Live-Nutzungssignale',
        refresh: 'Aktualisieren',
        currentTenant: 'Aktueller Tenant',
        tenant: 'Tenant',
        role: 'Rolle',
        checklistComplete: 'Checkliste abgeschlossen',
        lastRefresh: 'Letzte Aktualisierung',
        justLoaded: 'Gerade geladen',
        quickActions: 'Schnellaktionen',
      }
    }
    if (localeStore.currentLocale === 'en') {
      return {
        welcomeBack: 'Welcome back',
        setupMode: 'Setup mode',
        operational: 'Operational',
        loadingTitle: 'Loading tenant onboarding guidance',
        loadingBody: 'We are checking documents, members, announcements, and events so the checklist reflects the live tenant state.',
        firstRunChecklist: 'First-run checklist',
        complete: 'complete',
        nextBestAction: 'Next best action',
        completed: 'Completed',
        pending: 'Pending',
        tenantSnapshot: 'Tenant snapshot',
        liveUsageSignals: 'Live usage signals',
        refresh: 'Refresh',
        currentTenant: 'Current tenant',
        tenant: 'Tenant',
        role: 'Role',
        checklistComplete: 'Checklist complete',
        lastRefresh: 'Last refresh',
        justLoaded: 'Just loaded',
        quickActions: 'Quick actions',
      }
    }
    return {
      welcomeBack: 'Bon retour',
      setupMode: 'Mode initialisation',
      operational: 'Opérationnel',
      loadingTitle: 'Chargement du guide de démarrage du tenant',
      loadingBody: "Nous vérifions les documents, membres, annonces et événements pour refléter l'état réel du tenant.",
      firstRunChecklist: 'Checklist de premier démarrage',
      complete: 'terminé',
      nextBestAction: 'Prochaine meilleure action',
      completed: 'Terminé',
      pending: 'En attente',
      tenantSnapshot: 'Aperçu du tenant',
      liveUsageSignals: "Signaux d'usage en direct",
      refresh: 'Actualiser',
      currentTenant: 'Tenant actuel',
      tenant: 'Tenant',
      role: 'Rôle',
      checklistComplete: 'Checklist terminée',
      lastRefresh: 'Dernière actualisation',
      justLoaded: 'À l’instant',
      quickActions: 'Actions rapides',
    }
  })

  const dashboardKicker = computed(() => {
    if (localeStore.currentLocale === 'en') {
      if (roles.isPrincipalAdmin.value) return 'Principal admin control plane'
      if (roles.isMemberOnly.value) return 'Member portal'
      if (roles.isTreasurer.value) return 'Finance workspace'
      if (roles.isSecretaryGeneral.value) return 'Secretary workspace'
      if (roles.isAuditor.value) return 'Finance audit'
      if (roles.isCensor.value) return 'Disciplinary console'
      if (roles.isSportsManager.value) return 'Sports workspace'
      if (roles.isPresidentRole.value || roles.isVicePresidentRole.value) return 'Governance cockpit'
      return 'Tenant overview'
    }
    if (localeStore.currentLocale === 'de') {
      if (roles.isPrincipalAdmin.value) return 'Hauptadmin-Zentrale'
      if (roles.isMemberOnly.value) return 'Mitgliederportal'
      if (roles.isTreasurer.value) return 'Finanzbereich'
      if (roles.isSecretaryGeneral.value) return 'Sekretariatsbereich'
      if (roles.isAuditor.value) return 'Finanzaudit'
      if (roles.isCensor.value) return 'Disziplinarkonsole'
      if (roles.isSportsManager.value) return 'Sportbereich'
      if (roles.isPresidentRole.value || roles.isVicePresidentRole.value) return 'Governance-Cockpit'
      return 'Tenant-Ueberblick'
    }
    if (roles.isPrincipalAdmin.value) return 'Espace administrateur principal'
    if (roles.isMemberOnly.value) return 'Portail membre'
    if (roles.isTreasurer.value) return 'Espace finances'
    if (roles.isSecretaryGeneral.value) return 'Espace secrétariat'
    if (roles.isAuditor.value) return 'Audit finances'
    if (roles.isCensor.value) return 'Console disciplinaire'
    if (roles.isSportsManager.value) return 'Espace sport'
    if (roles.isPresidentRole.value || roles.isVicePresidentRole.value) return 'Cockpit de gouvernance'
    return 'Aperçu du tenant'
  })

  const dashboardLead = computed(() => {
    const tenantName = tenantStore.currentTenantName
    if (localeStore.currentLocale === 'fr') {
      if (roles.isPrincipalAdmin.value) {
        return `Votre tenant actuel est ${tenantName}. Utilisez cet espace pour l'administration globale sans compromettre l'isolation.`
      }
      if (roles.isMemberOnly.value) {
        return `Votre tenant actuel est ${tenantName}. Consultez votre profil, vos cotisations et les informations associatives autorisées.`
      }
      if (roles.isTreasurer.value) {
        return `Votre tenant actuel est ${tenantName}. Suivez les finances, les soldes membres et les paiements depuis l'espace dédié.`
      }
      if (roles.isSecretaryGeneral.value) {
        return `Votre tenant actuel est ${tenantName}. Gardez les documents, règlements et annonces bien organisés depuis l'espace secrétariat.`
      }
      if (roles.isAuditor.value) {
        return `Votre tenant actuel est ${tenantName}. Contrôlez les totaux financiers et les enregistrements prêts pour l'audit.`
      }
      if (roles.isCensor.value) {
        return `Votre tenant actuel est ${tenantName}. Travaillez dans la console disciplinaire avec les frontières de confidentialité préservées.`
      }
      if (roles.isSportsManager.value) {
        return `Votre tenant actuel est ${tenantName}. Gérez les activités sportives depuis un espace ciblé et sans surcharge.`
      }
      if (roles.isPresidentRole.value || roles.isVicePresidentRole.value) {
        return `Votre tenant actuel est ${tenantName}. Utilisez le cockpit de gouvernance pour une supervision claire de l'association.`
      }
      return `Votre tenant actuel est ${tenantName}. Le tableau de bord met en avant les prochaines actions les plus utiles.`
    }
    if (localeStore.currentLocale === 'de') {
      if (roles.isPrincipalAdmin.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Nutzen Sie diese Zentrale fuer die tenant-weite Administration, ohne die Isolation zu gefaehrden.`
      }
      if (roles.isMemberOnly.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Sehen Sie Ihr Profil, Ihre Beitraege und die fuer Sie freigegebenen Vereinsinformationen ein.`
      }
      if (roles.isTreasurer.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Verfolgen Sie Finanzen, Mitgliedersalden und Zahlungen im dafuer vorgesehenen Bereich.`
      }
      if (roles.isSecretaryGeneral.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Halten Sie Dokumente, Regeln und Ankuendigungen im Sekretariatsbereich ordentlich.`
      }
      if (roles.isAuditor.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Kontrollieren Sie Finanzsummen und auditbereite Aufzeichnungen in sicherem Lesemodus.`
      }
      if (roles.isCensor.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Arbeiten Sie in der Disziplinarkonsole bei gewahrter Vertraulichkeit.`
      }
      if (roles.isSportsManager.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Verwalten Sie Sportaktivitaeten in einem fokussierten und klaren Bereich.`
      }
      if (roles.isPresidentRole.value || roles.isVicePresidentRole.value) {
        return `Ihr aktueller Tenant ist ${tenantName}. Nutzen Sie das Governance-Cockpit fuer eine klare Aufsicht ueber den Verein.`
      }
      return `Ihr aktueller Tenant ist ${tenantName}. Das Dashboard zeigt Ihnen die naechsten sinnvollen Schritte.`
    }
    if (roles.isPrincipalAdmin.value) {
      return `Your current tenant is ${tenantName}. Use the control plane for tenant-wide administration without breaking isolation.`
    }
    if (roles.isMemberOnly.value) {
      return `Your current tenant is ${tenantName}. Review your personal profile, contribution statement, and read-only association updates.`
    }
    if (roles.isTreasurer.value) {
      return `Your current tenant is ${tenantName}. Review finance tasks, member balances, and payment activity from the dedicated workspace.`
    }
    if (roles.isSecretaryGeneral.value) {
      return `Your current tenant is ${tenantName}. Keep documents, policies, and announcements tidy from the secretary workspace.`
    }
    if (roles.isAuditor.value) {
      return `Your current tenant is ${tenantName}. Inspect finance totals and audit-ready records without mutation controls.`
    }
    if (roles.isCensor.value) {
      return `Your current tenant is ${tenantName}. Work inside the disciplinary console with privacy boundaries preserved.`
    }
    if (roles.isSportsManager.value) {
      return `Your current tenant is ${tenantName}. Manage sports events in a focused workspace with no extra noise.`
    }
    if (roles.isPresidentRole.value || roles.isVicePresidentRole.value) {
      return `Your current tenant is ${tenantName}. Use the governance cockpit for focused oversight across the association.`
    }
    return `Your current tenant is ${tenantName}. The dashboard highlights the next steps that matter most.`
  })

  return { copy, dashboardKicker, dashboardLead }
}
