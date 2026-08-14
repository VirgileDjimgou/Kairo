import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/features/governance/data/governance_gateway.dart';
import 'package:kairo_flutter/features/governance/presentation/governance_workspace_page.dart';
import 'package:kairo_flutter/features/members/data/member_gateway.dart';
import 'package:kairo_flutter/features/members/data/member_models.dart';

void main() {
  testWidgets('F5 proof censor Android discipline workspace', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(_page(const <String>['censor']));
    await tester.pumpAndSettle();
    expect(find.text('Dossiers disciplinaires'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f5/censor-android-discipline.png'),
    );
  });
  testWidgets('F5 proof president Web read-only and backup', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(_page(const <String>['president']));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Annonces'));
    await tester.pumpAndSettle();
    expect(find.text('Centre de sauvegarde'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f5/president-web-read-only.png'),
    );
  });
}

Widget _page(List<String> roles) => MaterialApp(
  home: GovernanceWorkspacePage(
    gateway: _Gateway(),
    memberGateway: _Members(),
    locale: KairoLocale.fr,
    roles: roles,
  ),
);

class _Gateway implements GovernanceGateway {
  @override
  Future<BackupOverview> backupOverview() async => const BackupOverview(
    automatic: true,
    retention: 30,
    externalStorage: true,
    pitr: true,
    lastSuccess: null,
    runCount: 3,
  );
  @override
  Future<DisciplineRecord> createDiscipline(Map<String, dynamic> data) async =>
      DisciplineRecord(
        id: 'r2',
        memberId: 'm1',
        memberName: 'Arlette Ndzi',
        title: 'Retard',
        description: '',
        amount: '20.00',
        currency: 'EUR',
        status: 'open',
        recordedAt: DateTime(2026, 8, 12),
      );
  @override
  Future<List<DisciplineRecord>> discipline({required bool ownOnly}) async =>
      <DisciplineRecord>[
        DisciplineRecord(
          id: 'r1',
          memberId: 'm1',
          memberName: 'Arlette Ndzi',
          title: 'Avertissement',
          description: 'Incident après entraînement',
          amount: '10.00',
          currency: 'EUR',
          status: 'open',
          recordedAt: DateTime(2026, 8, 12),
        ),
      ];
  @override
  Future<List<GovernanceItem>> announcements() async => const <GovernanceItem>[
    GovernanceItem(
      id: 'a1',
      title: 'Réunion générale',
      body: 'Vendredi à 19 h',
      meta: '2026-08-12',
      status: 'published',
    ),
  ];
  @override
  Future<List<GovernanceItem>> documents() async => const <GovernanceItem>[
    GovernanceItem(
      id: 'd1',
      title: 'Statuts 2026',
      body: 'Document de référence',
      meta: 'tenant_public',
      status: 'ready',
    ),
  ];
  @override
  Future<List<GovernanceItem>> events() async => const <GovernanceItem>[
    GovernanceItem(
      id: 'e1',
      title: 'Tournoi d’été',
      body: 'Terrain central',
      meta: '2026-08-18',
      status: 'published',
    ),
  ];
  @override
  Future<List<GovernanceItem>> policies() async => const <GovernanceItem>[
    GovernanceItem(
      id: 'p1',
      title: 'Code de conduite',
      body: 'Règle interne',
      meta: 'discipline',
      status: 'published',
    ),
  ];
  @override
  Future<void> requestBackup(String? reason) async {}
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
