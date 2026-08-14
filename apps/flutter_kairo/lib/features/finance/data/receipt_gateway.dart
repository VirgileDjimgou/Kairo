import '../../../core/api/kairo_api_client.dart';

class ReceiptDeclaration {
  const ReceiptDeclaration({
    required this.id,
    required this.amount,
    required this.status,
    required this.incomeType,
    this.sourceName,
    this.note,
    this.cashHandoverStatus,
    this.handoverReminderDays,
  });

  factory ReceiptDeclaration.fromJson(Map<String, dynamic> json) =>
      ReceiptDeclaration(
        id: json['id'] as String,
        amount: json['amount'].toString(),
        status: json['status'] as String,
        incomeType: json['income_type'] as String,
        sourceName: json['source_name'] as String?,
        note: json['note'] as String?,
        cashHandoverStatus: json['cash_handover_status'] as String?,
        handoverReminderDays: json['handover_reminder_days'] as int?,
      );

  final String id;
  final String amount;
  final String status;
  final String incomeType;
  final String? sourceName;
  final String? note;
  final String? cashHandoverStatus;
  final int? handoverReminderDays;
}

class ReceiptMemberOption {
  const ReceiptMemberOption({required this.id, required this.label});
  factory ReceiptMemberOption.fromJson(Map<String, dynamic> json) =>
      ReceiptMemberOption(
        id: json['id'] as String,
        label: (json['label'] ?? json['display_name'] ?? json['member_code'])
            .toString(),
      );
  final String id;
  final String label;
}

abstract class ReceiptGateway {
  Future<List<ReceiptDeclaration>> mine();
  Future<List<ReceiptDeclaration>> review();
  Future<List<ReceiptMemberOption>> memberOptions({String? query});
  Future<ReceiptDeclaration> create(Map<String, dynamic> draft);
  Future<ReceiptDeclaration> submit(String id);
  Future<ReceiptDeclaration> process(String id, Map<String, dynamic> payload);
  Future<ReceiptDeclaration> confirmTreasury(
    String id,
    Map<String, dynamic> payload,
  );
  Future<ReceiptDeclaration> updateReminder(
    String id,
    Map<String, dynamic> payload,
  );
}

class HttpReceiptGateway implements ReceiptGateway {
  const HttpReceiptGateway(this.client);
  final KairoApiClient client;

  Future<List<ReceiptDeclaration>> _list(String path) async {
    final Object? raw = await client.requestJson('GET', path);
    if (raw is! List<dynamic>) {
      throw const KairoApiException(
        statusCode: 200,
        message: 'Unexpected receipt response.',
      );
    }
    return raw
        .map(
          (dynamic item) =>
              ReceiptDeclaration.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  @override
  Future<List<ReceiptDeclaration>> mine() =>
      _list('contributions/receipt-declarations/mine');
  @override
  Future<List<ReceiptDeclaration>> review() =>
      _list('contributions/receipt-declarations');

  @override
  Future<List<ReceiptMemberOption>> memberOptions({String? query}) async {
    final String suffix = query == null || query.trim().isEmpty
        ? ''
        : '?q=${Uri.encodeQueryComponent(query.trim())}';
    final Object? raw = await client.requestJson(
      'GET',
      'contributions/receipt-declarations/member-options$suffix',
    );
    if (raw is! List<dynamic>) return const <ReceiptMemberOption>[];
    return raw
        .map(
          (dynamic item) =>
              ReceiptMemberOption.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  @override
  Future<ReceiptDeclaration> create(Map<String, dynamic> draft) async =>
      _receipt('POST', 'contributions/receipt-declarations', body: draft);
  @override
  Future<ReceiptDeclaration> submit(String id) async =>
      _receipt('POST', 'contributions/receipt-declarations/$id/submit');
  @override
  Future<ReceiptDeclaration> process(String id, Map<String, dynamic> payload) =>
      _receipt(
        'POST',
        'contributions/receipt-declarations/$id/process',
        body: payload,
      );
  @override
  Future<ReceiptDeclaration> confirmTreasury(
    String id,
    Map<String, dynamic> payload,
  ) => _receipt(
    'POST',
    'contributions/receipt-declarations/$id/confirm-treasury-receipt',
    body: payload,
  );
  @override
  Future<ReceiptDeclaration> updateReminder(
    String id,
    Map<String, dynamic> payload,
  ) => _receipt(
    'POST',
    'contributions/receipt-declarations/$id/handover-reminder',
    body: payload,
  );

  Future<ReceiptDeclaration> _receipt(
    String method,
    String path, {
    Map<String, dynamic>? body,
  }) async {
    final Object? raw = await client.requestJson(method, path, body: body);
    return ReceiptDeclaration.fromJson(raw as Map<String, dynamic>);
  }
}
