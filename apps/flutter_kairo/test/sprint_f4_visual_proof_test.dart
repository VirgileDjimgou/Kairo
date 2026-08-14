import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/features/finance/data/finance_gateway.dart';
import 'package:kairo_flutter/features/finance/presentation/finance_workspace_page.dart';
import 'package:kairo_flutter/features/members/data/member_gateway.dart';
import 'package:kairo_flutter/features/members/data/member_models.dart';

void main() {
  testWidgets('F4 proof treasurer budget and expense on Android width', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(_page(canWriteExpenses: true));
    await tester.pumpAndSettle();
    expect(find.text('Budget annuel · ${DateTime.now().year}'), findsOneWidget);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f4/treasurer-android-budget.png'),
    );
  });

  testWidgets('F4 proof auditor read-only export on Web width', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(_page(canWriteExpenses: false));
    await tester.pumpAndSettle();
    expect(
      find.text('Consultation financière en lecture seule et exports.'),
      findsOneWidget,
    );
    expect(find.text('Enregistrer une dépense'), findsNothing);
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f4/auditor-web-read-only.png'),
    );
  });
}

Widget _page({required bool canWriteExpenses}) => MaterialApp(
  home: FinanceWorkspacePage(
    gateway: _Gateway(),
    memberGateway: _Members(),
    locale: KairoLocale.fr,
    canWriteExpenses: canWriteExpenses,
  ),
);

class _Gateway implements FinanceGateway {
  @override
  Future<AnnualBudget> annualBudget(int year) async => AnnualBudget(
    year: year,
    currency: 'EUR',
    incomeTotal: '460.00',
    expenseTotal: '120.00',
    availableBalance: '340.00',
    incomeByCategory: const <BudgetSlice>[
      BudgetSlice(category: 'membership_contribution', amount: '300.00'),
      BudgetSlice(category: 'donation', amount: '160.00'),
    ],
    expensesByCategory: const <BudgetSlice>[
      BudgetSlice(category: 'sport_equipment', amount: '80.00'),
      BudgetSlice(category: 'fuel_transport', amount: '40.00'),
    ],
    recentExpenses: const <FinanceExpense>[
      FinanceExpense(
        id: 'expense-1',
        category: 'sport_equipment',
        amount: '80.00',
        description: 'Achat de ballons',
        spentAt: '2026-08-12',
        payee: 'Sport Pro',
      ),
    ],
  );
  @override
  Future<List<FinanceContribution>> contributions(int year) async =>
      const <FinanceContribution>[
        FinanceContribution(
          id: 'contribution-1',
          memberProfileId: 'member-1',
          year: 2026,
          expectedAmount: '60.00',
          paidAmount: '40.00',
          balance: '20.00',
          status: 'partial',
        ),
      ];
  @override
  Future<FinanceExpense> createExpense(Map<String, dynamic> payload) async =>
      throw UnimplementedError();
  @override
  Future<List<int>> exportReport(String format, int year) async => <int>[1];
  @override
  Future<List<FinanceContribution>> memberContributions(
    String profileId,
  ) async => const <FinanceContribution>[];
  @override
  Future<FinanceSummary> summary(int year) async => const FinanceSummary(
    totalExpected: '600.00',
    totalPaid: '460.00',
    totalBalance: '140.00',
    totalCount: 10,
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
