import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class OfflineScope {
  const OfflineScope({required this.userId, required this.tenantId});

  final String userId;
  final String tenantId;

  String get key => '${_safe(userId)}.${_safe(tenantId)}';

  static String _safe(String value) =>
      base64Url.encode(utf8.encode(value)).replaceAll('=', '');
}

class PendingOfflineCommand {
  const PendingOfflineCommand({
    required this.idempotencyKey,
    required this.kind,
    required this.createdAt,
  });

  factory PendingOfflineCommand.fromJson(Map<String, dynamic> json) =>
      PendingOfflineCommand(
        idempotencyKey: json['idempotency_key'] as String,
        kind: json['kind'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  final String idempotencyKey;
  final String kind;
  final DateTime createdAt;

  Map<String, dynamic> toJson() => <String, dynamic>{
    'idempotency_key': idempotencyKey,
    'kind': kind,
    'created_at': createdAt.toIso8601String(),
  };
}

/// Secure, identity-scoped local state. The platform secure keystore encrypts this
/// data where supported; Flutter Web intentionally treats it as a device-local cache.
abstract interface class OfflineStorage {
  Future<void> delete({required String key});
  Future<void> write({required String key, required String? value});
  Future<String?> read({required String key});
  Future<Map<String, String>> readAll();
}

class SecureOfflineStorage implements OfflineStorage {
  SecureOfflineStorage({FlutterSecureStorage? storage})
    : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  @override
  Future<void> delete({required String key}) => _storage.delete(key: key);

  @override
  Future<Map<String, String>> readAll() => _storage.readAll();

  @override
  Future<String?> read({required String key}) => _storage.read(key: key);

  @override
  Future<void> write({required String key, required String? value}) =>
      _storage.write(key: key, value: value);
}

class OfflineWorkspaceController extends ChangeNotifier {
  OfflineWorkspaceController({OfflineStorage? storage})
    : _storage = storage ?? SecureOfflineStorage();

  final OfflineStorage _storage;
  OfflineScope? _scope;
  bool isOnline = true;
  DateTime? lastSynchronizedAt;
  List<PendingOfflineCommand> pendingCommands = const <PendingOfflineCommand>[];

  String? get scopeKey => _scope?.key;
  bool get hasScope => _scope != null;

  Future<void> activate(OfflineScope scope) async {
    if (_scope?.key == scope.key) return;
    _scope = scope;
    isOnline = true;
    lastSynchronizedAt = null;
    pendingCommands = const <PendingOfflineCommand>[];
    try {
      await _restoreMetadata();
    } catch (_) {
      pendingCommands = const <PendingOfflineCommand>[];
    }
    notifyListeners();
  }

  void reportConnectivity(bool online) {
    if (isOnline == online && (online || lastSynchronizedAt != null)) return;
    isOnline = online;
    if (online) lastSynchronizedAt = DateTime.now();
    _writeMetadata();
    notifyListeners();
  }

  Future<void> saveDraft(String area, Map<String, dynamic> values) async {
    final key = _key('draft.$area');
    if (key == null) return;
    try {
      await _storage.write(key: key, value: jsonEncode(values));
    } catch (_) {
      return;
    }
    _queueDraft(area);
  }

  Future<Map<String, dynamic>?> readDraft(String area) async {
    final key = _key('draft.$area');
    if (key == null) return null;
    String? raw;
    try {
      raw = await _storage.read(key: key);
    } catch (_) {
      return null;
    }
    if (raw == null) return null;
    try {
      final value = jsonDecode(raw);
      return value is Map<String, dynamic> ? value : null;
    } on FormatException {
      return null;
    }
  }

  Future<void> clearDraft(String area) async {
    final key = _key('draft.$area');
    if (key == null) return;
    try {
      await _storage.delete(key: key);
    } catch (_) {
      return;
    }
    pendingCommands = pendingCommands
        .where((item) => item.kind != 'draft:$area')
        .toList();
    await _writeMetadata();
    notifyListeners();
  }

  Future<void> cacheRead(String cacheKey, Object? payload) async {
    final key = _key('cache.$cacheKey');
    if (key == null) return;
    try {
      await _storage.write(key: key, value: jsonEncode(payload));
    } catch (_) {
      return;
    }
    reportConnectivity(true);
  }

  Future<Object?> readCached(String cacheKey) async {
    final key = _key('cache.$cacheKey');
    if (key == null) return null;
    String? raw;
    try {
      raw = await _storage.read(key: key);
    } catch (_) {
      return null;
    }
    if (raw == null) return null;
    try {
      return jsonDecode(raw);
    } on FormatException {
      return null;
    }
  }

  Future<void> clearCurrentScope() async {
    final scope = _scope;
    if (scope == null) return;
    final prefix = 'kairo.offline.${scope.key}.';
    try {
      final all = await _storage.readAll();
      await Future.wait<void>(
        all.keys
            .where((key) => key.startsWith(prefix))
            .map((key) => _storage.delete(key: key)),
      );
    } catch (_) {
      // Session safety must not depend on a temporarily unavailable keystore.
    }
    _scope = null;
    pendingCommands = const <PendingOfflineCommand>[];
    lastSynchronizedAt = null;
    notifyListeners();
  }

  void _queueDraft(String area) {
    final existing = pendingCommands
        .where((item) => item.kind != 'draft:$area')
        .toList();
    pendingCommands = <PendingOfflineCommand>[
      ...existing,
      PendingOfflineCommand(
        idempotencyKey: '${DateTime.now().microsecondsSinceEpoch}-$area',
        kind: 'draft:$area',
        createdAt: DateTime.now(),
      ),
    ];
    _writeMetadata();
    notifyListeners();
  }

  Future<void> _restoreMetadata() async {
    final raw = await _storage.read(key: _key('metadata')!);
    if (raw == null) return;
    try {
      final json = jsonDecode(raw) as Map<String, dynamic>;
      final timestamp = json['last_synchronized_at'] as String?;
      lastSynchronizedAt = timestamp == null
          ? null
          : DateTime.tryParse(timestamp);
      pendingCommands =
          (json['pending_commands'] as List<dynamic>? ?? const <dynamic>[])
              .cast<Map<String, dynamic>>()
              .map(PendingOfflineCommand.fromJson)
              .toList();
    } on FormatException {
      pendingCommands = const <PendingOfflineCommand>[];
    }
  }

  Future<void> _writeMetadata() async {
    final key = _key('metadata');
    if (key == null) return;
    try {
      await _storage.write(
        key: key,
        value: jsonEncode(<String, dynamic>{
          'last_synchronized_at': lastSynchronizedAt?.toIso8601String(),
          'pending_commands': pendingCommands
              .map((item) => item.toJson())
              .toList(),
        }),
      );
    } catch (_) {
      // Draft state remains in memory until a secure store is available.
    }
  }

  String? _key(String suffix) =>
      _scope == null ? null : 'kairo.offline.${_scope!.key}.$suffix';
}
