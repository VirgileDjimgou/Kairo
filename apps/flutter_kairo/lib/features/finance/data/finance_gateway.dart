import '../../../core/api/kairo_api_client.dart';
import '../../members/data/member_models.dart';

class FinanceSummary {
  const FinanceSummary({
    required this.totalExpected,
    required this.totalPaid,
    required this.totalBalance,
    required this.totalCount,
  });

  factory FinanceSummary.fromJson(Map<String, dynamic> json) => FinanceSummary(
    totalExpected: (json['total_expected'] ?? '0.00').toString(),
    totalPaid: (json['total_paid'] ?? '0.00').toString(),
    totalBalance: (json['total_balance'] ?? '0.00').toString(),
    totalCount: (json['total_count'] ?? 0) as int,
  );

  final String totalExpected;
  final String totalPaid;
  final String totalBalance;
  final int totalCount;
}

class FinanceContribution {
  const FinanceContribution({
    required this.id,
    required this.memberProfileId,
    required this.year,
    required this.expectedAmount,
    required this.paidAmount,
    required this.balance,
    required this.status,
  });

  factory FinanceContribution.fromJson(Map<String, dynamic> json) =>
      FinanceContribution(
        id: json['id'].toString(),
        memberProfileId: json['membership_profile_id'].toString(),
        year: (json['year'] ?? 0) as int,
        expectedAmount: (json['expected_amount'] ?? '0.00').toString(),
        paidAmount: (json['paid_amount'] ?? '0.00').toString(),
        balance: (json['balance'] ?? '0.00').toString(),
        status: (json['status'] ?? 'pending').toString(),
      );

  final String id;
  final String memberProfileId;
  final int year;
  final String expectedAmount;
  final String paidAmount;
  final String balance;
  final String status;
}

class BudgetSlice {
  const BudgetSlice({required this.category, required this.amount});
  factory BudgetSlice.fromJson(Map<String, dynamic> json) => BudgetSlice(
    category: json['category'].toString(),
    amount: (json['amount'] ?? '0.00').toString(),
  );
  final String category;
  final String amount;
}

class FinanceExpense {
  const FinanceExpense({
    required this.id,
    required this.category,
    required this.amount,
    required this.description,
    required this.spentAt,
    this.payee,
  });
  factory FinanceExpense.fromJson(Map<String, dynamic> json) => FinanceExpense(
    id: json['id'].toString(),
    category: json['category'].toString(),
    amount: (json['amount'] ?? '0.00').toString(),
    description: (json['description'] ?? '').toString(),
    spentAt: (json['spent_at'] ?? '').toString(),
    payee: json['payee']?.toString(),
  );
  final String id;
  final String category;
  final String amount;
  final String description;
  final String spentAt;
  final String? payee;
}

class AnnualBudget {
  const AnnualBudget({
    required this.year,
    required this.currency,
    required this.incomeTotal,
    required this.expenseTotal,
    required this.availableBalance,
    required this.incomeByCategory,
    required this.expensesByCategory,
    required this.recentExpenses,
  });
  factory AnnualBudget.fromJson(Map<String, dynamic> json) => AnnualBudget(
    year: (json['year'] ?? 0) as int,
    currency: (json['currency'] ?? 'EUR').toString(),
    incomeTotal: (json['income_total'] ?? '0.00').toString(),
    expenseTotal: (json['expense_total'] ?? '0.00').toString(),
    availableBalance: (json['available_balance'] ?? '0.00').toString(),
    incomeByCategory:
        ((json['income_by_category'] ?? <dynamic>[]) as List<dynamic>)
            .map(
              (dynamic item) =>
                  BudgetSlice.fromJson(item as Map<String, dynamic>),
            )
            .toList(),
    expensesByCategory:
        ((json['expenses_by_category'] ?? <dynamic>[]) as List<dynamic>)
            .map(
              (dynamic item) =>
                  BudgetSlice.fromJson(item as Map<String, dynamic>),
            )
            .toList(),
    recentExpenses: ((json['recent_expenses'] ?? <dynamic>[]) as List<dynamic>)
        .map(
          (dynamic item) =>
              FinanceExpense.fromJson(item as Map<String, dynamic>),
        )
        .toList(),
  );
  final int year;
  final String currency;
  final String incomeTotal;
  final String expenseTotal;
  final String availableBalance;
  final List<BudgetSlice> incomeByCategory;
  final List<BudgetSlice> expensesByCategory;
  final List<FinanceExpense> recentExpenses;
}

abstract class FinanceGateway {
  Future<FinanceSummary> summary(int year);
  Future<List<FinanceContribution>> contributions(int year);
  Future<List<FinanceContribution>> memberContributions(String profileId);
  Future<AnnualBudget> annualBudget(int year);
  Future<FinanceExpense> createExpense(Map<String, dynamic> payload);
  Future<List<int>> exportReport(String format, int year);
}

class HttpFinanceGateway implements FinanceGateway {
  const HttpFinanceGateway(this._client);
  final KairoApiClient _client;

  @override
  Future<FinanceSummary> summary(int year) async => FinanceSummary.fromJson(
    await _client.getJson('contributions/summary?year=$year'),
  );

  @override
  Future<List<FinanceContribution>> contributions(int year) async =>
      _contributions('contributions/?year=$year');

  @override
  Future<List<FinanceContribution>> memberContributions(
    String profileId,
  ) async => _contributions('contributions/by-member/$profileId');

  Future<List<FinanceContribution>> _contributions(String path) async {
    final Object? payload = await _client.requestJson('GET', path);
    if (payload is! List<dynamic>) {
      throw const KairoApiException(
        statusCode: 200,
        message: 'Unexpected finance response.',
      );
    }
    return payload
        .map(
          (dynamic item) =>
              FinanceContribution.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  @override
  Future<AnnualBudget> annualBudget(int year) async => AnnualBudget.fromJson(
    await _client.getJson('contributions/annual-budget?year=$year'),
  );

  @override
  Future<FinanceExpense> createExpense(Map<String, dynamic> payload) async {
    final Object? data = await _client.requestJson(
      'POST',
      'contributions/expenses',
      body: payload,
    );
    return FinanceExpense.fromJson(data as Map<String, dynamic>);
  }

  @override
  Future<List<int>> exportReport(String format, int year) =>
      _client.requestBytes('contributions/report/export/$format?year=$year');
}

class FinanceMemberResult {
  const FinanceMemberResult({
    required this.member,
    required this.contributions,
  });
  final MemberProfile member;
  final List<FinanceContribution> contributions;
}
