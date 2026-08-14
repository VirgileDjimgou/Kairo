import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/app_environment.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/features/auth/data/auth_models.dart';
import 'package:kairo_flutter/features/finance/data/member_statement_gateway.dart';
import 'package:kairo_flutter/features/finance/data/receipt_gateway.dart';
import 'package:kairo_flutter/features/finance/presentation/receipt_controller.dart';
import 'package:kairo_flutter/features/foundation/presentation/role_shell.dart';
import 'package:kairo_flutter/features/governance/data/operation_journal_gateway.dart';
import 'package:kairo_flutter/features/members/data/member_gateway.dart';
import 'package:kairo_flutter/features/members/data/member_models.dart';
import 'package:kairo_flutter/features/members/presentation/member_controller.dart';
import 'package:kairo_flutter/features/notifications/data/inbox_gateway.dart';

void main() {
  testWidgets('F3 proof member contribution statement on Android width', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(_shell(const <String>['member']));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Cotisations'));
    await tester.pumpAndSettle();
    expect(find.text('Mes cotisations'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile(
        '../artifacts/sprint-f3/member-android-contributions.png',
      ),
    );
  });

  testWidgets('F3 proof treasurer custody on Web width', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(_shell(const <String>['treasurer']));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Encaissements'));
    await tester.pumpAndSettle();
    expect(find.text('Validation de trésorerie'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f3/treasurer-web-custody.png'),
    );
  });

  testWidgets('F3 proof president journal and notifications on Android width', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(_shell(const <String>['president']));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Plus'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Journal'));
    await tester.pumpAndSettle();
    expect(find.text('Journal des opérations'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f3/president-android-journal.png'),
    );
  });
}

Widget _shell(List<String> roles) => MaterialApp(
  home: RoleShell(
    environment: KairoEnvironment.fromValues(
      flavor: 'development',
      apiBaseUrl: '',
    ),
    locale: KairoLocale.fr,
    onLocaleChanged: (_) {},
    user: KairoUser(
      id: roles.first,
      email: '${roles.first}@test.org',
      displayName: roles.first == 'member' ? 'Membre Test' : 'Trésorier Test',
      tenantId: 'tenant-a',
      roles: roles,
      passwordChangeRequired: false,
      memberships: const <TenantMembership>[],
    ),
    onSignOut: () async {},
    onAccountSecurity: () {},
    memberController: MemberController(gateway: _MemberGateway()),
    receiptGateway: _ReceiptGateway(),
    receiptController: ReceiptController(gateway: _ReceiptGateway()),
    memberStatementGateway: _StatementGateway(),
    inboxGateway: _InboxGateway(),
    operationJournalGateway: _JournalGateway(),
  ),
);

class _StatementGateway implements MemberStatementGateway {
  @override
  Future<MemberStatement> mine() async => const MemberStatement(
    displayName: 'Mireille Tchoumi',
    memberCode: 'MIR-COMBIS-0041',
    totalExpected: '60.00',
    totalPaid: '20.00',
    totalBalance: '40.00',
    contributions: <MemberContribution>[
      MemberContribution(
        year: '2026',
        expectedAmount: '60.00',
        paidAmount: '20.00',
        balanceAmount: '40.00',
        status: 'partial',
      ),
    ],
  );
}

class _ReceiptGateway implements ReceiptGateway {
  static const ReceiptDeclaration item = ReceiptDeclaration(
    id: 'receipt-1',
    amount: '60.00',
    status: 'validated',
    incomeType: 'membership_contribution',
    sourceName: 'Mireille Tchoumi',
    note: 'Cotisation reçue en espèces',
    cashHandoverStatus: 'pending_handover',
    handoverReminderDays: 2,
  );
  @override
  Future<ReceiptDeclaration> confirmTreasury(
    String id,
    Map<String, dynamic> payload,
  ) async => item;
  @override
  Future<ReceiptDeclaration> create(Map<String, dynamic> draft) async => item;
  @override
  Future<List<ReceiptMemberOption>> memberOptions({String? query}) async =>
      const <ReceiptMemberOption>[];
  @override
  Future<List<ReceiptDeclaration>> mine() async => <ReceiptDeclaration>[item];
  @override
  Future<ReceiptDeclaration> process(
    String id,
    Map<String, dynamic> payload,
  ) async => item;
  @override
  Future<List<ReceiptDeclaration>> review() async => <ReceiptDeclaration>[item];
  @override
  Future<ReceiptDeclaration> submit(String id) async => item;
  @override
  Future<ReceiptDeclaration> updateReminder(
    String id,
    Map<String, dynamic> payload,
  ) async => item;
}

class _InboxGateway implements InboxGateway {
  @override
  Future<NotificationInbox> load() async => const NotificationInbox(
    unreadCount: 1,
    items: <InboxNotification>[
      InboxNotification(
        id: 'notice-1',
        eventType: 'receipt_validated',
        category: 'finance',
        priority: 'normal',
        readAt: null,
        createdAt: '2026-08-12 10:30',
        targetPath: '/receipts',
        metadata: <String, dynamic>{
          'message': 'La cotisation a été validée par le trésorier.',
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

class _JournalGateway implements OperationJournalGateway {
  @override
  Future<List<OperationJournalEntry>> load({String? search}) async =>
      const <OperationJournalEntry>[
        OperationJournalEntry(
          action: 'receipt_validated',
          entityType: 'receipt',
          createdAt: '2026-08-12 10:30',
          actorName: 'Jean Paul Fouda',
          actorRoles: <String>['treasurer'],
          details: <String, dynamic>{
            'member': 'Mireille Tchoumi',
            'amount': '60.00 EUR',
            'result': 'validated',
          },
        ),
      ];
}

class _MemberGateway implements MemberGateway {
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
