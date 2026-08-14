import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import '../core/api/kairo_api_client.dart';
import '../core/offline/offline_workspace_controller.dart';
import '../core/security/session_storage.dart';
import '../features/auth/data/auth_gateway.dart';
import '../features/auth/presentation/auth_gate.dart';
import '../features/auth/presentation/session_controller.dart';
import 'app_environment.dart';
import 'localization/kairo_localizations.dart';
import 'theme/kairo_theme.dart';

class KairoApp extends StatefulWidget {
  KairoApp({
    super.key,
    required this.environment,
    SessionController? sessionController,
  }) : sessionController =
           sessionController ?? _defaultSessionController(environment);

  final KairoEnvironment environment;
  final SessionController sessionController;

  static SessionController _defaultSessionController(
    KairoEnvironment environment,
  ) {
    final KairoApiClient client = KairoApiClient(environment: environment);
    final OfflineWorkspaceController offlineWorkspace =
        OfflineWorkspaceController();
    client.offlineWorkspace = offlineWorkspace;
    return SessionController(
      apiClient: client,
      storage: SecureSessionStorage(),
      gateway: HttpAuthGateway(client),
      offlineWorkspace: offlineWorkspace,
    );
  }

  @override
  State<KairoApp> createState() => _KairoAppState();
}

class _KairoAppState extends State<KairoApp> {
  KairoLocale _locale = KairoLocale.fr;
  ThemeMode _themeMode = ThemeMode.system;

  void _cycleThemeMode() {
    setState(() {
      _themeMode = switch (_themeMode) {
        ThemeMode.system => ThemeMode.light,
        ThemeMode.light => ThemeMode.dark,
        ThemeMode.dark => ThemeMode.system,
      };
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Kairo',
      theme: KairoTheme.light(),
      darkTheme: KairoTheme.dark(),
      themeMode: _themeMode,
      locale: _locale.locale,
      supportedLocales: KairoLocale.values.map(
        (KairoLocale item) => item.locale,
      ),
      localizationsDelegates: const <LocalizationsDelegate<dynamic>>[
        KairoLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      initialRoute: '/',
      onGenerateRoute: _onGenerateRoute,
    );
  }

  Route<void> _onGenerateRoute(RouteSettings settings) {
    return MaterialPageRoute<void>(
      settings: settings,
      builder: (BuildContext context) => AuthGate(
        controller: widget.sessionController,
        environment: widget.environment,
        locale: _locale,
        onLocaleChanged: (KairoLocale locale) =>
            setState(() => _locale = locale),
        themeMode: _themeMode,
        onToggleThemeMode: _cycleThemeMode,
      ),
    );
  }
}
