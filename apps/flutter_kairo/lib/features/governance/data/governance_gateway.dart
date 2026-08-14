import '../../../core/api/kairo_api_client.dart';

class DisciplineRecord {
  const DisciplineRecord({
    required this.id,
    required this.memberId,
    required this.memberName,
    required this.title,
    required this.description,
    required this.amount,
    required this.currency,
    required this.status,
    required this.recordedAt,
  });
  factory DisciplineRecord.fromJson(Map<String, dynamic> json) =>
      DisciplineRecord(
        id: json['id'] as String,
        memberId: json['membership_profile_id'] as String,
        memberName: json['membership_display_name'] as String? ?? '',
        title: json['title'] as String,
        description: json['description'] as String? ?? '',
        amount: json['amount'] as String? ?? '0.00',
        currency: json['currency'] as String? ?? 'EUR',
        status: json['status'] as String? ?? 'open',
        recordedAt:
            DateTime.tryParse(json['recorded_at'] as String? ?? '') ??
            DateTime.now(),
      );
  final String id,
      memberId,
      memberName,
      title,
      description,
      amount,
      currency,
      status;
  final DateTime recordedAt;
}

class GovernanceItem {
  const GovernanceItem({
    required this.id,
    required this.title,
    required this.body,
    required this.meta,
    required this.status,
  });
  factory GovernanceItem.fromJson(
    Map<String, dynamic> json, {
    String? bodyKey,
    String? metaKey,
  }) => GovernanceItem(
    id: json['id'] as String,
    title: json['title'] as String? ?? '',
    body: json[bodyKey ?? 'description'] as String? ?? '',
    meta: json[metaKey ?? 'status']?.toString() ?? '',
    status: json['status']?.toString() ?? 'published',
  );
  final String id, title, body, meta, status;
}

class BackupOverview {
  const BackupOverview({
    required this.automatic,
    required this.retention,
    required this.externalStorage,
    required this.pitr,
    required this.lastSuccess,
    required this.runCount,
  });
  factory BackupOverview.fromJson(Map<String, dynamic> json) => BackupOverview(
    automatic: json['automatic_enabled'] as bool? ?? false,
    retention: json['retention_days'] as int? ?? 0,
    externalStorage: json['external_storage_configured'] as bool? ?? false,
    pitr: json['point_in_time_recovery_enabled'] as bool? ?? false,
    lastSuccess: json['last_successful_backup_at'] as String?,
    runCount: (json['runs'] as List<dynamic>? ?? <dynamic>[]).length,
  );
  final bool automatic, externalStorage, pitr;
  final int retention, runCount;
  final String? lastSuccess;
}

abstract class GovernanceGateway {
  Future<List<DisciplineRecord>> discipline({required bool ownOnly});
  Future<DisciplineRecord> createDiscipline(Map<String, dynamic> data);
  Future<List<GovernanceItem>> policies();
  Future<List<GovernanceItem>> documents();
  Future<List<GovernanceItem>> events();
  Future<List<GovernanceItem>> announcements();
  Future<BackupOverview> backupOverview();
  Future<void> requestBackup(String? reason);
}

abstract class DocumentUploadGateway {
  Future<GovernanceItem> uploadDocument({
    required String filename,
    required List<int> bytes,
    required String title,
  });
}

class HttpGovernanceGateway
    implements GovernanceGateway, DocumentUploadGateway {
  const HttpGovernanceGateway(this._client);
  final KairoApiClient _client;
  Future<List<Map<String, dynamic>>> _list(String path) async {
    final Object? payload = await _client.requestJson('GET', path);
    if (payload is! List<dynamic>) {
      throw const KairoApiException(
        statusCode: 200,
        message: 'Unexpected governance response.',
      );
    }
    return payload.cast<Map<String, dynamic>>();
  }

  @override
  Future<List<DisciplineRecord>> discipline({required bool ownOnly}) async =>
      (await _list(
        ownOnly ? 'disciplinary/me' : 'disciplinary/',
      )).map(DisciplineRecord.fromJson).toList();
  @override
  Future<DisciplineRecord> createDiscipline(Map<String, dynamic> data) async =>
      DisciplineRecord.fromJson(
        await _client.requestJson('POST', 'disciplinary/', body: data)
            as Map<String, dynamic>,
      );
  @override
  Future<List<GovernanceItem>> policies() async => (await _list(
    'policies/public',
  )).map((item) => GovernanceItem.fromJson(item)).toList();
  @override
  Future<List<GovernanceItem>> documents() async => (await _list('documents/'))
      .map((item) => GovernanceItem.fromJson(item, metaKey: 'access_scope'))
      .toList();
  @override
  Future<GovernanceItem> uploadDocument({
    required String filename,
    required List<int> bytes,
    required String title,
  }) async => GovernanceItem.fromJson(
    await _client.uploadFile(
      path: 'documents/upload',
      filename: filename,
      bytes: bytes,
      fields: <String, String>{'title': title, 'access_scope': 'tenant_public'},
    ),
    metaKey: 'access_scope',
  );
  @override
  Future<List<GovernanceItem>> events() async => (await _list(
    'events/public',
  )).map((item) => GovernanceItem.fromJson(item, metaKey: 'start_at')).toList();
  @override
  Future<List<GovernanceItem>> announcements() async =>
      (await _list('announcements/active'))
          .map(
            (item) => GovernanceItem.fromJson(
              item,
              bodyKey: 'body',
              metaKey: 'published_at',
            ),
          )
          .toList();
  @override
  Future<BackupOverview> backupOverview() async =>
      BackupOverview.fromJson(await _client.getJson('recovery/backups'));
  @override
  Future<void> requestBackup(String? reason) async {
    await _client.requestJson(
      'POST',
      'recovery/backups',
      body: <String, dynamic>{
        if (reason != null && reason.isNotEmpty) 'reason': reason,
      },
    );
  }
}
