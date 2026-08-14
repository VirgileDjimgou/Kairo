import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/features/notifications/data/device_registration.dart';
import 'package:kairo_flutter/features/notifications/data/inbox_gateway.dart';

void main() {
  test(
    'device registration uses one installation id and scopes registration per session',
    () async {
      final storage = _Storage();
      final gateway = _Inbox();
      final registration = DeviceRegistration(storage: storage);

      await registration.registerForSession(
        gateway: gateway,
        tenantId: 'tenant-a',
        userId: 'user-a',
      );
      await registration.registerForSession(
        gateway: gateway,
        tenantId: 'tenant-a',
        userId: 'user-a',
      );
      await registration.registerForSession(
        gateway: gateway,
        tenantId: 'tenant-a',
        userId: 'user-b',
      );
      await registration.clearSessionBinding();
      await registration.registerForSession(
        gateway: gateway,
        tenantId: 'tenant-a',
        userId: 'user-b',
      );

      expect(gateway.installations, hasLength(3));
      expect(gateway.installations.toSet(), hasLength(1));
      expect(gateway.installations.first.length, greaterThanOrEqualTo(16));
    },
  );
}

class _Storage implements SecureStoragePort {
  final Map<String, String> values = <String, String>{};
  @override
  Future<String?> read(String key) async => values[key];
  @override
  Future<void> write(String key, String value) async => values[key] = value;
}

class _Inbox implements InboxGateway, DeviceRegistrationGateway {
  final List<String> installations = <String>[];
  @override
  Future<void> registerDevice({
    required String installationId,
    required String platform,
  }) async => installations.add(installationId);
  @override
  Future<void> registerMobilePushToken({
    required String installationId,
    required String fcmToken,
  }) async {}
  @override
  Future<NotificationInbox> load() async =>
      const NotificationInbox(items: <InboxNotification>[], unreadCount: 0);
  @override
  Future<void> markAllRead() async {}
  @override
  Future<void> markRead(String id) async {}
  @override
  Future<NotificationPreferences> preferences() async =>
      const NotificationPreferences(
        pushEnabled: true,
        financeEnabled: true,
        disciplineEnabled: true,
        announcementsEnabled: true,
        eventsEnabled: true,
      );
  @override
  Future<NotificationPreferences> updatePreferences(
    NotificationPreferences values,
  ) async => values;
}
