import type { SupportedLocale } from './messages'

type DemoMessageDictionary = Record<SupportedLocale, Record<string, string>>

/**
 * Messages for the public portfolio demo experience (`/demo`, demo banner and
 * guided tour). Kept in a dedicated module so the main catalogue stays focused.
 */
export const demoMessages: DemoMessageDictionary = {
  fr: {
    'demo.pageTitle': 'Découvrir Kairo',
    'demo.brandSubtitle': 'Démonstration portfolio',
    'demo.heroKicker': 'Démonstration',
    'demo.heroTitle': 'Explorez Kairo avec un rôle, en un clic.',
    'demo.heroCopy':
      "Choisissez un rôle ci-dessous pour ouvrir immédiatement un espace de démonstration. Aucune inscription n'est requise.",
    'demo.explore': 'Explorer ce rôle',
    'demo.chooseRoleTitle': 'Choisissez un rôle',
    'demo.chooseRoleSubtitle':
      'Chaque rôle ouvre un espace et des permissions différents.',
    'demo.advancedRoles': 'Rôles avancés',
    'demo.advancedHint':
      'Rôles sensibles, adaptés à une démonstration accompagnée.',
    'demo.signInInstead': "J'ai un compte — se connecter",
    'demo.loading': 'Ouverture de la démonstration…',
    'demo.loginFailed':
      "Impossible d'ouvrir cette démonstration pour le moment. Réessayez ou choisissez un autre rôle.",
    'demo.disabled':
      "La démonstration portfolio n'est pas activée sur cette instance.",
    'demo.bannerText': 'Environnement de démonstration portfolio',
    'demo.bannerData':
      "Données fictives — rien de ce que vous voyez ici n'est réel.",
    'demo.switchRole': 'Changer de rôle',
    'demo.exit': 'Quitter la démo',
    'demo.tourTitle': 'Parcours guidé',
    'demo.tourSubtitle': 'Trois actions suggérées pour ce rôle.',
    'demo.tourGo': 'Ouvrir',
    'demo.tourRestart': 'Recommencer la démo',
    'demo.tourStep': 'Étape {n}',
    'demo.role.member': 'Membre',
    'demo.role.president': 'Président',
    'demo.role.treasurer': 'Trésorier',
    'demo.role.secretary_general': 'Secrétaire général',
    'demo.role.auditor': 'Commissaire aux comptes',
    'demo.role.censor': 'Censeur',
    'demo.role.sports_manager': 'Responsable sportif',
    'demo.role.vice_president': 'Vice-président',
    'demo.roleDesc.member':
      'Espace personnel, cotisations, événements et documents.',
    'demo.roleDesc.president': 'Vision globale, gouvernance et indicateurs.',
    'demo.roleDesc.treasurer':
      'Recettes, budget et validation des encaissements.',
    'demo.roleDesc.secretary_general':
      'Membres, documents, politiques et communications.',
    'demo.roleDesc.auditor': "Finance en lecture seule et piste d'audit.",
    'demo.roleDesc.censor': 'Confidentialité et suivi disciplinaire.',
    'demo.roleDesc.sports_manager':
      'Événements, équipes et logistique sportive.',
    'demo.roleDesc.vice_president': 'Gouvernance et appui à la présidence.',
  },
  en: {
    'demo.pageTitle': 'Discover Kairo',
    'demo.brandSubtitle': 'Portfolio demo',
    'demo.heroKicker': 'Demo',
    'demo.heroTitle': 'Explore Kairo with a role, in one click.',
    'demo.heroCopy':
      'Pick a role below to open a demo workspace instantly. No sign-up required.',
    'demo.explore': 'Explore this role',
    'demo.chooseRoleTitle': 'Choose a role',
    'demo.chooseRoleSubtitle':
      'Each role opens a different workspace and set of permissions.',
    'demo.advancedRoles': 'Advanced roles',
    'demo.advancedHint': 'Sensitive roles, best suited to a guided walkthrough.',
    'demo.signInInstead': 'I have an account — sign in',
    'demo.loading': 'Opening the demo…',
    'demo.loginFailed':
      'This demo cannot be opened right now. Try again or pick another role.',
    'demo.disabled': 'The portfolio demo is not enabled on this instance.',
    'demo.bannerText': 'Portfolio demo environment',
    'demo.bannerData': 'Fictional data — nothing you see here is real.',
    'demo.switchRole': 'Switch role',
    'demo.exit': 'Exit demo',
    'demo.tourTitle': 'Guided tour',
    'demo.tourSubtitle': 'Three suggested actions for this role.',
    'demo.tourGo': 'Open',
    'demo.tourRestart': 'Restart the demo',
    'demo.tourStep': 'Step {n}',
    'demo.role.member': 'Member',
    'demo.role.president': 'President',
    'demo.role.treasurer': 'Treasurer',
    'demo.role.secretary_general': 'Secretary General',
    'demo.role.auditor': 'Auditor',
    'demo.role.censor': 'Censor',
    'demo.role.sports_manager': 'Sports Manager',
    'demo.role.vice_president': 'Vice President',
    'demo.roleDesc.member':
      'Personal space, dues, events and documents.',
    'demo.roleDesc.president': 'Overall vision, governance and indicators.',
    'demo.roleDesc.treasurer': 'Income, budget and payment validation.',
    'demo.roleDesc.secretary_general':
      'Members, documents, policies and communications.',
    'demo.roleDesc.auditor': 'Read-only finance and audit trail.',
    'demo.roleDesc.censor': 'Confidentiality and disciplinary follow-up.',
    'demo.roleDesc.sports_manager': 'Events, teams and sports logistics.',
    'demo.roleDesc.vice_president': 'Governance and support to the presidency.',
  },
  de: {
    'demo.pageTitle': 'Kairo entdecken',
    'demo.brandSubtitle': 'Portfolio-Demo',
    'demo.heroKicker': 'Demo',
    'demo.heroTitle': 'Kairo mit einer Rolle erkunden — mit einem Klick.',
    'demo.heroCopy':
      'Wählen Sie unten eine Rolle, um sofort einen Demo-Bereich zu öffnen. Keine Registrierung nötig.',
    'demo.explore': 'Diese Rolle erkunden',
    'demo.chooseRoleTitle': 'Rolle wählen',
    'demo.chooseRoleSubtitle':
      'Jede Rolle öffnet einen anderen Bereich mit anderen Rechten.',
    'demo.advancedRoles': 'Erweiterte Rollen',
    'demo.advancedHint':
      'Sensible Rollen, ideal für eine begleitete Vorführung.',
    'demo.signInInstead': 'Ich habe ein Konto — anmelden',
    'demo.loading': 'Demo wird geöffnet…',
    'demo.loginFailed':
      'Diese Demo kann derzeit nicht geöffnet werden. Bitte erneut versuchen oder eine andere Rolle wählen.',
    'demo.disabled': 'Die Portfolio-Demo ist auf dieser Instanz nicht aktiviert.',
    'demo.bannerText': 'Portfolio-Demo-Umgebung',
    'demo.bannerData': 'Fiktive Daten — nichts davon ist real.',
    'demo.switchRole': 'Rolle wechseln',
    'demo.exit': 'Demo verlassen',
    'demo.tourTitle': 'Geführte Tour',
    'demo.tourSubtitle': 'Drei vorgeschlagene Aktionen für diese Rolle.',
    'demo.tourGo': 'Öffnen',
    'demo.tourRestart': 'Demo neu starten',
    'demo.tourStep': 'Schritt {n}',
    'demo.role.member': 'Mitglied',
    'demo.role.president': 'Präsident',
    'demo.role.treasurer': 'Kassierer',
    'demo.role.secretary_general': 'Generalsekretär',
    'demo.role.auditor': 'Rechnungsprüfer',
    'demo.role.censor': 'Zensor',
    'demo.role.sports_manager': 'Sportwart',
    'demo.role.vice_president': 'Vizepräsident',
    'demo.roleDesc.member':
      'Persönlicher Bereich, Beiträge, Termine und Dokumente.',
    'demo.roleDesc.president': 'Überblick, Governance und Kennzahlen.',
    'demo.roleDesc.treasurer': 'Einnahmen, Budget und Zahlungsprüfung.',
    'demo.roleDesc.secretary_general':
      'Mitglieder, Dokumente, Richtlinien und Kommunikation.',
    'demo.roleDesc.auditor': 'Finanzen nur lesend und Prüfpfad.',
    'demo.roleDesc.censor': 'Vertraulichkeit und Disziplinarverfolgung.',
    'demo.roleDesc.sports_manager': 'Termine, Teams und Sportlogistik.',
    'demo.roleDesc.vice_president': 'Governance und Unterstützung der Präsidentschaft.',
  },
}
