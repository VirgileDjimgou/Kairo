import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/features/governance/data/governance_gateway.dart';
import 'package:kairo_flutter/features/governance/presentation/governance_workspace_page.dart';
import 'package:kairo_flutter/features/members/data/member_gateway.dart';
import 'package:kairo_flutter/features/members/data/member_models.dart';
import 'package:kairo_flutter/features/notifications/data/fcm_registration_state.dart';
import 'package:kairo_flutter/features/notifications/data/inbox_gateway.dart';
import 'package:kairo_flutter/features/notifications/presentation/inbox_page.dart';

void main() {
  testWidgets('F8 proof Android secretary document import capability', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      MaterialApp(
        home: GovernanceWorkspacePage(
          gateway: _Gateway(),
          memberGateway: _Members(),
          locale: KairoLocale.fr,
          roles: const <String>['secretary_general'],
        ),
      ),
    );
    await tester.pumpAndSettle();
    final Finder documentsTab = find.text('Documents');
    await tester.ensureVisible(documentsTab);
    await tester.tap(documentsTab);
    await tester.pumpAndSettle();
    expect(find.text('Importer un document'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile(
        '../artifacts/sprint-f8/android-secretary-document-import.png',
      ),
    );
  });

  testWidgets('F8 proof Android native notification activation', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      MaterialApp(
        home: InboxPage(
          gateway: _Inbox(),
          locale: KairoLocale.fr,
          onEnableAndroidPush: () async => const FcmRegistrationState(
            available: true,
            permissionGranted: true,
            tokenRegistered: true,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Activer les notifications Android'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile(
        '../artifacts/sprint-f8/android-notification-activation.png',
      ),
    );
  });
}

class _Gateway implements GovernanceGateway, DocumentUploadGateway {
  @override
  Future<List<GovernanceItem>> announcements() async =>
      const <GovernanceItem>[];
  @override
  Future<BackupOverview> backupOverview() async => const BackupOverview(
    automatic: true,
    retention: 14,
    externalStorage: true,
    pitr: false,
    lastSuccess: null,
    runCount: 1,
  );
  @override
  Future<DisciplineRecord> createDiscipline(Map<String, dynamic> data) async =>
      throw UnimplementedError();
  @override
  Future<List<DisciplineRecord>> discipline({required bool ownOnly}) async =>
      const <DisciplineRecord>[];
  @override
  Future<List<GovernanceItem>> documents() async => const <GovernanceItem>[
    GovernanceItem(
      id: 'document-1',
      title: 'Règlement intérieur',
      body: 'Document officiel de l’association',
      meta: 'tenant_public',
      status: 'published',
    ),
  ];
  @override
  Future<List<GovernanceItem>> events() async => const <GovernanceItem>[];
  @override
  Future<List<GovernanceItem>> policies() async => const <GovernanceItem>[];
  @override
  Future<void> requestBackup(String? reason) async {}
  @override
  Future<GovernanceItem> uploadDocument({
    required String filename,
    required List<int> bytes,
    required String title,
  }) async => GovernanceItem(
    id: 'document-2',
    title: title,
    body: '',
    meta: 'tenant_public',
    status: 'uploaded',
  );
}

class _Members implements MemberGateway {
  @override
  Future<MemberProfile> create(MemberDraft draft) async =>
      throw UnimplementedError();
  @override
  Future<List<MemberProfile>> list({String? query}) async =>
      const <MemberProfile>[];
  @override
  Future<MemberProfile> update(String id, Map<String, dynamic> patch) async =>
      throw UnimplementedError();
}

class _Inbox implements InboxGateway {
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
