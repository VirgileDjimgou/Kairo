import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/app_environment.dart';
import 'package:kairo_flutter/app/kairo_app.dart';
import 'package:kairo_flutter/core/api/kairo_api_client.dart';
import 'package:kairo_flutter/core/security/session_storage.dart';
import 'package:kairo_flutter/features/auth/data/auth_gateway.dart';
import 'package:kairo_flutter/features/auth/data/auth_models.dart';
import 'package:kairo_flutter/features/auth/presentation/session_controller.dart';

void main() {
  testWidgets(
    'shows the French sign-in screen and password visibility control',
    (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        KairoApp(
          environment: KairoEnvironment.fromValues(
            flavor: 'development',
            apiBaseUrl: '',
          ),
          sessionController: _signedOutController(),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Se connecter'), findsOneWidget);
      expect(find.byIcon(Icons.visibility), findsOneWidget);
    },
  );

  testWidgets('uses a centered sign-in layout on desktop', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      KairoApp(
        environment: KairoEnvironment.fromValues(
          flavor: 'development',
          apiBaseUrl: '',
        ),
        sessionController: _signedOutController(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('E-mail, téléphone ou identifiant'), findsOneWidget);
    expect(find.byType(Card), findsOneWidget);
  });
}

SessionController _signedOutController() => SessionController(
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
  Future<LoginResult> login(String identifier, String password) =>
      throw UnimplementedError();
  @override
  Future<KairoUser> me() => throw UnimplementedError();
  @override
  Future<void> revokeOtherSessions() async {}
  @override
  Future<void> revokeSession(String sessionId) async {}
  @override
  Future<void> revokeAllSessions() async {}
  @override
  Future<MfaStatus> mfaStatus() async =>
      const MfaStatus(enabled: false, enrolled: false);
  @override
  Future<MfaEnrollment> enrollMfa() async => throw UnimplementedError();
  @override
  Future<void> verifyMfa(String code) async {}
  @override
  Future<void> disableMfa() async {}
  @override
  Future<void> requestPasswordReset(String identifier) async {}
  @override
  Future<List<ActiveSession>> sessions() async => const <ActiveSession>[];
  @override
  Future<AuthToken> switchTenant(String tenantId) => throw UnimplementedError();
}
