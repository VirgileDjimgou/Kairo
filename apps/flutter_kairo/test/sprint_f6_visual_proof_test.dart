import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/features/chat/data/chat_gateway.dart';
import 'package:kairo_flutter/features/chat/presentation/chat_workspace_page.dart';
import 'package:kairo_flutter/features/notifications/data/inbox_gateway.dart';
import 'package:kairo_flutter/features/notifications/presentation/inbox_page.dart';

void main() {
  testWidgets('F6 proof Android private assistant', (tester) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      MaterialApp(
        home: ChatWorkspacePage(gateway: _Chat(), locale: KairoLocale.fr),
      ),
    );
    await tester.pumpAndSettle();
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f6/android-private-assistant.png'),
    );
  });

  testWidgets('F6 proof Web notification inbox', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      MaterialApp(
        home: InboxPage(gateway: _Inbox(), locale: KairoLocale.fr),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Préférences de notification'));
    await tester.pumpAndSettle();
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f6/web-notification-inbox.png'),
    );
  });
}

class _Chat implements ChatGateway {
  @override
  Future<ChatConversationDetail> conversation(String id) async =>
      const ChatConversationDetail(
        id: 'c1',
        title: 'Règlement',
        messages: <ChatMessage>[],
      );
  @override
  Future<List<ChatConversation>> conversations() async =>
      const <ChatConversation>[
        ChatConversation(
          id: 'c1',
          title: 'Règlement intérieur',
          messageCount: 4,
        ),
      ];
  @override
  Future<ChatConversation> createConversation(String title) async =>
      ChatConversation(id: 'c2', title: title, messageCount: 0);
  @override
  Future<List<String>> domainPolicy() async => const <String>[
    'documents',
    'finance',
  ];
  @override
  Future<ChatReply> query({
    required String question,
    required String locale,
    String? conversationId,
  }) async => throw UnimplementedError();
  @override
  Stream<Map<String, dynamic>> queryStream({
    required String question,
    required String locale,
    String? conversationId,
  }) => const Stream<Map<String, dynamic>>.empty();
}

class _Inbox implements InboxGateway {
  @override
  Future<NotificationInbox> load() async => const NotificationInbox(
    unreadCount: 2,
    items: <InboxNotification>[
      InboxNotification(
        id: 'n1',
        eventType: 'receipt_validated',
        category: 'finance',
        priority: 'high',
        readAt: null,
        createdAt: '2026-08-12 10:30',
        targetPath: '/receipts',
        metadata: <String, dynamic>{
          'message': 'Cotisation validée par le trésorier.',
        },
      ),
      InboxNotification(
        id: 'n2',
        eventType: 'disciplinary_record_created',
        category: 'discipline',
        priority: 'medium',
        readAt: null,
        createdAt: '2026-08-12 09:20',
        targetPath: '/censor',
        metadata: <String, dynamic>{
          'message': 'Un dossier disciplinaire est disponible.',
        },
      ),
    ],
  );
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
