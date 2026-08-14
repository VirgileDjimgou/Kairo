import 'package:flutter/widgets.dart';

enum KairoLocale {
  fr(Locale('fr')),
  en(Locale('en')),
  de(Locale('de'));

  const KairoLocale(this.locale);

  final Locale locale;

  String get displayName => switch (this) {
    KairoLocale.fr => 'Français',
    KairoLocale.en => 'English',
    KairoLocale.de => 'Deutsch',
  };

  static KairoLocale fromLocale(Locale locale) => switch (locale.languageCode) {
    'en' => KairoLocale.en,
    'de' => KairoLocale.de,
    _ => KairoLocale.fr,
  };
}

enum KairoCopyKey {
  appName,
  foundationLabel,
  foundationTitle,
  foundationBody,
  parityTitle,
  parityBody,
  apiConfigured,
  apiAwaitingConfiguration,
  dashboard,
  members,
  finance,
  notices,
  profile,
  developmentOnly,
  responsiveReady,
  offlineFuture,
  signIn,
  signOut,
  identifier,
  password,
  showPassword,
  hidePassword,
  signInHelp,
  mfaCode,
  continueAction,
  authenticationFailed,
  sessionRestored,
  passwordUpdateTitle,
  passwordUpdateBody,
  newPassword,
  confirmPassword,
  savePassword,
  passwordsDoNotMatch,
  passwordRules,
  tenantSelectionTitle,
  tenantSelectionBody,
  accountSecurity,
  activeSessions,
  revokeOtherSessions,
  mfa,
  mfaEnabled,
  mfaDisabled,
  enableMfa,
  verifyMfa,
  securityCode,
  apiUnavailable,
  changePassword,
  currentPassword,
  passwordUpdated,
  forgotPassword,
  passwordResetRequested,
  securityCenter,
  refresh,
  revoke,
  revokeAllSessions,
  currentSession,
  noOtherSessions,
  mfaSetupInstructions,
  manualMfaKey,
  cancel,
  disableMfa,
  unknownDevice,
}

class KairoLocalizations {
  const KairoLocalizations(this.locale);

  final KairoLocale locale;

  static const LocalizationsDelegate<KairoLocalizations> delegate =
      _KairoLocalizationsDelegate();

  String text(KairoCopyKey key) => _translations[locale]![key]!;

  static const Map<KairoLocale, Map<KairoCopyKey, String>>
  _translations = <KairoLocale, Map<KairoCopyKey, String>>{
    KairoLocale.fr: <KairoCopyKey, String>{
      KairoCopyKey.appName: 'Kairo',
      KairoCopyKey.foundationLabel: 'CLIENT FLUTTER',
      KairoCopyKey.foundationTitle: 'Fondation mobile et web',
      KairoCopyKey.foundationBody:
          'Le client Flutter est prêt à reproduire progressivement les parcours de la PWA, sans modifier la plateforme actuelle.',
      KairoCopyKey.parityTitle: 'Parité pilotée par preuves',
      KairoCopyKey.parityBody:
          'Chaque fonctionnalité sera validée sur Android et sur le Web, y compris les interfaces mobiles.',
      KairoCopyKey.apiConfigured: 'API configurée',
      KairoCopyKey.apiAwaitingConfiguration:
          'API à configurer pour cet environnement',
      KairoCopyKey.dashboard: 'Accueil',
      KairoCopyKey.members: 'Membres',
      KairoCopyKey.finance: 'Finances',
      KairoCopyKey.notices: 'Alertes',
      KairoCopyKey.profile: 'Profil',
      KairoCopyKey.developmentOnly: 'Fondation F0',
      KairoCopyKey.responsiveReady: 'Navigation responsive',
      KairoCopyKey.offlineFuture: 'Mode hors ligne prévu',
      KairoCopyKey.signIn: 'Se connecter',
      KairoCopyKey.signOut: 'Se déconnecter',
      KairoCopyKey.identifier: 'E-mail, téléphone ou identifiant',
      KairoCopyKey.password: 'Mot de passe',
      KairoCopyKey.showPassword: 'Afficher le mot de passe',
      KairoCopyKey.hidePassword: 'Masquer le mot de passe',
      KairoCopyKey.signInHelp: 'Utilisez vos identifiants personnels Kairo.',
      KairoCopyKey.mfaCode: 'Code de vérification à 6 chiffres',
      KairoCopyKey.continueAction: 'Continuer',
      KairoCopyKey.authenticationFailed:
          'Connexion impossible. Vérifiez vos informations.',
      KairoCopyKey.sessionRestored: 'Session sécurisée',
      KairoCopyKey.passwordUpdateTitle: 'Choisissez un nouveau mot de passe',
      KairoCopyKey.passwordUpdateBody:
          'Votre mot de passe provisoire doit être remplacé avant de continuer.',
      KairoCopyKey.newPassword: 'Nouveau mot de passe',
      KairoCopyKey.confirmPassword: 'Confirmer le mot de passe',
      KairoCopyKey.savePassword: 'Enregistrer le mot de passe',
      KairoCopyKey.passwordsDoNotMatch: 'Les mots de passe sont différents.',
      KairoCopyKey.passwordRules: 'Au moins 8 caractères.',
      KairoCopyKey.tenantSelectionTitle: 'Choisir une association',
      KairoCopyKey.tenantSelectionBody:
          'Sélectionnez l’espace auquel vous souhaitez accéder.',
      KairoCopyKey.accountSecurity: 'Sécurité du compte',
      KairoCopyKey.activeSessions: 'Sessions actives',
      KairoCopyKey.revokeOtherSessions: 'Fermer les autres sessions',
      KairoCopyKey.mfa: 'Authentification à deux facteurs',
      KairoCopyKey.mfaEnabled: 'Activée',
      KairoCopyKey.mfaDisabled: 'Non activée',
      KairoCopyKey.enableMfa: 'Configurer MFA',
      KairoCopyKey.verifyMfa: 'Vérifier le code',
      KairoCopyKey.securityCode: 'Code de sécurité',
      KairoCopyKey.apiUnavailable:
          'Le service est temporairement indisponible.',
      KairoCopyKey.changePassword: 'Modifier le mot de passe',
      KairoCopyKey.currentPassword: 'Mot de passe actuel',
      KairoCopyKey.passwordUpdated:
          'Mot de passe mis à jour. Les autres sessions ont été fermées.',
      KairoCopyKey.forgotPassword: 'Mot de passe oublié ?',
      KairoCopyKey.passwordResetRequested:
          'La demande a été transmise de façon sécurisée.',
      KairoCopyKey.securityCenter: 'Centre de sécurité',
      KairoCopyKey.refresh: 'Actualiser',
      KairoCopyKey.revoke: 'Révoquer',
      KairoCopyKey.revokeAllSessions: 'Fermer toutes les sessions',
      KairoCopyKey.currentSession: 'Session actuelle',
      KairoCopyKey.noOtherSessions: 'Aucune autre session active.',
      KairoCopyKey.mfaSetupInstructions:
          'Ajoutez la clé dans une application d’authentification puis saisissez son code.',
      KairoCopyKey.manualMfaKey: 'Clé manuelle',
      KairoCopyKey.cancel: 'Annuler',
      KairoCopyKey.disableMfa: 'Désactiver MFA',
      KairoCopyKey.unknownDevice: 'Appareil non identifié',
    },
    KairoLocale.en: <KairoCopyKey, String>{
      KairoCopyKey.appName: 'Kairo',
      KairoCopyKey.foundationLabel: 'FLUTTER CLIENT',
      KairoCopyKey.foundationTitle: 'Mobile and web foundation',
      KairoCopyKey.foundationBody:
          'The Flutter client is ready to progressively reproduce PWA journeys without changing the current platform.',
      KairoCopyKey.parityTitle: 'Evidence-led parity',
      KairoCopyKey.parityBody:
          'Every feature will be validated on Android and on the web, including mobile interfaces.',
      KairoCopyKey.apiConfigured: 'API configured',
      KairoCopyKey.apiAwaitingConfiguration:
          'API must be configured for this environment',
      KairoCopyKey.dashboard: 'Home',
      KairoCopyKey.members: 'Members',
      KairoCopyKey.finance: 'Finance',
      KairoCopyKey.notices: 'Alerts',
      KairoCopyKey.profile: 'Profile',
      KairoCopyKey.developmentOnly: 'F0 foundation',
      KairoCopyKey.responsiveReady: 'Responsive navigation',
      KairoCopyKey.offlineFuture: 'Offline mode planned',
      KairoCopyKey.signIn: 'Sign in',
      KairoCopyKey.signOut: 'Sign out',
      KairoCopyKey.identifier: 'Email, phone, or username',
      KairoCopyKey.password: 'Password',
      KairoCopyKey.showPassword: 'Show password',
      KairoCopyKey.hidePassword: 'Hide password',
      KairoCopyKey.signInHelp: 'Use your personal Kairo credentials.',
      KairoCopyKey.mfaCode: 'Six-digit verification code',
      KairoCopyKey.continueAction: 'Continue',
      KairoCopyKey.authenticationFailed:
          'Unable to sign in. Check your credentials.',
      KairoCopyKey.sessionRestored: 'Secure session',
      KairoCopyKey.passwordUpdateTitle: 'Choose a new password',
      KairoCopyKey.passwordUpdateBody:
          'Your temporary password must be changed before continuing.',
      KairoCopyKey.newPassword: 'New password',
      KairoCopyKey.confirmPassword: 'Confirm password',
      KairoCopyKey.savePassword: 'Save password',
      KairoCopyKey.passwordsDoNotMatch: 'Passwords do not match.',
      KairoCopyKey.passwordRules: 'At least 8 characters.',
      KairoCopyKey.tenantSelectionTitle: 'Choose an association',
      KairoCopyKey.tenantSelectionBody: 'Select the space you want to access.',
      KairoCopyKey.accountSecurity: 'Account security',
      KairoCopyKey.activeSessions: 'Active sessions',
      KairoCopyKey.revokeOtherSessions: 'Sign out other sessions',
      KairoCopyKey.mfa: 'Two-factor authentication',
      KairoCopyKey.mfaEnabled: 'Enabled',
      KairoCopyKey.mfaDisabled: 'Not enabled',
      KairoCopyKey.enableMfa: 'Set up MFA',
      KairoCopyKey.verifyMfa: 'Verify code',
      KairoCopyKey.securityCode: 'Security code',
      KairoCopyKey.apiUnavailable: 'The service is temporarily unavailable.',
      KairoCopyKey.changePassword: 'Change password',
      KairoCopyKey.currentPassword: 'Current password',
      KairoCopyKey.passwordUpdated:
          'Password updated. Other sessions have been signed out.',
      KairoCopyKey.forgotPassword: 'Forgot password?',
      KairoCopyKey.passwordResetRequested:
          'The request was submitted securely.',
      KairoCopyKey.securityCenter: 'Security center',
      KairoCopyKey.refresh: 'Refresh',
      KairoCopyKey.revoke: 'Revoke',
      KairoCopyKey.revokeAllSessions: 'Sign out all sessions',
      KairoCopyKey.currentSession: 'Current session',
      KairoCopyKey.noOtherSessions: 'No other active sessions.',
      KairoCopyKey.mfaSetupInstructions:
          'Add the key to an authenticator app, then enter its code.',
      KairoCopyKey.manualMfaKey: 'Manual key',
      KairoCopyKey.cancel: 'Cancel',
      KairoCopyKey.disableMfa: 'Disable MFA',
      KairoCopyKey.unknownDevice: 'Unknown device',
    },
    KairoLocale.de: <KairoCopyKey, String>{
      KairoCopyKey.appName: 'Kairo',
      KairoCopyKey.foundationLabel: 'FLUTTER-CLIENT',
      KairoCopyKey.foundationTitle: 'Grundlage für Mobilgeräte und Web',
      KairoCopyKey.foundationBody:
          'Der Flutter-Client ist bereit, die Abläufe der PWA schrittweise nachzubilden, ohne die aktuelle Plattform zu verändern.',
      KairoCopyKey.parityTitle: 'Parität mit Nachweisen',
      KairoCopyKey.parityBody:
          'Jede Funktion wird auf Android und im Web geprüft, einschließlich der mobilen Oberflächen.',
      KairoCopyKey.apiConfigured: 'API konfiguriert',
      KairoCopyKey.apiAwaitingConfiguration:
          'API muss für diese Umgebung konfiguriert werden',
      KairoCopyKey.dashboard: 'Start',
      KairoCopyKey.members: 'Mitglieder',
      KairoCopyKey.finance: 'Finanzen',
      KairoCopyKey.notices: 'Hinweise',
      KairoCopyKey.profile: 'Profil',
      KairoCopyKey.developmentOnly: 'Grundlage F0',
      KairoCopyKey.responsiveReady: 'Responsive Navigation',
      KairoCopyKey.offlineFuture: 'Offline-Modus geplant',
      KairoCopyKey.signIn: 'Anmelden',
      KairoCopyKey.signOut: 'Abmelden',
      KairoCopyKey.identifier: 'E-Mail, Telefon oder Benutzername',
      KairoCopyKey.password: 'Passwort',
      KairoCopyKey.showPassword: 'Passwort anzeigen',
      KairoCopyKey.hidePassword: 'Passwort verbergen',
      KairoCopyKey.signInHelp:
          'Verwenden Sie Ihre persönlichen Kairo-Zugangsdaten.',
      KairoCopyKey.mfaCode: 'Sechsstelliger Bestätigungscode',
      KairoCopyKey.continueAction: 'Weiter',
      KairoCopyKey.authenticationFailed:
          'Anmeldung nicht möglich. Prüfen Sie Ihre Angaben.',
      KairoCopyKey.sessionRestored: 'Sichere Sitzung',
      KairoCopyKey.passwordUpdateTitle: 'Neues Passwort festlegen',
      KairoCopyKey.passwordUpdateBody:
          'Ihr temporäres Passwort muss vor dem Fortfahren ersetzt werden.',
      KairoCopyKey.newPassword: 'Neues Passwort',
      KairoCopyKey.confirmPassword: 'Passwort bestätigen',
      KairoCopyKey.savePassword: 'Passwort speichern',
      KairoCopyKey.passwordsDoNotMatch: 'Passwörter stimmen nicht überein.',
      KairoCopyKey.passwordRules: 'Mindestens 8 Zeichen.',
      KairoCopyKey.tenantSelectionTitle: 'Verein auswählen',
      KairoCopyKey.tenantSelectionBody:
          'Wählen Sie den Bereich, den Sie öffnen möchten.',
      KairoCopyKey.accountSecurity: 'Kontosicherheit',
      KairoCopyKey.activeSessions: 'Aktive Sitzungen',
      KairoCopyKey.revokeOtherSessions: 'Andere Sitzungen abmelden',
      KairoCopyKey.mfa: 'Zwei-Faktor-Authentifizierung',
      KairoCopyKey.mfaEnabled: 'Aktiviert',
      KairoCopyKey.mfaDisabled: 'Nicht aktiviert',
      KairoCopyKey.enableMfa: 'MFA einrichten',
      KairoCopyKey.verifyMfa: 'Code prüfen',
      KairoCopyKey.securityCode: 'Sicherheitscode',
      KairoCopyKey.apiUnavailable:
          'Der Dienst ist vorübergehend nicht verfügbar.',
      KairoCopyKey.changePassword: 'Passwort ändern',
      KairoCopyKey.currentPassword: 'Aktuelles Passwort',
      KairoCopyKey.passwordUpdated:
          'Passwort aktualisiert. Andere Sitzungen wurden abgemeldet.',
      KairoCopyKey.forgotPassword: 'Passwort vergessen?',
      KairoCopyKey.passwordResetRequested:
          'Die Anfrage wurde sicher übermittelt.',
      KairoCopyKey.securityCenter: 'Sicherheitscenter',
      KairoCopyKey.refresh: 'Aktualisieren',
      KairoCopyKey.revoke: 'Widerrufen',
      KairoCopyKey.revokeAllSessions: 'Alle Sitzungen abmelden',
      KairoCopyKey.currentSession: 'Aktuelle Sitzung',
      KairoCopyKey.noOtherSessions: 'Keine weitere aktive Sitzung.',
      KairoCopyKey.mfaSetupInstructions:
          'Fügen Sie den Schlüssel einer Authenticator-App hinzu und geben Sie den Code ein.',
      KairoCopyKey.manualMfaKey: 'Manueller Schlüssel',
      KairoCopyKey.cancel: 'Abbrechen',
      KairoCopyKey.disableMfa: 'MFA deaktivieren',
      KairoCopyKey.unknownDevice: 'Unbekanntes Gerät',
    },
  };
}

class _KairoLocalizationsDelegate
    extends LocalizationsDelegate<KairoLocalizations> {
  const _KairoLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) =>
      <String>['fr', 'en', 'de'].contains(locale.languageCode);

  @override
  Future<KairoLocalizations> load(Locale locale) async =>
      KairoLocalizations(KairoLocale.fromLocale(locale));

  @override
  bool shouldReload(_KairoLocalizationsDelegate old) => false;
}
