import 'dart:async';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'fcm_registration_state.dart';
import 'inbox_gateway.dart';

class FcmRuntime {
  StreamSubscription<String>? _tokenRefreshSubscription;
  StreamSubscription<RemoteMessage>? _messageOpenSubscription;
  bool _notificationOpenConfigured = false;

  Future<void> configureNotificationOpens(
    void Function(String targetPath) onTargetPath,
  ) async {
    try {
      await _initializeFirebase();
      if (_notificationOpenConfigured) return;
      _notificationOpenConfigured = true;
      final FirebaseMessaging messaging = FirebaseMessaging.instance;
      final RemoteMessage? initialMessage = await messaging.getInitialMessage();
      final String? initialTarget = initialMessage?.data['target_path'];
      if (initialTarget != null && initialTarget.isNotEmpty) {
        onTargetPath(initialTarget);
      }
      _messageOpenSubscription = FirebaseMessaging.onMessageOpenedApp.listen((
        RemoteMessage message,
      ) {
        final String? targetPath = message.data['target_path'];
        if (targetPath != null && targetPath.isNotEmpty) {
          onTargetPath(targetPath);
        }
      });
    } on FirebaseException {
      // The inbox remains available when native messaging is not configured.
    }
  }

  Future<FcmRegistrationState> activate({
    required DeviceRegistrationGateway gateway,
    required String installationId,
  }) async {
    try {
      await _initializeFirebase();
      final FirebaseMessaging messaging = FirebaseMessaging.instance;
      final NotificationSettings settings = await messaging.requestPermission();
      final bool granted =
          settings.authorizationStatus == AuthorizationStatus.authorized ||
          settings.authorizationStatus == AuthorizationStatus.provisional;
      if (!granted) {
        return const FcmRegistrationState(
          available: true,
          permissionGranted: false,
          tokenRegistered: false,
          reason: 'permission_denied',
        );
      }
      final String? token = await messaging.getToken();
      if (token == null || token.isEmpty) {
        return const FcmRegistrationState(
          available: true,
          permissionGranted: true,
          tokenRegistered: false,
          reason: 'token_unavailable',
        );
      }
      await gateway.registerMobilePushToken(
        installationId: installationId,
        fcmToken: token,
      );
      await _tokenRefreshSubscription?.cancel();
      _tokenRefreshSubscription = messaging.onTokenRefresh.listen((
        String refreshed,
      ) {
        unawaited(
          gateway.registerMobilePushToken(
            installationId: installationId,
            fcmToken: refreshed,
          ),
        );
      });
      return const FcmRegistrationState(
        available: true,
        permissionGranted: true,
        tokenRegistered: true,
      );
    } on FirebaseException catch (error) {
      return FcmRegistrationState(
        available: false,
        permissionGranted: false,
        tokenRegistered: false,
        reason: error.code,
      );
    } catch (_) {
      return const FcmRegistrationState(
        available: false,
        permissionGranted: false,
        tokenRegistered: false,
        reason: 'initialization_failed',
      );
    }
  }

  /// Stops the authenticated token-refresh callback when its session ends.
  /// The next explicit Android-notification activation installs a callback for
  /// the newly authenticated tenant/user session.
  Future<void> clearSessionBinding() async {
    await _tokenRefreshSubscription?.cancel();
    _tokenRefreshSubscription = null;
  }

  Future<void> dispose() async {
    await clearSessionBinding();
    await _messageOpenSubscription?.cancel();
  }

  Future<void> _initializeFirebase() async {
    if (Firebase.apps.isEmpty) await Firebase.initializeApp();
  }
}
