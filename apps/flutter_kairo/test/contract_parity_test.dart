import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/core/api/generated/contracts.dart' as contract;
import 'package:kairo_flutter/features/notifications/data/inbox_gateway.dart';

void main() {
  test('generated notification contract matches the hand-written gateway', () {
    final Map<String, dynamic> itemJson = <String, dynamic>{
      'id': 'notification-1',
      'event_type': 'finance.receipt_validated',
      'category': 'finance',
      'priority': 'high',
      'target_path': '/finance',
      'event_id': 'event-1',
      'correlation_id': 'request-1',
      'metadata': <String, dynamic>{'income_type': 'membership_contribution'},
      'read_at': null,
      'created_at': '2026-09-26T10:00:00Z',
    };
    final contract.InboxResponse inbox =
        contract.InboxResponse.fromJson(<String, dynamic>{
          'items': <dynamic>[itemJson],
          'unread_count': 1,
        });
    final InboxNotification handWritten = InboxNotification.fromJson(itemJson);

    expect(inbox.unread_count, 1);
    expect(inbox.items, hasLength(1));
    expect(inbox.items!.single.id, handWritten.id);
    expect(inbox.items!.single.event_type, handWritten.eventType);
    expect(inbox.items!.single.target_path, handWritten.targetPath);
    expect(inbox.items!.single.event_id, 'event-1');
    expect(inbox.items!.single.correlation_id, 'request-1');
    expect(
      inbox.items!.single.metadata!['income_type'],
      handWritten.metadata['income_type'],
    );
  });

  test('generated contracts cover the sprint 114 notification surface', () {
    final contract.NotificationPreferencesResponse preferences =
        contract.NotificationPreferencesResponse.fromJson(<String, dynamic>{
          'push_enabled': true,
          'finance_enabled': false,
          'discipline_enabled': true,
          'announcements_enabled': true,
          'events_enabled': true,
        });
    expect(preferences.finance_enabled, isFalse);

    final contract.NotificationHealthResponse health =
        contract.NotificationHealthResponse.fromJson(<String, dynamic>{
          'web_push_configured': true,
          'firebase_configured': true,
          'worker_running': true,
          'pending_outbox': 0,
          'failed_outbox': 0,
          'oldest_pending_seconds': null,
          'disabled_web_subscriptions': 0,
          'disabled_fcm_tokens': 0,
          'last_successful_dispatch_at': null,
        });
    expect(health.worker_running, isTrue);

    final contract.NotificationDeviceRevocationResponse revocation =
        contract.NotificationDeviceRevocationResponse.fromJson(
          <String, dynamic>{
            'revoked_profiles': 1,
            'disabled_web_subscriptions': 1,
            'disabled_fcm_tokens': 0,
          },
        );
    expect(revocation.revoked_profiles, 1);

    for (final String operation in <String>[
      'GET /api/v1/notifications/inbox',
      'POST /api/v1/notifications/inbox/{notification_id}/read',
      'POST /api/v1/notifications/inbox/read-all',
      'GET /api/v1/notifications/preferences',
      'PUT /api/v1/notifications/preferences',
      'GET /api/v1/notifications/push/configuration',
      'POST /api/v1/notifications/devices',
      'POST /api/v1/notifications/devices/{installation_id}/revoke',
      'POST /api/v1/notifications/push-subscriptions',
      'POST /api/v1/notifications/mobile-push-tokens',
      'GET /api/v1/notifications/health',
    ]) {
      expect(
        contract.apiOperationIds.containsKey(operation),
        isTrue,
        reason: 'missing generated operation: $operation',
      );
    }
  });
}
