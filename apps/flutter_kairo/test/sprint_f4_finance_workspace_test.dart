import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/localization/kairo_localizations.dart';
import 'package:kairo_flutter/features/finance/data/finance_gateway.dart';
import 'package:kairo_flutter/features/finance/presentation/finance_workspace_page.dart';
import 'package:kairo_flutter/features/members/data/member_gateway.dart';
import 'package:kairo_flutter/features/members/data/member_models.dart';

void main() {
  testWidgets('treasurer can view budget and expense entry', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: FinanceWorkspacePage(
          gateway: _FinanceGateway(),
          memberGateway: _MemberGateway(),
          locale: KairoLocale.fr,
          canWriteExpenses: true,
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Budget annuel · ${DateTime.now().year}'), findsOneWidget);
    await tester.drag(find.byType(ListView), const Offset(0, -900));
    await tester.pumpAndSettle();
    expect(find.text('Enregistrer une dépense'), findsAtLeastNWidgets(1));
    expect(find.text('Trésorerie disponible'), findsOneWidget);
  });

  testWidgets(
    'auditor receives read-only finance overview without expense entry',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: FinanceWorkspacePage(
            gateway: _FinanceGateway(),
            memberGateway: _MemberGateway(),
            locale: KairoLocale.fr,
            canWriteExpenses: false,
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(
        find.text('Consultation financière en lecture seule et exports.'),
        findsOneWidget,
      );
      await tester.drag(find.byType(ListView), const Offset(0, -900));
      await tester.pumpAndSettle();
      expect(find.text('Enregistrer une dépense'), findsNothing);
      expect(find.text('Vue des cotisations'), findsOneWidget);
    },
  );
}

class _FinanceGateway implements FinanceGateway {
  @override
  Future<AnnualBudget> annualBudget(int year) async => AnnualBudget(
    year: year,
    currency: 'EUR',
    incomeTotal: '240.00',
    expenseTotal: '60.00',
    availableBalance: '180.00',
    incomeByCategory: const <BudgetSlice>[
      BudgetSlice(category: 'membership_contribution', amount: '240.00'),
    ],
    expensesByCategory: const <BudgetSlice>[
      BudgetSlice(category: 'sport_equipment', amount: '60.00'),
    ],
    recentExpenses: const <FinanceExpense>[
      FinanceExpense(
        id: 'expense',
        category: 'sport_equipment',
        amount: '60.00',
        description: 'Balls',
        spentAt: '2026-08-12',
      ),
    ],
  );
  @override
  Future<List<FinanceContribution>> contributions(int year) async =>
      const <FinanceContribution>[
        FinanceContribution(
          id: 'contribution',
          memberProfileId: 'member',
          year: 2026,
          expectedAmount: '60.00',
          paidAmount: '20.00',
          balance: '40.00',
          status: 'partial',
        ),
      ];
  @override
  Future<FinanceExpense> createExpense(Map<String, dynamic> payload) async =>
      const FinanceExpense(
        id: 'expense',
        category: 'sport_equipment',
        amount: '60.00',
        description: 'Balls',
        spentAt: '2026-08-12',
      );
  @override
  Future<List<int>> exportReport(String format, int year) async => <int>[
    1,
    2,
    3,
  ];
  @override
  Future<List<FinanceContribution>> memberContributions(
    String profileId,
  ) async => const <FinanceContribution>[];
  @override
  Future<FinanceSummary> summary(int year) async => const FinanceSummary(
    totalExpected: '300.00',
    totalPaid: '240.00',
    totalBalance: '60.00',
    totalCount: 5,
  );
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
