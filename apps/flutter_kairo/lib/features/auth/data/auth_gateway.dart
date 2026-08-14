import '../../../core/api/kairo_api_client.dart';
import 'auth_models.dart';

abstract interface class AuthGateway {
  Future<LoginResult> login(String identifier, String password);
  Future<AuthToken> completeMfa(String challengeToken, String code);
  Future<KairoUser> me();
  Future<AuthToken> switchTenant(String tenantId);
  Future<void> changeInitialPassword(String password);
  Future<void> changePassword(String currentPassword, String newPassword);
  Future<List<ActiveSession>> sessions();
  Future<void> revokeOtherSessions();
  Future<void> revokeSession(String sessionId);
  Future<void> revokeAllSessions();
  Future<MfaStatus> mfaStatus();
  Future<MfaEnrollment> enrollMfa();
  Future<void> verifyMfa(String code);
  Future<void> disableMfa();
  Future<void> requestPasswordReset(String identifier);
}

class HttpAuthGateway implements AuthGateway {
  HttpAuthGateway(this._client);
  final KairoApiClient _client;

  @override
  Future<LoginResult> login(String identifier, String password) async {
    final Object? payload = await _client.requestJson(
      'POST',
      '/auth/login',
      body: <String, String>{'email': identifier, 'password': password},
    );
    final Map<String, dynamic> json = payload! as Map<String, dynamic>;
    if (json['mfa_required'] == true) {
      return LoginResult.challenge(MfaChallenge(json['mfa_token'] as String));
    }
    return LoginResult.token(AuthToken.fromJson(json));
  }

  @override
  Future<AuthToken> completeMfa(String challengeToken, String code) async {
    final Object? payload = await _client.requestJson(
      'POST',
      '/auth/mfa/complete',
      body: <String, String>{'mfa_token': challengeToken, 'code': code},
    );
    return AuthToken.fromJson(payload! as Map<String, dynamic>);
  }

  @override
  Future<KairoUser> me() async =>
      KairoUser.fromJson(await _client.getJson('/auth/me'));

  @override
  Future<AuthToken> switchTenant(String tenantId) async {
    final Object? payload = await _client.requestJson(
      'POST',
      '/auth/switch-tenant',
      body: <String, String>{'tenant_id': tenantId},
    );
    return AuthToken.fromJson(payload! as Map<String, dynamic>);
  }

  @override
  Future<void> changeInitialPassword(String password) => _client.requestJson(
    'POST',
    '/auth/change-initial-password',
    body: <String, String>{'new_password': password},
  );

  @override
  Future<void> changePassword(String currentPassword, String newPassword) =>
      _client.requestJson(
        'POST',
        '/auth/change-password',
        body: <String, String>{
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      );

  @override
  Future<List<ActiveSession>> sessions() async {
    final Object? payload = await _client.requestJson('GET', '/auth/sessions');
    return (payload! as List<dynamic>)
        .map(
          (dynamic item) =>
              ActiveSession.fromJson(item as Map<String, dynamic>),
        )
        .toList(growable: false);
  }

  @override
  Future<void> revokeOtherSessions() =>
      _client.requestJson('POST', '/auth/sessions/revoke-others');

  @override
  Future<void> revokeSession(String sessionId) =>
      _client.requestJson('DELETE', '/auth/sessions/$sessionId');

  @override
  Future<void> revokeAllSessions() =>
      _client.requestJson('POST', '/auth/sessions/revoke-all');

  @override
  Future<MfaStatus> mfaStatus() async =>
      MfaStatus.fromJson(await _client.getJson('/auth/mfa/status'));

  @override
  Future<MfaEnrollment> enrollMfa() async {
    final Object? payload = await _client.requestJson(
      'POST',
      '/auth/mfa/enroll',
    );
    return MfaEnrollment.fromJson(payload! as Map<String, dynamic>);
  }

  @override
  Future<void> verifyMfa(String code) => _client.requestJson(
    'POST',
    '/auth/mfa/verify',
    body: <String, String>{'code': code},
  );

  @override
  Future<void> disableMfa() => _client.requestJson('DELETE', '/auth/mfa');

  @override
  Future<void> requestPasswordReset(String identifier) => _client.requestJson(
    'POST',
    '/auth/forgot-password',
    body: <String, String>{'email': identifier},
  );
}
