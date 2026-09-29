import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/app_environment.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/app/theme/kairo_theme.dart';
import 'package:kairo_flutter/core/api/kairo_api_client.dart';
import 'package:kairo_flutter/core/security/session_storage.dart';
import 'package:kairo_flutter/features/auth/data/auth_gateway.dart';
import 'package:kairo_flutter/features/auth/data/auth_models.dart';
import 'package:kairo_flutter/features/auth/presentation/auth_gate.dart';
import 'package:kairo_flutter/features/auth/presentation/session_controller.dart';
import 'package:kairo_flutter/features/foundation/presentation/role_shell.dart';

void main() {
  test('F9 maps notification inbox target paths to the inbox destination', () {
    expect(notificationDestinationKey('/notifications'), 'inbox');
    expect(notificationDestinationKey('/notifications/inbox'), 'inbox');
    expect(notificationDestinationKey('/inbox'), 'inbox');
    expect(notificationDestinationKey('/finance'), 'finance');
    expect(notificationDestinationKey('/receipts'), 'receipts');
    expect(notificationDestinationKey('/discipline'), 'governance');
  });

  test('F9 rejects external and unknown notification target paths', () {
    expect(notificationDestinationKey('https://evil.example/steal'), isNull);
    expect(notificationDestinationKey('http://evil.example'), isNull);
    expect(notificationDestinationKey('//evil.example/path'), isNull);
    expect(notificationDestinationKey('/unknown-target'), isNull);
    expect(notificationDestinationKey(''), isNull);
    expect(notificationDestinationKey('relative/path'), isNull);
  });

  testWidgets('F9 sign-in controls remain accessible on phone and desktop', (
    WidgetTester tester,
  ) async {
    final SemanticsHandle handle = tester.ensureSemantics();

    for (final Size size in <Size>[
      const Size(390, 844),
      const Size(1280, 900),
    ]) {
      await tester.binding.setSurfaceSize(size);
      await tester.pumpWidget(
        MaterialApp(
          home: LoginPage(controller: _controller(), locale: KairoLocale.fr),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(seconds: 1));

      expect(find.byIcon(Icons.visibility), findsOneWidget);
      expect(find.bySemanticsLabel('Se connecter'), findsOneWidget);
      expect(find.bySemanticsLabel('Afficher le mot de passe'), findsOneWidget);
      await expectLater(
        find.byType(MaterialApp),
        matchesGoldenFile(
          size.width < 600
              ? '../artifacts/sprint-f9/sign-in-android.png'
              : '../artifacts/sprint-f9/sign-in-web.png',
        ),
      );
    }
    await tester.binding.setSurfaceSize(null);
    handle.dispose();
  });

  testWidgets('F9 sign-in stays usable at 200% Android text scaling', (
    WidgetTester tester,
  ) async {
    final SemanticsHandle handle = tester.ensureSemantics();
    await tester.binding.setSurfaceSize(const Size(390, 844));
    await tester.pumpWidget(
      MaterialApp(
        theme: KairoTheme.light(),
        home: MediaQuery(
          data: const MediaQueryData(
            size: Size(390, 844),
            textScaler: TextScaler.linear(2.0),
          ),
          child: LoginPage(controller: _controller(), locale: KairoLocale.fr),
        ),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    expect(find.bySemanticsLabel('Se connecter'), findsOneWidget);
    expect(find.bySemanticsLabel('Afficher le mot de passe'), findsOneWidget);
    expect(tester.takeException(), isNull);

    final Size toggleSize = tester.getSize(
      find.bySemanticsLabel('Afficher le mot de passe'),
    );
    expect(toggleSize.height, greaterThanOrEqualTo(44));

    await tester.binding.setSurfaceSize(null);
    handle.dispose();
  });

  testWidgets('F9 sign-in renders with the dark theme and exposes semantics', (
    WidgetTester tester,
  ) async {
    final SemanticsHandle handle = tester.ensureSemantics();
    await tester.binding.setSurfaceSize(const Size(390, 844));
    await tester.pumpWidget(
      MaterialApp(
        theme: KairoTheme.light(),
        darkTheme: KairoTheme.dark(),
        themeMode: ThemeMode.dark,
        home: LoginPage(controller: _controller(), locale: KairoLocale.fr),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    final BuildContext context = tester.element(find.byType(LoginPage));
    expect(Theme.of(context).brightness, Brightness.dark);
    expect(find.bySemanticsLabel('Se connecter'), findsOneWidget);
    expect(find.bySemanticsLabel('Afficher le mot de passe'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.binding.setSurfaceSize(null);
    handle.dispose();
  });
}

SessionController _controller() => SessionController(
  apiClient: KairoApiClient(
    environment: KairoEnvironment.fromValues(
      flavor: 'development',
      apiBaseUrl: '',
    ),
  ),
  storage: const _NoTokenStorage(),
  gateway: const _NoopGateway(),
);

class _NoTokenStorage implements SessionStorage {
  const _NoTokenStorage();
  @override
  Future<void> clear() async {}
  @override
  Future<String?> readAccessToken() async => null;
  @override
  Future<void> writeAccessToken(String token) async {}
}

class _NoopGateway implements AuthGateway {
  const _NoopGateway();
  @override
  Future<void> changeInitialPassword(String password) async {}
  @override
  Future<void> changePassword(
    String currentPassword,
    String newPassword,
  ) async {}
  @override
  Future<AuthToken> completeMfa(String challengeToken, String code) =>
      throw UnimplementedError();
  @override
  Future<void> disableMfa() async {}
  @override
  Future<MfaEnrollment> enrollMfa() async => throw UnimplementedError();
  @override
  Future<LoginResult> login(String identifier, String password) =>
      throw UnimplementedError();
  @override
  Future<KairoUser> me() => throw UnimplementedError();
  @override
  Future<MfaStatus> mfaStatus() async =>
      const MfaStatus(enabled: false, enrolled: false);
  @override
  Future<void> requestPasswordReset(String identifier) async {}
  @override
  Future<void> revokeAllSessions() async {}
  @override
  Future<void> revokeOtherSessions() async {}
  @override
  Future<void> revokeSession(String sessionId) async {}
  @override
  Future<List<ActiveSession>> sessions() async => const <ActiveSession>[];
  @override
  Future<AuthToken> switchTenant(String tenantId) => throw UnimplementedError();
  @override
  Future<void> verifyMfa(String code) async {}
}
