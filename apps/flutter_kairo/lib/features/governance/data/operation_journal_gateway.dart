import '../../../core/api/kairo_api_client.dart';

class OperationJournalEntry {
  const OperationJournalEntry({
    required this.action,
    required this.entityType,
    required this.createdAt,
    this.actorName,
    this.actorRoles = const <String>[],
    this.details = const <String, dynamic>{},
  });
  factory OperationJournalEntry.fromJson(Map<String, dynamic> json) {
    final Map<String, dynamic>? actor = json['actor'] as Map<String, dynamic>?;
    return OperationJournalEntry(
      action: json['action'].toString(),
      entityType: json['entity_type'].toString(),
      createdAt: json['created_at'].toString(),
      actorName:
          actor?['display_name']?.toString() ?? actor?['email']?.toString(),
      actorRoles: (actor?['roles'] as List<dynamic>? ?? const <dynamic>[])
          .map((dynamic value) => value.toString())
          .toList(),
      details:
          json['details'] as Map<String, dynamic>? ?? const <String, dynamic>{},
    );
  }
  final String action;
  final String entityType;
  final String createdAt;
  final String? actorName;
  final List<String> actorRoles;
  final Map<String, dynamic> details;
}

abstract class OperationJournalGateway {
  Future<List<OperationJournalEntry>> load({String? search});
}

class HttpOperationJournalGateway implements OperationJournalGateway {
  const HttpOperationJournalGateway(this._client);
  final KairoApiClient _client;
  @override
  Future<List<OperationJournalEntry>> load({String? search}) async {
    final String suffix = search == null || search.trim().isEmpty
        ? '?limit=50'
        : '?limit=50&search=${Uri.encodeQueryComponent(search.trim())}';
    final Object? raw = await _client.requestJson(
      'GET',
      'admin/audit/operation-journal$suffix',
    );
    return (raw as List<dynamic>)
        .map(
          (dynamic value) =>
              OperationJournalEntry.fromJson(value as Map<String, dynamic>),
        )
        .toList();
  }
}
