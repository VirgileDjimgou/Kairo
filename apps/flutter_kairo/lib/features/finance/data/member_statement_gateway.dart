import '../../../core/api/kairo_api_client.dart';

class MemberContribution {
  const MemberContribution({
    required this.year,
    required this.expectedAmount,
    required this.paidAmount,
    required this.balanceAmount,
    required this.status,
  });

  factory MemberContribution.fromJson(Map<String, dynamic> json) =>
      MemberContribution(
        year: json['year'].toString(),
        expectedAmount:
            (json['expected_amount'] ?? json['amount_expected'] ?? '0.00')
                .toString(),
        paidAmount: (json['paid_amount'] ?? json['amount_paid'] ?? '0.00')
            .toString(),
        balanceAmount:
            (json['balance'] ??
                    json['balance_amount'] ??
                    json['amount_due'] ??
                    '0.00')
                .toString(),
        status: (json['status'] ?? 'open').toString(),
      );

  final String year;
  final String expectedAmount;
  final String paidAmount;
  final String balanceAmount;
  final String status;
}

class MemberStatement {
  const MemberStatement({
    required this.displayName,
    required this.memberCode,
    required this.totalExpected,
    required this.totalPaid,
    required this.totalBalance,
    required this.contributions,
  });

  factory MemberStatement.fromJson(Map<String, dynamic> json) {
    final Map<String, dynamic> profile =
        json['profile'] as Map<String, dynamic>;
    final Map<String, dynamic> summary =
        json['summary'] as Map<String, dynamic>;
    final List<dynamic> entries =
        json['contributions'] as List<dynamic>? ?? const <dynamic>[];
    return MemberStatement(
      displayName: profile['display_name'].toString(),
      memberCode: profile['member_code'].toString(),
      totalExpected: summary['total_expected'].toString(),
      totalPaid: summary['total_paid'].toString(),
      totalBalance: summary['total_balance'].toString(),
      contributions: entries
          .map(
            (dynamic entry) =>
                MemberContribution.fromJson(entry as Map<String, dynamic>),
          )
          .toList(),
    );
  }

  final String displayName;
  final String memberCode;
  final String totalExpected;
  final String totalPaid;
  final String totalBalance;
  final List<MemberContribution> contributions;
}

abstract class MemberStatementGateway {
  Future<MemberStatement> mine();
}

class HttpMemberStatementGateway implements MemberStatementGateway {
  const HttpMemberStatementGateway(this._client);
  final KairoApiClient _client;

  @override
  Future<MemberStatement> mine() async {
    final Object? payload = await _client.requestJson(
      'GET',
      'memberships/me/statement',
    );
    return MemberStatement.fromJson(payload as Map<String, dynamic>);
  }
}
