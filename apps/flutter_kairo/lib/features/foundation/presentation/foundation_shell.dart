import 'package:flutter/material.dart';

import '../../../app/app_environment.dart';
import '../../../app/localization/kairo_localizations.dart';
import '../../../app/theme/kairo_theme.dart';

class FoundationShell extends StatefulWidget {
  const FoundationShell({
    super.key,
    required this.environment,
    required this.locale,
    required this.onLocaleChanged,
    this.userName,
    this.onSignOut,
    this.onAccountSecurity,
  });

  final KairoEnvironment environment;
  final KairoLocale locale;
  final ValueChanged<KairoLocale> onLocaleChanged;
  final String? userName;
  final Future<void> Function()? onSignOut;
  final VoidCallback? onAccountSecurity;

  @override
  State<FoundationShell> createState() => _FoundationShellState();
}

class _FoundationShellState extends State<FoundationShell> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final KairoLocalizations copy = KairoLocalizations(widget.locale);
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final bool compact = constraints.maxWidth < 720;
        final Widget content = _FoundationContent(
          copy: copy,
          environment: widget.environment,
        );
        return Scaffold(
          appBar: _KairoAppBar(
            copy: copy,
            selectedLocale: widget.locale,
            onLocaleChanged: widget.onLocaleChanged,
            userName: widget.userName,
            onSignOut: widget.onSignOut,
            onAccountSecurity: widget.onAccountSecurity,
          ),
          body: compact
              ? content
              : Row(
                  children: <Widget>[
                    NavigationRail(
                      selectedIndex: _selectedIndex,
                      onDestinationSelected: (int index) =>
                          setState(() => _selectedIndex = index),
                      labelType: NavigationRailLabelType.all,
                      destinations: _destinations(copy),
                    ),
                    const VerticalDivider(width: 1),
                    Expanded(child: content),
                  ],
                ),
          bottomNavigationBar: compact
              ? NavigationBar(
                  selectedIndex: _selectedIndex,
                  onDestinationSelected: (int index) =>
                      setState(() => _selectedIndex = index),
                  destinations: _bottomDestinations(copy),
                )
              : null,
        );
      },
    );
  }

  List<NavigationRailDestination> _destinations(KairoLocalizations copy) {
    return <NavigationRailDestination>[
      NavigationRailDestination(
        icon: const Icon(Icons.home_outlined),
        selectedIcon: const Icon(Icons.home),
        label: Text(copy.text(KairoCopyKey.dashboard)),
      ),
      NavigationRailDestination(
        icon: const Icon(Icons.groups_outlined),
        selectedIcon: const Icon(Icons.groups),
        label: Text(copy.text(KairoCopyKey.members)),
      ),
      NavigationRailDestination(
        icon: const Icon(Icons.account_balance_wallet_outlined),
        selectedIcon: const Icon(Icons.account_balance_wallet),
        label: Text(copy.text(KairoCopyKey.finance)),
      ),
      NavigationRailDestination(
        icon: const Icon(Icons.notifications_none),
        selectedIcon: const Icon(Icons.notifications),
        label: Text(copy.text(KairoCopyKey.notices)),
      ),
      NavigationRailDestination(
        icon: const Icon(Icons.person_outline),
        selectedIcon: const Icon(Icons.person),
        label: Text(copy.text(KairoCopyKey.profile)),
      ),
    ];
  }

  List<NavigationDestination> _bottomDestinations(KairoLocalizations copy) {
    return <NavigationDestination>[
      NavigationDestination(
        icon: const Icon(Icons.home_outlined),
        selectedIcon: const Icon(Icons.home),
        label: copy.text(KairoCopyKey.dashboard),
      ),
      NavigationDestination(
        icon: const Icon(Icons.groups_outlined),
        selectedIcon: const Icon(Icons.groups),
        label: copy.text(KairoCopyKey.members),
      ),
      NavigationDestination(
        icon: const Icon(Icons.account_balance_wallet_outlined),
        selectedIcon: const Icon(Icons.account_balance_wallet),
        label: copy.text(KairoCopyKey.finance),
      ),
      NavigationDestination(
        icon: const Icon(Icons.notifications_none),
        selectedIcon: const Icon(Icons.notifications),
        label: copy.text(KairoCopyKey.notices),
      ),
      NavigationDestination(
        icon: const Icon(Icons.person_outline),
        selectedIcon: const Icon(Icons.person),
        label: copy.text(KairoCopyKey.profile),
      ),
    ];
  }
}

class _KairoAppBar extends StatelessWidget implements PreferredSizeWidget {
  const _KairoAppBar({
    required this.copy,
    required this.selectedLocale,
    required this.onLocaleChanged,
    this.userName,
    this.onSignOut,
    this.onAccountSecurity,
  });

  final KairoLocalizations copy;
  final KairoLocale selectedLocale;
  final ValueChanged<KairoLocale> onLocaleChanged;
  final String? userName;
  final Future<void> Function()? onSignOut;
  final VoidCallback? onAccountSecurity;

  @override
  Size get preferredSize => const Size.fromHeight(72);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      titleSpacing: 20,
      title: Row(
        children: <Widget>[
          Container(
            width: 40,
            height: 40,
            decoration: const BoxDecoration(
              color: KairoColors.primary,
              borderRadius: BorderRadius.all(Radius.circular(10)),
            ),
            child: const Icon(
              Icons.dashboard_customize_outlined,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                Text(
                  copy.text(KairoCopyKey.foundationLabel),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(
                    context,
                  ).textTheme.labelSmall?.copyWith(letterSpacing: 0.8),
                ),
                Text(
                  copy.text(KairoCopyKey.appName),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
          ),
        ],
      ),
      actions: <Widget>[
        PopupMenuButton<KairoLocale>(
          tooltip: 'Change language',
          initialValue: selectedLocale,
          onSelected: onLocaleChanged,
          itemBuilder: (BuildContext context) => KairoLocale.values
              .map(
                (KairoLocale locale) => PopupMenuItem<KairoLocale>(
                  value: locale,
                  child: Text(locale.displayName),
                ),
              )
              .toList(),
          child: Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Chip(
              avatar: const Icon(Icons.language, size: 18),
              label: Text(selectedLocale.displayName),
            ),
          ),
        ),
        if (onSignOut != null)
          IconButton(
            tooltip: copy.text(KairoCopyKey.signOut),
            onPressed: () => onSignOut!(),
            icon: const Icon(Icons.logout),
          ),
        if (onAccountSecurity != null)
          IconButton(
            tooltip: copy.text(KairoCopyKey.accountSecurity),
            onPressed: onAccountSecurity,
            icon: const Icon(Icons.security_outlined),
          ),
      ],
    );
  }
}

class _FoundationContent extends StatelessWidget {
  const _FoundationContent({required this.copy, required this.environment});

  final KairoLocalizations copy;
  final KairoEnvironment environment;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1040),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  copy.text(KairoCopyKey.developmentOnly),
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  copy.text(KairoCopyKey.foundationTitle),
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(
                  copy.text(KairoCopyKey.foundationBody),
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 24),
                LayoutBuilder(
                  builder: (BuildContext context, BoxConstraints constraints) {
                    final bool narrow = constraints.maxWidth < 620;
                    final List<Widget> cards = <Widget>[
                      _StatusCard(
                        icon: Icons.verified_outlined,
                        color: KairoColors.primary,
                        title: copy.text(KairoCopyKey.parityTitle),
                        body: copy.text(KairoCopyKey.parityBody),
                      ),
                      _StatusCard(
                        icon: environment.hasApiBaseUrl
                            ? Icons.cloud_done_outlined
                            : Icons.settings_ethernet_outlined,
                        color: environment.hasApiBaseUrl
                            ? KairoColors.success
                            : KairoColors.warning,
                        title: environment.hasApiBaseUrl
                            ? copy.text(KairoCopyKey.apiConfigured)
                            : copy.text(KairoCopyKey.apiAwaitingConfiguration),
                        body: environment.hasApiBaseUrl
                            ? environment.apiBaseUrl
                            : copy.text(KairoCopyKey.offlineFuture),
                      ),
                    ];
                    if (narrow) {
                      return Column(
                        children: <Widget>[
                          cards.first,
                          const SizedBox(height: 16),
                          cards.last,
                        ],
                      );
                    }
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Expanded(child: cards.first),
                        const SizedBox(width: 16),
                        Expanded(child: cards.last),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 16),
                Chip(
                  avatar: const Icon(Icons.phone_android_outlined, size: 18),
                  label: Text(copy.text(KairoCopyKey.responsiveReady)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _StatusCard extends StatelessWidget {
  const _StatusCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.body,
  });

  final IconData icon;
  final Color color;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Icon(icon, color: color),
            const SizedBox(height: 14),
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Text(body, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}
