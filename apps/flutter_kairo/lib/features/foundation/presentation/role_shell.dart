import 'package:flutter/material.dart';

import '../../../app/app_environment.dart';
import '../../../app/localization/kairo_localizations.dart';
import '../../../core/offline/offline_status_banner.dart';
import '../../../core/offline/offline_workspace_controller.dart';
import '../../../design_system/components/app_metric_card.dart';
import '../../../design_system/components/app_section_header.dart';
import '../../../design_system/components/app_surface_card.dart';
import '../../../design_system/theme/app_tokens.dart';
import '../../auth/data/auth_models.dart';
import '../../chat/data/chat_gateway.dart';
import '../../chat/presentation/chat_workspace_page.dart';
import '../../finance/data/finance_gateway.dart';
import '../../finance/data/member_statement_gateway.dart';
import '../../finance/data/receipt_gateway.dart';
import '../../finance/presentation/finance_workspace_page.dart';
import '../../finance/presentation/member_statement_page.dart';
import '../../finance/presentation/receipt_controller.dart';
import '../../finance/presentation/receipt_workspace.dart';
import '../../governance/data/governance_gateway.dart';
import '../../governance/data/operation_journal_gateway.dart';
import '../../governance/presentation/governance_workspace_page.dart';
import '../../governance/presentation/operation_journal_page.dart';
import '../../members/presentation/member_controller.dart';
import '../../members/presentation/member_directory_page.dart';
import '../../notifications/data/fcm_registration_state.dart';
import '../../notifications/data/inbox_gateway.dart';
import '../../notifications/presentation/inbox_page.dart';

class RoleShell extends StatefulWidget {
  const RoleShell({
    super.key,
    required this.environment,
    required this.locale,
    required this.onLocaleChanged,
    required this.user,
    required this.onSignOut,
    required this.onAccountSecurity,
    required this.memberController,
    required this.receiptGateway,
    required this.receiptController,
    required this.memberStatementGateway,
    this.financeGateway,
    required this.inboxGateway,
    required this.operationJournalGateway,
    this.governanceGateway,
    this.chatGateway,
    this.offlineWorkspace,
    this.onEnableAndroidPush,
    this.notificationTargetPath,
    this.onNotificationTargetHandled,
    this.themeMode = ThemeMode.system,
    this.onToggleThemeMode,
  });

  final KairoEnvironment environment;
  final KairoLocale locale;
  final ValueChanged<KairoLocale> onLocaleChanged;
  final KairoUser user;
  final Future<void> Function() onSignOut;
  final VoidCallback onAccountSecurity;
  final MemberController memberController;
  final ReceiptGateway receiptGateway;
  final ReceiptController receiptController;
  final MemberStatementGateway memberStatementGateway;
  final FinanceGateway? financeGateway;
  final InboxGateway inboxGateway;
  final OperationJournalGateway operationJournalGateway;
  final GovernanceGateway? governanceGateway;
  final ChatGateway? chatGateway;
  final OfflineWorkspaceController? offlineWorkspace;
  final Future<FcmRegistrationState> Function()? onEnableAndroidPush;
  final String? notificationTargetPath;
  final VoidCallback? onNotificationTargetHandled;
  final ThemeMode themeMode;
  final VoidCallback? onToggleThemeMode;

  @override
  State<RoleShell> createState() => _RoleShellState();
}

class _RoleShellState extends State<RoleShell> {
  int _index = 0;
  List<String> _destinationKeys = const <String>[];
  String? _handledNotificationTarget;
  @override
  Widget build(BuildContext context) {
    final _ShellText text = _ShellText(widget.locale);
    final bool canDirectory = _hasAny(<String>[
      'principal_admin',
      'president',
      'vice_president',
      'secretary_general',
      'treasurer',
      'auditor',
      'censor',
      'sports_manager',
    ]);
    final bool canCreate = _hasAny(<String>[
      'principal_admin',
      'president',
      'secretary_general',
    ]);
    final bool canDeclareReceipt = _hasAny(<String>[
      'principal_admin',
      'president',
      'vice_president',
      'secretary_general',
      'treasurer',
      'auditor',
      'censor',
      'sports_manager',
    ]);
    final bool canProcessReceipt = _hasAny(<String>[
      'principal_admin',
      'treasurer',
    ]);
    final bool canUseFinance = _hasAny(<String>[
      'principal_admin',
      'treasurer',
      'auditor',
    ]);
    final bool canWriteExpenses = _hasAny(<String>['treasurer']);
    final bool canUseChat = _hasAny(<String>[
      'principal_admin',
      'president',
      'vice_president',
      'secretary_general',
      'treasurer',
      'auditor',
      'censor',
      'sports_manager',
      'member',
    ]);
    final bool canUseGovernance = _hasAny(<String>[
      'principal_admin',
      'president',
      'vice_president',
      'secretary_general',
      'treasurer',
      'auditor',
      'censor',
      'sports_manager',
      'ordinary_member',
    ]);
    final List<_Destination> destinations = <_Destination>[
      _Destination(
        key: 'home',
        icon: Icons.dashboard_outlined,
        selectedIcon: Icons.dashboard,
        label: text.home,
        child: _Dashboard(
          user: widget.user,
          text: text,
          canDirectory: canDirectory,
          onOpenMembers: () => setState(() => _index = 1),
        ),
      ),
      if (canDirectory)
        _Destination(
          key: 'members',
          icon: Icons.groups_outlined,
          selectedIcon: Icons.groups,
          label: text.members,
          child: MemberDirectoryPage(
            controller: widget.memberController,
            locale: widget.locale,
            canCreate: canCreate,
          ),
        ),
      if (canDirectory)
        _Destination(
          key: 'journal',
          icon: Icons.history_outlined,
          selectedIcon: Icons.history,
          label: text.journal,
          child: OperationJournalPage(
            gateway: widget.operationJournalGateway,
            locale: widget.locale,
          ),
        ),
      if (canDeclareReceipt)
        _Destination(
          key: 'receipts',
          icon: Icons.payments_outlined,
          selectedIcon: Icons.payments,
          label: text.receipts,
          child: ReceiptWorkspace(
            gateway: widget.receiptGateway,
            controller: widget.receiptController,
            canProcess: canProcessReceipt,
            locale: widget.locale,
            offlineWorkspace: widget.offlineWorkspace,
          ),
        ),
      if (canUseFinance && widget.financeGateway != null)
        _Destination(
          key: 'finance',
          icon: Icons.account_balance_wallet_outlined,
          selectedIcon: Icons.account_balance_wallet,
          label: text.finance,
          child: FinanceWorkspacePage(
            gateway: widget.financeGateway!,
            memberGateway: widget.memberController.gateway,
            locale: widget.locale,
            canWriteExpenses: canWriteExpenses,
            offlineWorkspace: widget.offlineWorkspace,
          ),
        ),
      if (canUseGovernance && widget.governanceGateway != null)
        _Destination(
          key: 'governance',
          icon: Icons.account_balance_outlined,
          selectedIcon: Icons.account_balance,
          label: text.governance,
          child: GovernanceWorkspacePage(
            gateway: widget.governanceGateway!,
            memberGateway: widget.memberController.gateway,
            locale: widget.locale,
            roles: widget.user.roles,
          ),
        ),
      if (canUseChat && widget.chatGateway != null)
        _Destination(
          key: 'chat',
          icon: Icons.chat_bubble_outline,
          selectedIcon: Icons.chat_bubble,
          label: text.chat,
          child: ChatWorkspacePage(
            gateway: widget.chatGateway!,
            locale: widget.locale,
          ),
        ),
      _Destination(
        key: 'contributions',
        icon: Icons.account_balance_outlined,
        selectedIcon: Icons.account_balance,
        label: text.contributions,
        child: MemberStatementPage(
          gateway: widget.memberStatementGateway,
          locale: widget.locale,
        ),
      ),
      _Destination(
        key: 'inbox',
        icon: Icons.notifications_none,
        selectedIcon: Icons.notifications,
        label: text.inbox,
        child: InboxPage(
          gateway: widget.inboxGateway,
          locale: widget.locale,
          onOpenTarget: _openNotificationTarget,
          onEnableAndroidPush: widget.onEnableAndroidPush,
        ),
      ),
      _Destination(
        key: 'profile',
        icon: Icons.person_outline,
        selectedIcon: Icons.person,
        label: text.profile,
        child: _ProfilePage(
          user: widget.user,
          text: text,
          onSecurity: widget.onAccountSecurity,
        ),
      ),
    ];
    _destinationKeys = destinations
        .map((destination) => destination.key)
        .toList();
    final String? notificationTargetPath = widget.notificationTargetPath;
    if (notificationTargetPath != null &&
        notificationTargetPath != _handledNotificationTarget) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        _handledNotificationTarget = notificationTargetPath;
        _openNotificationTarget(notificationTargetPath);
        widget.onNotificationTargetHandled?.call();
      });
    }
    if (_index >= destinations.length) {
      _index = 0;
    }
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final bool compact = constraints.maxWidth < 800;
        return Scaffold(
          appBar: AppBar(
            titleSpacing: 20,
            title: _Brand(text: text, user: widget.user),
            actions: <Widget>[
              _LanguageMenu(
                locale: widget.locale,
                onChanged: widget.onLocaleChanged,
              ),
              if (widget.onToggleThemeMode != null)
                IconButton(
                  onPressed: widget.onToggleThemeMode,
                  tooltip: text.themeMode(widget.themeMode),
                  icon: Icon(
                    widget.themeMode == ThemeMode.dark
                        ? Icons.dark_mode
                        : widget.themeMode == ThemeMode.light
                        ? Icons.light_mode
                        : Icons.brightness_auto_outlined,
                  ),
                ),
              IconButton(
                onPressed: widget.onAccountSecurity,
                tooltip: text.security,
                icon: const Icon(Icons.security_outlined),
              ),
              IconButton(
                onPressed: widget.onSignOut,
                tooltip: text.signOut,
                icon: const Icon(Icons.logout),
              ),
            ],
          ),
          body: Column(
            children: <Widget>[
              if (widget.offlineWorkspace != null)
                OfflineStatusBanner(
                  controller: widget.offlineWorkspace!,
                  locale: widget.locale.name,
                ),
              Expanded(
                child: compact
                    ? destinations[_index].child
                    : Row(
                        children: <Widget>[
                          NavigationRail(
                            selectedIndex: _index,
                            onDestinationSelected: (int value) =>
                                setState(() => _index = value),
                            labelType: NavigationRailLabelType.all,
                            destinations: destinations
                                .map(
                                  (item) => NavigationRailDestination(
                                    icon: Icon(item.icon),
                                    selectedIcon: Icon(item.selectedIcon),
                                    label: Text(item.label),
                                  ),
                                )
                                .toList(),
                          ),
                          const VerticalDivider(width: 1),
                          Expanded(child: destinations[_index].child),
                        ],
                      ),
              ),
            ],
          ),
          bottomNavigationBar: compact
              ? _buildMobileNavigation(destinations, text)
              : null,
        );
      },
    );
  }

  bool _hasAny(List<String> expected) =>
      widget.user.roles.any(expected.contains);

  Widget _buildMobileNavigation(
    List<_Destination> destinations,
    _ShellText text,
  ) {
    if (destinations.length <= 5) {
      return NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (int value) => setState(() => _index = value),
        destinations: destinations.map(_navigationDestination).toList(),
      );
    }

    final List<int> directIndexes = _mobileDirectIndexes(destinations);
    final int selectedDirectIndex = directIndexes.indexOf(_index);
    return NavigationBar(
      selectedIndex: selectedDirectIndex >= 0
          ? selectedDirectIndex
          : directIndexes.length,
      onDestinationSelected: (int value) {
        if (value < directIndexes.length) {
          setState(() => _index = directIndexes[value]);
          return;
        }
        _showMoreDestinations(destinations, directIndexes, text);
      },
      destinations: <NavigationDestination>[
        ...directIndexes.map(
          (int index) => _navigationDestination(destinations[index]),
        ),
        NavigationDestination(
          icon: const Icon(Icons.more_horiz),
          selectedIcon: const Icon(Icons.more_horiz),
          label: text.more,
        ),
      ],
    );
  }

  List<int> _mobileDirectIndexes(List<_Destination> destinations) {
    final List<int> direct = <int>[];
    void addKey(String key) {
      final int index = destinations.indexWhere((item) => item.key == key);
      if (index >= 0 && !direct.contains(index) && direct.length < 3) {
        direct.add(index);
      }
    }

    addKey('home');
    for (final key in <String>[
      'members',
      'finance',
      'receipts',
      'contributions',
      'governance',
      'chat',
      'profile',
    ]) {
      addKey(key);
    }
    final int inboxIndex = destinations.indexWhere(
      (item) => item.key == 'inbox',
    );
    if (inboxIndex >= 0) direct.add(inboxIndex);
    return direct;
  }

  NavigationDestination _navigationDestination(_Destination item) =>
      NavigationDestination(
        icon: Icon(item.icon),
        selectedIcon: Icon(item.selectedIcon),
        label: item.key == 'receipts'
            ? (widget.locale == KairoLocale.en
                  ? 'Cash'
                  : widget.locale == KairoLocale.de
                  ? 'Kasse'
                  : 'Caisse')
            : item.key == 'inbox'
            ? (widget.locale == KairoLocale.en
                  ? 'Alerts'
                  : widget.locale == KairoLocale.de
                  ? 'Hinweise'
                  : 'Alertes')
            : item.label,
      );

  Future<void> _showMoreDestinations(
    List<_Destination> destinations,
    List<int> directIndexes,
    _ShellText text,
  ) async {
    final int? selected = await showModalBottomSheet<int>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (BuildContext context) => SafeArea(
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.sizeOf(context).height * 0.72,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
                child: Text(
                  text.allWorkspaces,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              Flexible(
                child: ListView(
                  shrinkWrap: true,
                  children: <Widget>[
                    for (int index = 0; index < destinations.length; index++)
                      if (!directIndexes.contains(index))
                        ListTile(
                          leading: Icon(
                            index == _index
                                ? destinations[index].selectedIcon
                                : destinations[index].icon,
                          ),
                          title: Text(destinations[index].label),
                          selected: index == _index,
                          trailing: index == _index
                              ? const Icon(Icons.check_circle)
                              : null,
                          onTap: () => Navigator.of(context).pop(index),
                        ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
    if (selected != null && mounted) setState(() => _index = selected);
  }

  void _openNotificationTarget(String path) {
    final value = path.toLowerCase();
    final key = value.contains('receipt') || value.contains('encaissement')
        ? 'receipts'
        : value.contains('finance') || value.contains('expense')
        ? 'finance'
        : value.contains('disciplin') || value.contains('censor')
        ? 'governance'
        : value.contains('member')
        ? 'members'
        : value.contains('chat')
        ? 'chat'
        : 'home';
    final index = _destinationKeys.indexOf(key);
    if (index >= 0) setState(() => _index = index);
  }
}

class _Destination {
  const _Destination({
    required this.key,
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.child,
  });
  final String key;
  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final Widget child;
}

class _Brand extends StatelessWidget {
  const _Brand({required this.text, required this.user});
  final _ShellText text;
  final KairoUser user;
  @override
  Widget build(BuildContext context) => Row(
    children: <Widget>[
      DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.primaryContainer,
          borderRadius: AppRadius.small,
        ),
        child: SizedBox(
          width: 40,
          height: 40,
          child: Icon(
            Icons.dashboard_customize_outlined,
            color: Theme.of(context).colorScheme.onPrimaryContainer,
          ),
        ),
      ),
      const SizedBox(width: AppSpacing.sm),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Text(text.workspace, style: Theme.of(context).textTheme.labelSmall),
            Text(
              text.roleLabel(user.roles),
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ],
        ),
      ),
    ],
  );
}

class _LanguageMenu extends StatelessWidget {
  const _LanguageMenu({required this.locale, required this.onChanged});
  final KairoLocale locale;
  final ValueChanged<KairoLocale> onChanged;
  @override
  Widget build(BuildContext context) => PopupMenuButton<KairoLocale>(
    initialValue: locale,
    onSelected: onChanged,
    itemBuilder: (_) => KairoLocale.values
        .map(
          (item) => PopupMenuItem(value: item, child: Text(item.displayName)),
        )
        .toList(),
    child: Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Chip(label: Text(locale.displayName)),
    ),
  );
}

class _Dashboard extends StatelessWidget {
  const _Dashboard({
    required this.user,
    required this.text,
    required this.canDirectory,
    required this.onOpenMembers,
  });
  final KairoUser user;
  final _ShellText text;
  final bool canDirectory;
  final VoidCallback onOpenMembers;
  @override
  Widget build(BuildContext context) {
    final List<Widget> cards = <Widget>[
      AppMetricCard(
        icon: Icons.verified_user_outlined,
        title: text.accessTitle,
        value: '${user.roles.length}',
        detail: text.roles(user.roles),
        tone: AppCardTone.primary,
      ),
      AppMetricCard(
        icon: Icons.sync_outlined,
        title: text.dataTitle,
        value: '✓',
        detail: text.dataBody,
        tone: AppCardTone.success,
      ),
      AppMetricCard(
        icon: Icons.notifications_none,
        title: text.inbox,
        value: '•',
        detail: text.inboxBody,
        tone: AppCardTone.tertiary,
      ),
    ];
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1120),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              AppSurfaceCard(
                tone: AppCardTone.primary,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      text.kicker,
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: AppSpacing.sm),
                    Text(
                      text.welcome(user.displayName),
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: AppSpacing.xs),
                    Text(text.dashboardBody(user.roles)),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.xl),
              AppSectionHeader(title: text.accessTitle, eyebrow: text.kicker),
              const SizedBox(height: AppSpacing.sm),
              LayoutBuilder(
                builder: (BuildContext context, BoxConstraints constraints) {
                  if (constraints.maxWidth < 620) {
                    return Column(
                      children: cards
                          .map(
                            (Widget card) => Padding(
                              padding: const EdgeInsets.only(
                                bottom: AppSpacing.sm,
                              ),
                              child: card,
                            ),
                          )
                          .toList(),
                    );
                  }
                  return Row(
                    children: <Widget>[
                      Expanded(child: cards[0]),
                      const SizedBox(width: AppSpacing.sm),
                      Expanded(child: cards[1]),
                      const SizedBox(width: AppSpacing.sm),
                      Expanded(child: cards[2]),
                    ],
                  );
                },
              ),
              if (canDirectory) ...<Widget>[
                const SizedBox(height: AppSpacing.sm),
                AppSurfaceCard(
                  tone: AppCardTone.secondary,
                  onTap: onOpenMembers,
                  child: LayoutBuilder(
                    builder:
                        (BuildContext context, BoxConstraints constraints) {
                          final Widget copy = Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text(
                                text.membersTitle,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              Text(text.membersBody),
                            ],
                          );
                          if (constraints.maxWidth < 460) {
                            return Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Icon(
                                  Icons.groups_outlined,
                                  color: Theme.of(context).colorScheme.primary,
                                ),
                                const SizedBox(height: AppSpacing.sm),
                                copy,
                                const SizedBox(height: AppSpacing.md),
                                FilledButton(
                                  onPressed: onOpenMembers,
                                  child: Text(text.openMembers),
                                ),
                              ],
                            );
                          }
                          return Row(
                            children: <Widget>[
                              Icon(
                                Icons.groups_outlined,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                              const SizedBox(width: AppSpacing.sm),
                              Expanded(child: copy),
                              FilledButton(
                                onPressed: onOpenMembers,
                                child: Text(text.openMembers),
                              ),
                            ],
                          );
                        },
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _ProfilePage extends StatelessWidget {
  const _ProfilePage({
    required this.user,
    required this.text,
    required this.onSecurity,
  });
  final KairoUser user;
  final _ShellText text;
  final VoidCallback onSecurity;
  @override
  Widget build(BuildContext context) => Center(
    child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 560),
      child: AppSurfaceCard(
        tone: AppCardTone.tertiary,
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.xs),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              CircleAvatar(
                radius: 28,
                backgroundColor: Theme.of(context).colorScheme.primary,
                foregroundColor: Theme.of(context).colorScheme.onPrimary,
                child: Text(
                  user.displayName.isEmpty
                      ? '?'
                      : user.displayName.characters.first.toUpperCase(),
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              Text(
                user.displayName,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(user.email),
              const SizedBox(height: AppSpacing.md),
              Text(text.roles(user.roles)),
              const SizedBox(height: AppSpacing.md),
              OutlinedButton.icon(
                onPressed: onSecurity,
                icon: const Icon(Icons.security_outlined),
                label: Text(text.security),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class _ShellText {
  const _ShellText(this.locale);
  final KairoLocale locale;
  bool get en => locale == KairoLocale.en;
  bool get de => locale == KairoLocale.de;
  String get workspace => en
      ? 'ASSOCIATION WORKSPACE'
      : de
      ? 'VEREINSBEREICH'
      : 'ESPACE ASSOCIATION';
  String roleLabel(List<String> roles) => 'Kairo — ${roles.join(', ')}';
  String get home => en
      ? 'Home'
      : de
      ? 'Start'
      : 'Accueil';
  String get members => en
      ? 'Members'
      : de
      ? 'Mitglieder'
      : 'Membres';
  String get contributions => en
      ? 'Contributions'
      : de
      ? 'Beiträge'
      : 'Cotisations';
  String get journal => en
      ? 'Journal'
      : de
      ? 'Journal'
      : 'Journal';
  String get receipts => en
      ? 'Receipts'
      : de
      ? 'Einnahmen'
      : 'Encaissements';
  String get finance => en
      ? 'Finance'
      : de
      ? 'Finanzen'
      : 'Finances';
  String get governance => en
      ? 'Governance'
      : de
      ? 'Governance'
      : 'Gouvernance';
  String get chat => 'Chat';
  String get inbox => en
      ? 'Inbox'
      : de
      ? 'Postfach'
      : 'Notifications';
  String get profile => en
      ? 'Profile'
      : de
      ? 'Profil'
      : 'Profil';
  String get more => en
      ? 'More'
      : de
      ? 'Mehr'
      : 'Plus';
  String get allWorkspaces => en
      ? 'All workspaces'
      : de
      ? 'Alle Bereiche'
      : 'Tous les espaces';
  String get security => en
      ? 'Account security'
      : de
      ? 'Kontosicherheit'
      : 'Sécurité du compte';
  String get signOut => en
      ? 'Sign out'
      : de
      ? 'Abmelden'
      : 'Se déconnecter';
  String themeMode(ThemeMode mode) => switch (mode) {
    ThemeMode.dark =>
      en
          ? 'Use system appearance'
          : de
          ? 'Systemdarstellung verwenden'
          : 'Utiliser l’apparence système',
    ThemeMode.light =>
      en
          ? 'Use dark appearance'
          : de
          ? 'Dunkles Design utiliser'
          : 'Utiliser l’apparence sombre',
    ThemeMode.system =>
      en
          ? 'Use light appearance'
          : de
          ? 'Helles Design verwenden'
          : 'Utiliser l’apparence claire',
  };
  String get kicker => en
      ? 'ROLE-AWARE DASHBOARD'
      : de
      ? 'ROLLENBASIERTES DASHBOARD'
      : 'TABLEAU DE BORD PAR RÔLE';
  String welcome(String name) => en
      ? 'Welcome back, $name'
      : de
      ? 'Willkommen zurück, $name'
      : 'Bon retour, $name';
  String dashboardBody(List<String> roles) => en
      ? 'Your available areas are based on the association role returned by the secure API.'
      : de
      ? 'Ihre verfügbaren Bereiche basieren auf der von der sicheren API zurückgegebenen Vereinsrolle.'
      : 'Vos espaces disponibles dépendent du rôle associatif renvoyé par l’API sécurisée.';
  String get accessTitle => en
      ? 'Your access'
      : de
      ? 'Ihre Zugriffe'
      : 'Vos accès';
  String roles(List<String> roles) => roles.join(' · ');
  String get dataTitle => en
      ? 'Data status'
      : de
      ? 'Datenstatus'
      : 'État des données';
  String get dataBody => en
      ? 'Loading and retry states are built into each workspace.'
      : de
      ? 'Lade- und Wiederholungszustände sind in jeden Bereich integriert.'
      : 'Les états de chargement et de reprise sont intégrés à chaque espace.';
  String get inboxBody => en
      ? 'Your authorised operation alerts and reminders are available in the notification inbox.'
      : de
      ? 'Ihre berechtigten Vorgangshinweise und Erinnerungen sind im Benachrichtigungspostfach verfügbar.'
      : 'Vos alertes et rappels autorisés sont disponibles dans la boîte de notifications.';
  String get membersTitle => en
      ? 'Member operations'
      : de
      ? 'Mitgliederverwaltung'
      : 'Gestion des membres';
  String get membersBody => en
      ? 'Search the authorised directory and open a member profile.'
      : de
      ? 'Durchsuchen Sie das berechtigte Verzeichnis und öffnen Sie ein Mitgliederprofil.'
      : 'Recherchez dans l’annuaire autorisé et ouvrez un profil membre.';
  String get openMembers => en
      ? 'Open members'
      : de
      ? 'Mitglieder öffnen'
      : 'Ouvrir les membres';
}
