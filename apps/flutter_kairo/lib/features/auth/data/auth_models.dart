class TenantMembership {
  const TenantMembership({
    required this.tenantId,
    required this.slug,
    required this.name,
    required this.roles,
  });

  factory TenantMembership.fromJson(Map<String, dynamic> json) =>
      TenantMembership(
        tenantId: json['tenant_id'] as String,
        slug: json['slug'] as String,
        name: json['name'] as String,
        roles: List<String>.from(
          json['roles'] as List<dynamic>? ?? <dynamic>[],
        ),
      );

  final String tenantId;
  final String slug;
  final String name;
  final List<String> roles;
}

class KairoUser {
  const KairoUser({
    required this.id,
    required this.email,
    required this.displayName,
    required this.tenantId,
    required this.roles,
    required this.passwordChangeRequired,
    required this.memberships,
  });

  factory KairoUser.fromJson(Map<String, dynamic> json) => KairoUser(
    id: json['id'] as String,
    email: json['email'] as String,
    displayName: json['display_name'] as String,
    tenantId: json['tenant_id'] as String,
    roles: List<String>.from(json['roles'] as List<dynamic>? ?? <dynamic>[]),
    passwordChangeRequired: json['password_change_required'] as bool? ?? false,
    memberships: (json['memberships'] as List<dynamic>? ?? <dynamic>[])
        .map(
          (dynamic item) =>
              TenantMembership.fromJson(item as Map<String, dynamic>),
        )
        .toList(growable: false),
  );

  final String id;
  final String email;
  final String displayName;
  final String tenantId;
  final List<String> roles;
  final bool passwordChangeRequired;
  final List<TenantMembership> memberships;
}

class AuthToken {
  const AuthToken({
    required this.accessToken,
    required this.passwordChangeRequired,
  });

  factory AuthToken.fromJson(Map<String, dynamic> json) => AuthToken(
    accessToken: json['access_token'] as String,
    passwordChangeRequired: json['password_change_required'] as bool? ?? false,
  );

  final String accessToken;
  final bool passwordChangeRequired;
}

class MfaChallenge {
  const MfaChallenge(this.token);
  final String token;
}

class LoginResult {
  const LoginResult.token(this.token) : challenge = null;
  const LoginResult.challenge(this.challenge) : token = null;
  final AuthToken? token;
  final MfaChallenge? challenge;
}

class ActiveSession {
  const ActiveSession({
    required this.id,
    required this.current,
    required this.lastSeenAt,
    required this.createdAt,
    required this.deviceLabel,
  });

  factory ActiveSession.fromJson(Map<String, dynamic> json) => ActiveSession(
    id: json['id'] as String,
    current: json['current'] as bool? ?? false,
    lastSeenAt: DateTime.tryParse(json['last_seen_at'] as String? ?? ''),
    createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
    deviceLabel:
        (json['last_seen_user_agent'] ?? json['created_user_agent'] ?? '')
            as String,
  );

  final String id;
  final bool current;
  final DateTime? lastSeenAt;
  final DateTime? createdAt;
  final String deviceLabel;
}

class MfaStatus {
  const MfaStatus({required this.enabled, required this.enrolled});
  factory MfaStatus.fromJson(Map<String, dynamic> json) => MfaStatus(
    enabled: json['enabled'] as bool? ?? false,
    enrolled: json['enrolled'] as bool? ?? false,
  );
  final bool enabled;
  final bool enrolled;
}

class MfaEnrollment {
  const MfaEnrollment({
    required this.secret,
    required this.uri,
    required this.qrCodeUrl,
  });
  factory MfaEnrollment.fromJson(Map<String, dynamic> json) => MfaEnrollment(
    secret: json['secret'] as String,
    uri: json['uri'] as String,
    qrCodeUrl: json['qr_code_url'] as String? ?? '',
  );
  final String secret;
  final String uri;
  final String qrCodeUrl;
}
