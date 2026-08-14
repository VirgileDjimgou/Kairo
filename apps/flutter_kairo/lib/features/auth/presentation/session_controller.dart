import 'package:flutter/foundation.dart';

import '../../../core/api/kairo_api_client.dart';
import '../../../core/offline/offline_workspace_controller.dart';
import '../../../core/security/session_storage.dart';
import '../data/auth_gateway.dart';
import '../data/auth_models.dart';

enum SessionPhase {
  checking,
  signedOut,
  mfaRequired,
  passwordChangeRequired,
  authenticated,
}

class SessionController extends ChangeNotifier {
  SessionController({
    required this.gateway,
    required this.storage,
    required this.apiClient,
    OfflineWorkspaceController? offlineWorkspace,
  }) : offlineWorkspace = offlineWorkspace ?? OfflineWorkspaceController();

  final AuthGateway gateway;
  final SessionStorage storage;
  final KairoApiClient apiClient;
  final OfflineWorkspaceController offlineWorkspace;
  SessionPhase phase = SessionPhase.checking;
  KairoUser? user;
  String? mfaToken;
  String? errorMessage;
  List<ActiveSession> activeSessions = const <ActiveSession>[];
  MfaStatus? mfaStatus;
  MfaEnrollment? mfaEnrollment;

  Future<void> restore() async {
    try {
      final String? token = await storage.readAccessToken();
      if (token == null) {
        phase = SessionPhase.signedOut;
        notifyListeners();
        return;
      }
      apiClient.accessToken = token;
      await _loadUser();
    } catch (_) {
      await signOut();
    }
  }

  Future<void> login(String identifier, String password) async {
    errorMessage = null;
    phase = SessionPhase.checking;
    notifyListeners();
    try {
      final LoginResult result = await gateway.login(
        identifier.trim(),
        password,
      );
      if (result.challenge != null) {
        mfaToken = result.challenge!.token;
        phase = SessionPhase.mfaRequired;
        notifyListeners();
        return;
      }
      await _acceptToken(result.token!);
    } on KairoApiException catch (error) {
      await _rejectAuthentication(error.message);
    } catch (_) {
      await _rejectAuthentication('service_unavailable');
    }
  }

  Future<void> completeMfa(String code) async {
    if (mfaToken == null) return;
    errorMessage = null;
    phase = SessionPhase.checking;
    notifyListeners();
    try {
      await _acceptToken(await gateway.completeMfa(mfaToken!, code));
    } on KairoApiException catch (error) {
      errorMessage = error.message;
      phase = SessionPhase.mfaRequired;
      notifyListeners();
    } catch (_) {
      errorMessage = 'service_unavailable';
      phase = SessionPhase.mfaRequired;
      notifyListeners();
    }
  }

  Future<void> switchTenant(String tenantId) async {
    await _acceptToken(await gateway.switchTenant(tenantId));
  }

  Future<void> replaceInitialPassword(String password) async {
    await gateway.changeInitialPassword(password);
    await _loadUser();
  }

  Future<void> changePassword(
    String currentPassword,
    String newPassword,
  ) async {
    await gateway.changePassword(currentPassword, newPassword);
    await loadSecurityState();
  }

  Future<void> loadSecurityState() async {
    final results = await Future.wait<Object>(<Future<Object>>[
      gateway.sessions(),
      gateway.mfaStatus(),
    ]);
    activeSessions = results[0] as List<ActiveSession>;
    mfaStatus = results[1] as MfaStatus;
    notifyListeners();
  }

  Future<void> startMfaEnrollment() async {
    mfaEnrollment = await gateway.enrollMfa();
    notifyListeners();
  }

  Future<void> verifyMfaEnrollment(String code) async {
    await gateway.verifyMfa(code);
    mfaEnrollment = null;
    await loadSecurityState();
  }

  Future<void> disableMfa() async {
    await gateway.disableMfa();
    await loadSecurityState();
  }

  Future<void> revokeOtherSessions() async {
    await gateway.revokeOtherSessions();
    await loadSecurityState();
  }

  Future<void> revokeSession(String sessionId) async {
    await gateway.revokeSession(sessionId);
    await loadSecurityState();
  }

  Future<void> revokeAllSessions() async {
    await gateway.revokeAllSessions();
    await signOut();
  }

  Future<void> requestPasswordReset(String identifier) =>
      gateway.requestPasswordReset(identifier);

  Future<void> signOut() async {
    apiClient.accessToken = null;
    user = null;
    mfaToken = null;
    errorMessage = null;
    await storage.clear();
    await offlineWorkspace.clearCurrentScope();
    phase = SessionPhase.signedOut;
    notifyListeners();
  }

  Future<void> _acceptToken(AuthToken token) async {
    apiClient.accessToken = token.accessToken;
    await storage.writeAccessToken(token.accessToken);
    await _loadUser();
  }

  Future<void> _rejectAuthentication(String message) async {
    apiClient.accessToken = null;
    user = null;
    await storage.clear();
    errorMessage = message;
    phase = SessionPhase.signedOut;
    notifyListeners();
  }

  Future<void> _loadUser() async {
    user = await gateway.me();
    await offlineWorkspace.activate(
      OfflineScope(userId: user!.id, tenantId: user!.tenantId),
    );
    phase = user!.passwordChangeRequired
        ? SessionPhase.passwordChangeRequired
        : SessionPhase.authenticated;
    notifyListeners();
  }
}
