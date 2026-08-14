import '../../../core/api/kairo_api_client.dart';

class InboxNotification {
  const InboxNotification({
    required this.id,
    required this.eventType,
    required this.category,
    required this.priority,
    required this.readAt,
    required this.createdAt,
    required this.targetPath,
    required this.metadata,
  });
  factory InboxNotification.fromJson(Map<String, dynamic> json) =>
      InboxNotification(
        id: json['id'] as String,
        eventType: json['event_type'] as String,
        category: json['category'] as String,
        priority: json['priority'] as String,
        readAt: json['read_at'] as String?,
        createdAt: json['created_at'] as String,
        targetPath: json['target_path'] as String,
        metadata:
            (json['metadata'] as Map<String, dynamic>? ??
            const <String, dynamic>{}),
      );
  final String id;
  final String eventType;
  final String category;
  final String priority;
  final String? readAt;
  final String createdAt;
  final String targetPath;
  final Map<String, dynamic> metadata;
}

class NotificationPreferences {
  const NotificationPreferences({
    required this.pushEnabled,
    required this.financeEnabled,
    required this.disciplineEnabled,
    required this.announcementsEnabled,
    required this.eventsEnabled,
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) =>
      NotificationPreferences(
        pushEnabled: json['push_enabled'] as bool? ?? true,
        financeEnabled: json['finance_enabled'] as bool? ?? true,
        disciplineEnabled: json['discipline_enabled'] as bool? ?? true,
        announcementsEnabled: json['announcements_enabled'] as bool? ?? true,
        eventsEnabled: json['events_enabled'] as bool? ?? true,
      );

  final bool pushEnabled;
  final bool financeEnabled;
  final bool disciplineEnabled;
  final bool announcementsEnabled;
  final bool eventsEnabled;

  NotificationPreferences copyWith({
    bool? pushEnabled,
    bool? financeEnabled,
    bool? disciplineEnabled,
    bool? announcementsEnabled,
    bool? eventsEnabled,
  }) => NotificationPreferences(
    pushEnabled: pushEnabled ?? this.pushEnabled,
    financeEnabled: financeEnabled ?? this.financeEnabled,
    disciplineEnabled: disciplineEnabled ?? this.disciplineEnabled,
    announcementsEnabled: announcementsEnabled ?? this.announcementsEnabled,
    eventsEnabled: eventsEnabled ?? this.eventsEnabled,
  );

  Map<String, dynamic> toJson() => <String, dynamic>{
    'push_enabled': pushEnabled,
    'finance_enabled': financeEnabled,
    'discipline_enabled': disciplineEnabled,
    'announcements_enabled': announcementsEnabled,
    'events_enabled': eventsEnabled,
  };
}

class NotificationInbox {
  const NotificationInbox({required this.items, required this.unreadCount});
  factory NotificationInbox.fromJson(Map<String, dynamic> json) =>
      NotificationInbox(
        items: (json['items'] as List<dynamic>)
            .map(
              (dynamic value) =>
                  InboxNotification.fromJson(value as Map<String, dynamic>),
            )
            .toList(),
        unreadCount: json['unread_count'] as int,
      );
  final List<InboxNotification> items;
  final int unreadCount;
}

abstract class InboxGateway {
  Future<NotificationInbox> load();
  Future<void> markRead(String id);
  Future<void> markAllRead();
  Future<NotificationPreferences> preferences();
  Future<NotificationPreferences> updatePreferences(
    NotificationPreferences values,
  );
}

abstract class DeviceRegistrationGateway {
  Future<void> registerDevice({
    required String installationId,
    required String platform,
  });
  Future<void> registerMobilePushToken({
    required String installationId,
    required String fcmToken,
  });
}

class HttpInboxGateway implements InboxGateway, DeviceRegistrationGateway {
  const HttpInboxGateway(this._client);
  final KairoApiClient _client;
  @override
  Future<NotificationInbox> load() async => NotificationInbox.fromJson(
    await _client.requestJson('GET', 'notifications/inbox')
        as Map<String, dynamic>,
  );
  @override
  Future<void> markRead(String id) async {
    await _client.requestJson('POST', 'notifications/inbox/$id/read');
  }

  @override
  Future<void> markAllRead() async {
    await _client.requestJson('POST', 'notifications/inbox/read-all');
  }

  @override
  Future<NotificationPreferences> preferences() async =>
      NotificationPreferences.fromJson(
        await _client.getJson('notifications/preferences'),
      );

  @override
  Future<NotificationPreferences> updatePreferences(
    NotificationPreferences values,
  ) async => NotificationPreferences.fromJson(
    await _client.requestJson(
          'PUT',
          'notifications/preferences',
          body: values.toJson(),
        )
        as Map<String, dynamic>,
  );

  @override
  Future<void> registerDevice({
    required String installationId,
    required String platform,
  }) async {
    await _client.requestJson(
      'POST',
      'notifications/devices',
      body: <String, dynamic>{
        'installation_id': installationId,
        'platform': platform,
      },
    );
  }

  @override
  Future<void> registerMobilePushToken({
    required String installationId,
    required String fcmToken,
  }) async {
    await _client.requestJson(
      'POST',
      'notifications/mobile-push-tokens',
      body: <String, dynamic>{
        'installation_id': installationId,
        'fcm_token': fcmToken,
      },
    );
  }
}
