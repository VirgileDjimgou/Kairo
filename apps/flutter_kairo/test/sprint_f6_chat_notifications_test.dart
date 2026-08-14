import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/core/api/kairo_api_client.dart';
import 'package:kairo_flutter/features/chat/data/chat_gateway.dart';
import 'package:kairo_flutter/features/chat/presentation/chat_workspace_page.dart';
import 'package:kairo_flutter/features/notifications/data/inbox_gateway.dart';
import 'package:kairo_flutter/features/notifications/presentation/inbox_page.dart';

void main() {
  testWidgets('assistant streams a grounded answer with citations', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChatWorkspacePage(
          gateway: _ChatGateway(),
          locale: KairoLocale.fr,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), 'Quel est le règlement ?');
    await tester.tap(find.byIcon(Icons.send));
    await tester.pumpAndSettle();
    expect(find.text('Le règlement est disponible.'), findsOneWidget);
    expect(find.text('Règlement intérieur'), findsOneWidget);
  });

  testWidgets('assistant clearly reports disabled state', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChatWorkspacePage(
          gateway: _FailingChatGateway(403),
          locale: KairoLocale.fr,
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Assistant IA désactivé'), findsOneWidget);
  });

  testWidgets('assistant clearly reports unavailable state', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChatWorkspacePage(
          gateway: _FailingChatGateway(503),
          locale: KairoLocale.fr,
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Assistant temporairement indisponible'), findsOneWidget);
  });

  testWidgets('inbox stores preferences and opens a notification target', (
    tester,
  ) async {
    final gateway = _InboxGateway();
    String? path;
    await tester.pumpWidget(
      MaterialApp(
        home: InboxPage(
          gateway: gateway,
          locale: KairoLocale.fr,
          onOpenTarget: (value) => path = value,
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Préférences de notification'), findsOneWidget);
    await tester.tap(find.text('Préférences de notification'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Finances'));
    await tester.pumpAndSettle();
    expect(gateway.values.financeEnabled, isFalse);
    await tester.tap(find.text('Encaissement validé'));
    await tester.pumpAndSettle();
    expect(path, '/receipts');
  });
}

class _ChatGateway implements ChatGateway {
  @override
  Future<ChatConversationDetail> conversation(String id) async =>
      const ChatConversationDetail(
        id: 'conversation-1',
        title: 'Règlement',
        messages: <ChatMessage>[],
      );
  @override
  Future<List<ChatConversation>> conversations() async =>
      const <ChatConversation>[
        ChatConversation(
          id: 'conversation-1',
          title: 'Règlement',
          messageCount: 1,
        ),
      ];
  @override
  Future<ChatConversation> createConversation(String title) async =>
      ChatConversation(id: 'conversation-2', title: title, messageCount: 0);
  @override
  Future<List<String>> domainPolicy() async => const <String>['documents'];
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
  }) async* {
    yield <String, dynamic>{
      'type': 'token',
      'content': 'Le règlement est disponible.',
    };
    yield <String, dynamic>{
      'type': 'done',
      'conversation_id': 'conversation-1',
      'citations': <Map<String, dynamic>>[
        <String, dynamic>{
          'document_title': 'Règlement intérieur',
          'excerpt': 'Les membres respectent le règlement.',
          'score': 0.93,
        },
      ],
    };
  }
}

class _FailingChatGateway implements ChatGateway {
  const _FailingChatGateway(this.statusCode);
  final int statusCode;
  KairoApiException get _error =>
      KairoApiException(statusCode: statusCode, message: 'Unavailable');
  @override
  Future<ChatConversationDetail> conversation(String id) async => throw _error;
  @override
  Future<List<ChatConversation>> conversations() async => throw _error;
  @override
  Future<ChatConversation> createConversation(String title) async =>
      throw _error;
  @override
  Future<List<String>> domainPolicy() async => throw _error;
  @override
  Future<ChatReply> query({
    required String question,
    required String locale,
    String? conversationId,
  }) async => throw _error;
  @override
  Stream<Map<String, dynamic>> queryStream({
    required String question,
    required String locale,
    String? conversationId,
  }) => Stream<Map<String, dynamic>>.error(_error);
}

class _InboxGateway implements InboxGateway {
  NotificationPreferences values = const NotificationPreferences(
    pushEnabled: true,
    financeEnabled: true,
    disciplineEnabled: true,
    announcementsEnabled: true,
    eventsEnabled: true,
  );
  @override
  Future<NotificationInbox> load() async => const NotificationInbox(
    unreadCount: 1,
    items: <InboxNotification>[
      InboxNotification(
        id: 'notice-1',
        eventType: 'receipt_validated',
        category: 'finance',
        priority: 'high',
        readAt: null,
        createdAt: '2026-08-12 10:30',
        targetPath: '/receipts',
        metadata: <String, dynamic>{'message': 'La cotisation a été validée.'},
      ),
    ],
  );
  @override
  Future<void> markAllRead() async {}
  @override
  Future<void> markRead(String id) async {}
  @override
  Future<NotificationPreferences> preferences() async => values;
  @override
  Future<NotificationPreferences> updatePreferences(
    NotificationPreferences next,
  ) async {
    values = next;
    return values;
  }
}
