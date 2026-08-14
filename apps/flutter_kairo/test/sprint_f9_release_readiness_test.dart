import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/app_environment.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/core/api/kairo_api_client.dart';
import 'package:kairo_flutter/core/security/session_storage.dart';
import 'package:kairo_flutter/features/auth/data/auth_gateway.dart';
import 'package:kairo_flutter/features/auth/data/auth_models.dart';
import 'package:kairo_flutter/features/auth/presentation/auth_gate.dart';
import 'package:kairo_flutter/features/auth/presentation/session_controller.dart';

void main() {
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
