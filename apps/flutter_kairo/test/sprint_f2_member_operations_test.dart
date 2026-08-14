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
import 'package:kairo_flutter/features/members/presentation/member_directory_page.dart';
import 'package:kairo_flutter/features/notifications/data/inbox_gateway.dart';

void main() {
  test(
    'member controller scopes search and updates only the returned member',
    () async {
      final _FakeMemberGateway gateway = _FakeMemberGateway();
      final MemberController controller = MemberController(gateway: gateway);

      await controller.load(query: 'ali');
      expect(gateway.lastQuery, 'ali');
      expect(controller.members.single.displayName, 'Alice Martin');

      final bool saved = await controller.changeStatus(
        controller.members.single,
        'paused',
      );
      expect(saved, isTrue);
      expect(controller.selected?.status, 'paused');
    },
  );

  testWidgets(
    'president sees member navigation and can open the directory on phone',
    (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final MemberController controller = MemberController(
        gateway: _FakeMemberGateway(),
      );
      await tester.pumpWidget(
        MaterialApp(
          home: RoleShell(
            environment: KairoEnvironment.fromValues(
              flavor: 'development',
              apiBaseUrl: '',
            ),
            locale: KairoLocale.fr,
            onLocaleChanged: (_) {},
            user: const KairoUser(
              id: 'president',
              email: 'president@test.org',
              displayName: 'Président Test',
              tenantId: 'tenant-a',
              roles: <String>['president'],
              passwordChangeRequired: false,
              memberships: <TenantMembership>[],
            ),
            onSignOut: () async {},
            onAccountSecurity: () {},
            memberController: controller,
            receiptGateway: _FakeReceiptGateway(),
            receiptController: ReceiptController(
              gateway: _FakeReceiptGateway(),
            ),
            memberStatementGateway: _FakeStatementGateway(),
            inboxGateway: _FakeInboxGateway(),
            operationJournalGateway: _FakeJournalGateway(),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Bon retour, Président Test'), findsOneWidget);
      expect(find.byType(NavigationDestination), findsNWidgets(5));
      expect(find.text('Plus'), findsOneWidget);
      await tester.tap(find.text('Membres'));
      await tester.pumpAndSettle();
      expect(find.byType(MemberDirectoryPage), findsOneWidget);
      expect(find.text('Ajouter un membre'), findsOneWidget);

      await tester.tap(find.text('Plus'));
      await tester.pumpAndSettle();
      expect(find.text('Tous les espaces'), findsOneWidget);
      expect(find.text('Journal'), findsOneWidget);
      expect(find.text('Cotisations'), findsOneWidget);
    },
  );

  testWidgets('ordinary member does not receive directory navigation', (
    WidgetTester tester,
  ) async {
    final MemberController controller = MemberController(
      gateway: _FakeMemberGateway(),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: RoleShell(
          environment: KairoEnvironment.fromValues(
            flavor: 'development',
            apiBaseUrl: '',
          ),
          locale: KairoLocale.fr,
          onLocaleChanged: (_) {},
          user: const KairoUser(
            id: 'member',
            email: 'member@test.org',
            displayName: 'Membre Test',
            tenantId: 'tenant-a',
            roles: <String>['member'],
            passwordChangeRequired: false,
            memberships: <TenantMembership>[],
          ),
          onSignOut: () async {},
          onAccountSecurity: () {},
          memberController: controller,
          receiptGateway: _FakeReceiptGateway(),
          receiptController: ReceiptController(gateway: _FakeReceiptGateway()),
          memberStatementGateway: _FakeStatementGateway(),
          inboxGateway: _FakeInboxGateway(),
          operationJournalGateway: _FakeJournalGateway(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Membres'), findsNothing);
    expect(find.text('Encaissements'), findsNothing);
    expect(find.text('Journal'), findsNothing);
    expect(find.text('Cotisations'), findsOneWidget);
  });
}

class _FakeReceiptGateway implements ReceiptGateway {
  @override
  Future<ReceiptDeclaration> confirmTreasury(
    String id,
    Map<String, dynamic> payload,
  ) async => _receipt;
  @override
  Future<ReceiptDeclaration> create(Map<String, dynamic> draft) async =>
      _receipt;
  @override
  Future<List<ReceiptMemberOption>> memberOptions({String? query}) async =>
      const <ReceiptMemberOption>[];
  @override
  Future<List<ReceiptDeclaration>> mine() async => const <ReceiptDeclaration>[];
  @override
  Future<ReceiptDeclaration> process(
    String id,
    Map<String, dynamic> payload,
  ) async => _receipt;
  @override
  Future<List<ReceiptDeclaration>> review() async =>
      const <ReceiptDeclaration>[];
  @override
  Future<ReceiptDeclaration> submit(String id) async => _receipt;
  @override
  Future<ReceiptDeclaration> updateReminder(
    String id,
    Map<String, dynamic> payload,
  ) async => _receipt;
  static const ReceiptDeclaration _receipt = ReceiptDeclaration(
    id: 'receipt-1',
    amount: '20.00',
    status: 'submitted',
    incomeType: 'donation',
  );
}

class _FakeStatementGateway implements MemberStatementGateway {
  @override
  Future<MemberStatement> mine() async => const MemberStatement(
    displayName: 'Alice Martin',
    memberCode: 'ALI-COMBIS-1001',
    totalExpected: '60.00',
    totalPaid: '20.00',
    totalBalance: '40.00',
    contributions: <MemberContribution>[],
  );
}

class _FakeInboxGateway implements InboxGateway {
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

class _FakeJournalGateway implements OperationJournalGateway {
  @override
  Future<List<OperationJournalEntry>> load({String? search}) async =>
      const <OperationJournalEntry>[];
}

class _FakeMemberGateway implements MemberGateway {
  String? lastQuery;
  MemberProfile member = const MemberProfile(
    id: 'member-1',
    memberCode: 'ALI-COMBIS-1001',
    firstName: 'Alice',
    lastName: 'Martin',
    displayName: 'Alice Martin',
    email: 'alice@combis.org',
    status: 'active',
    membershipType: 'individual',
    joinedAt: null,
  );
  @override
  Future<MemberProfile> create(MemberDraft draft) async => member;
  @override
  Future<List<MemberProfile>> list({String? query}) async {
    lastQuery = query;
    return <MemberProfile>[member];
  }

  @override
  Future<MemberProfile> update(String id, Map<String, dynamic> patch) async {
    member = MemberProfile(
      id: member.id,
      memberCode: member.memberCode,
      firstName: member.firstName,
      lastName: member.lastName,
      displayName: member.displayName,
      email: member.email,
      status: patch['status'] as String? ?? member.status,
      membershipType: member.membershipType,
      joinedAt: member.joinedAt,
    );
    return member;
  }
}
