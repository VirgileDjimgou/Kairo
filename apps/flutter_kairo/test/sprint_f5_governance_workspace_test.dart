import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/features/governance/data/governance_gateway.dart';
import 'package:kairo_flutter/features/governance/presentation/governance_workspace_page.dart';
import 'package:kairo_flutter/features/members/data/member_gateway.dart';
import 'package:kairo_flutter/features/members/data/member_models.dart';

void main() {
  testWidgets('censor can create a disciplinary record', (
    WidgetTester tester,
  ) async {
    final gateway = _GovernanceGateway();
    await tester.pumpWidget(
      MaterialApp(
        home: GovernanceWorkspacePage(
          gateway: gateway,
          memberGateway: _MemberGateway(),
          locale: KairoLocale.fr,
          roles: const <String>['censor'],
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Dossiers disciplinaires'), findsOneWidget);
    await tester.enterText(find.byType(TextField).first, 'Ari');
    await tester.pumpAndSettle();
    await tester.tap(find.text('Arlette Ndzi'));
    await tester.enterText(find.byType(TextField).at(1), 'Retard répété');
    await tester.enterText(find.byType(TextField).at(2), 'Après entraînement');
    await tester.enterText(find.byType(TextField).at(3), '20');
    await tester.tap(find.text('Créer le dossier disciplinaire'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmer').last);
    await tester.pumpAndSettle();
    expect(gateway.created, isTrue);
  });

  testWidgets(
    'president sees disciplinary records read-only and backup centre',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: GovernanceWorkspacePage(
            gateway: _GovernanceGateway(),
            memberGateway: _MemberGateway(),
            locale: KairoLocale.fr,
            roles: const <String>['president'],
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Mon historique disciplinaire'), findsOneWidget);
      expect(find.text('Créer le dossier disciplinaire'), findsNothing);
      await tester.tap(find.text('Annonces'));
      await tester.pumpAndSettle();
      expect(find.text('Centre de sauvegarde'), findsOneWidget);
    },
  );
}

class _GovernanceGateway implements GovernanceGateway {
  bool created = false;
  @override
  Future<BackupOverview> backupOverview() async => const BackupOverview(
    automatic: true,
    retention: 30,
    externalStorage: true,
    pitr: true,
    lastSuccess: null,
    runCount: 2,
  );
  @override
  Future<DisciplineRecord> createDiscipline(Map<String, dynamic> data) async {
    created = true;
    return DisciplineRecord(
      id: 'r2',
      memberId: 'member',
      memberName: 'Arlette Ndzi',
      title: 'Retard répété',
      description: '',
      amount: '20.00',
      currency: 'EUR',
      status: 'open',
      recordedAt: _fixed,
    );
  }

  @override
  Future<List<DisciplineRecord>> discipline({required bool ownOnly}) async =>
      <DisciplineRecord>[
        DisciplineRecord(
          id: 'r1',
          memberId: 'member',
          memberName: 'Arlette Ndzi',
          title: 'Avertissement',
          description: 'Incident',
          amount: '10.00',
          currency: 'EUR',
          status: 'open',
          recordedAt: _fixed,
        ),
      ];
  @override
  Future<List<GovernanceItem>> announcements() async => const <GovernanceItem>[
    GovernanceItem(
      id: 'a',
      title: 'Réunion',
      body: 'Vendredi',
      meta: '2026-08-12',
      status: 'published',
    ),
  ];
  @override
  Future<List<GovernanceItem>> documents() async => const <GovernanceItem>[];
  @override
  Future<List<GovernanceItem>> events() async => const <GovernanceItem>[];
  @override
  Future<List<GovernanceItem>> policies() async => const <GovernanceItem>[];
  @override
  Future<void> requestBackup(String? reason) async {}
}

final DateTime _fixed = DateTime(2026, 8, 12);

class _MemberGateway implements MemberGateway {
  @override
  Future<MemberProfile> create(MemberDraft draft) async =>
      throw UnimplementedError();
  @override
  Future<List<MemberProfile>> list({String? query}) async =>
      const <MemberProfile>[
        MemberProfile(
          id: 'member',
          memberCode: 'CEN-001',
          firstName: 'Arlette',
          lastName: 'Ndzi',
          displayName: 'Arlette Ndzi',
          status: 'active',
          membershipType: 'individual',
          joinedAt: null,
        ),
      ];
  @override
  Future<MemberProfile> update(String id, Map<String, dynamic> patch) async =>
      throw UnimplementedError();
}
