import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'fcm_registration_state.dart';
import 'fcm_runtime.dart';

import 'inbox_gateway.dart';

abstract class SecureStoragePort {
  Future<String?> read(String key);
  Future<void> write(String key, String value);
}

class FlutterSecureStoragePort implements SecureStoragePort {
  FlutterSecureStoragePort({FlutterSecureStorage? storage})
    : _storage = storage ?? const FlutterSecureStorage();
  final FlutterSecureStorage _storage;
  @override
  Future<String?> read(String key) => _storage.read(key: key);
  @override
  Future<void> write(String key, String value) =>
      _storage.write(key: key, value: value);
}

/// A random installation identifier is not an account identifier. The API binds it
/// to the current authenticated tenant/user session and remains the authority.
class DeviceRegistration {
  DeviceRegistration({SecureStoragePort? storage})
    : _storage = storage ?? FlutterSecureStoragePort();

  static const String _installationKey = 'kairo.native.installation-id';
  final SecureStoragePort _storage;
  String? _registeredScope;
  final FcmRuntime _fcmRuntime = FcmRuntime();

  Future<String> installationId() async {
    final String? existing = await _storage.read(_installationKey);
    if (existing != null && existing.length >= 16) return existing;
    final Random random = Random.secure();
    final String created = List<String>.generate(
      32,
      (_) => random.nextInt(16).toRadixString(16),
    ).join();
    await _storage.write(_installationKey, created);
    return created;
  }

  Future<void> registerForSession({
    required DeviceRegistrationGateway gateway,
    required String userId,
    required String tenantId,
  }) async {
    final String scope = '$tenantId:$userId';
    if (_registeredScope == scope) return;
    await gateway.registerDevice(
      installationId: await installationId(),
      platform: kIsWeb ? 'flutter_web' : 'android',
    );
    _registeredScope = scope;
  }

  Future<FcmRegistrationState> activatePush({
    required DeviceRegistrationGateway gateway,
  }) async => _fcmRuntime.activate(
    gateway: gateway,
    installationId: await installationId(),
  );

  Future<void> configureNotificationOpens(
    void Function(String targetPath) onTargetPath,
  ) => _fcmRuntime.configureNotificationOpens(onTargetPath);

  Future<void> clearSessionBinding() async {
    _registeredScope = null;
    await _fcmRuntime.clearSessionBinding();
  }
}
