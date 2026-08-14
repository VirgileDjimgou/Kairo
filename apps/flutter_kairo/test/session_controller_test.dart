import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/app_environment.dart';
import 'package:kairo_flutter/core/api/kairo_api_client.dart';
import 'package:kairo_flutter/core/security/session_storage.dart';
import 'package:kairo_flutter/features/auth/data/auth_gateway.dart';
import 'package:kairo_flutter/features/auth/data/auth_models.dart';
import 'package:kairo_flutter/features/auth/presentation/session_controller.dart';

void main() {
  test('restoring an invalid token clears the secure session', () async {
    final storage = _MemoryStorage('expired');
    final controller = _controller(storage, _FakeGateway(failMe: true));

    await controller.restore();

    expect(controller.phase, SessionPhase.signedOut);
    expect(await storage.readAccessToken(), isNull);
  });

  test('successful login persists only the access token', () async {
    final storage = _MemoryStorage();
    final controller = _controller(storage, _FakeGateway());

    await controller.login('member', 'never-persist-this-password');

    expect(controller.phase, SessionPhase.authenticated);
    expect(await storage.readAccessToken(), 'access-token');
    expect(
      storage.values.values,
      isNot(contains('never-persist-this-password')),
    );
  });

  test(
    'network login failure never leaves the session loading forever',
    () async {
      final storage = _MemoryStorage();
      final controller = _controller(
        storage,
        _FakeGateway(failLoginWithNetworkError: true),
      );

      await controller.login('member', 'password');

      expect(controller.phase, SessionPhase.signedOut);
      expect(controller.errorMessage, 'service_unavailable');
      expect(await storage.readAccessToken(), isNull);
    },
  );

  test(
    'profile loading failure clears the token accepted during login',
    () async {
      final storage = _MemoryStorage();
      final controller = _controller(
        storage,
        _FakeGateway(failMeWithNetworkError: true),
      );

      await controller.login('member', 'password');

      expect(controller.phase, SessionPhase.signedOut);
      expect(controller.errorMessage, 'service_unavailable');
      expect(await storage.readAccessToken(), isNull);
    },
  );

  test(
    'MFA challenge does not persist an access token before verification',
    () async {
      final storage = _MemoryStorage();
      final controller = _controller(storage, _FakeGateway(requiresMfa: true));

      await controller.login('member', 'password');

      expect(controller.phase, SessionPhase.mfaRequired);
      expect(await storage.readAccessToken(), isNull);
      await controller.completeMfa('123456');
      expect(controller.phase, SessionPhase.authenticated);
      expect(await storage.readAccessToken(), 'mfa-access-token');
    },
  );

  test(
    'revoking every session clears the local token and user state',
    () async {
      final storage = _MemoryStorage();
      final controller = _controller(storage, _FakeGateway());
      await controller.login('member', 'password');

      await controller.revokeAllSessions();

      expect(controller.phase, SessionPhase.signedOut);
      expect(controller.user, isNull);
      expect(await storage.readAccessToken(), isNull);
    },
  );

  test('security inventory is obtained through the API gateway', () async {
    final controller = _controller(_MemoryStorage(), _FakeGateway());
    await controller.loadSecurityState();

    expect(controller.mfaStatus?.enabled, isFalse);
    expect(controller.activeSessions, isEmpty);
  });
}

SessionController _controller(_MemoryStorage storage, _FakeGateway gateway) {
  return SessionController(
    apiClient: KairoApiClient(
      environment: KairoEnvironment.fromValues(
        flavor: 'development',
        apiBaseUrl: 'https://example.test/api/v1',
      ),
    ),
    storage: storage,
    gateway: gateway,
  );
}

class _MemoryStorage implements SessionStorage {
  _MemoryStorage([String? token]) {
    if (token != null) values['token'] = token;
  }
  final Map<String, String> values = <String, String>{};
  @override
  Future<void> clear() async => values.clear();
  @override
  Future<String?> readAccessToken() async => values['token'];
  @override
  Future<void> writeAccessToken(String token) async {
    values['token'] = token;
  }
}

class _FakeGateway implements AuthGateway {
  _FakeGateway({
    this.failMe = false,
    this.failLoginWithNetworkError = false,
    this.failMeWithNetworkError = false,
    this.requiresMfa = false,
  });
  final bool failMe;
  final bool failLoginWithNetworkError;
  final bool failMeWithNetworkError;
  final bool requiresMfa;
  @override
  Future<void> changeInitialPassword(String password) async {}
  @override
  Future<void> changePassword(
    String currentPassword,
    String newPassword,
  ) async {}
  @override
  Future<AuthToken> completeMfa(String challengeToken, String code) async =>
      const AuthToken(
        accessToken: 'mfa-access-token',
        passwordChangeRequired: false,
      );
  @override
  Future<LoginResult> login(String identifier, String password) async {
    if (failLoginWithNetworkError) throw StateError('network unavailable');
    return requiresMfa
        ? const LoginResult.challenge(MfaChallenge('mfa-token'))
        : const LoginResult.token(
            AuthToken(
              accessToken: 'access-token',
              passwordChangeRequired: false,
            ),
          );
  }

  @override
  Future<KairoUser> me() async {
    if (failMeWithNetworkError) throw StateError('network unavailable');
    if (failMe) {
      throw const KairoApiException(statusCode: 401, message: 'Expired');
    }
    return const KairoUser(
      id: 'user',
      email: 'member@combis.org',
      displayName: 'Member',
      tenantId: 'tenant',
      roles: <String>['member'],
      passwordChangeRequired: false,
      memberships: <TenantMembership>[],
    );
  }

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
  Future<MfaEnrollment> enrollMfa() async => const MfaEnrollment(
    secret: 'secret',
    uri: 'otpauth://test',
    qrCodeUrl: '',
  );
  @override
  Future<void> verifyMfa(String code) async {}
  @override
  Future<void> disableMfa() async {}
  @override
  Future<void> requestPasswordReset(String identifier) async {}
  @override
  Future<List<ActiveSession>> sessions() async => const <ActiveSession>[];
  @override
  Future<AuthToken> switchTenant(String tenantId) async => const AuthToken(
    accessToken: 'access-token',
    passwordChangeRequired: false,
  );
}
