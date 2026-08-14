import '../../../core/api/kairo_api_client.dart';
import 'member_models.dart';

abstract class MemberGateway {
  Future<List<MemberProfile>> list({String? query});
  Future<MemberProfile> create(MemberDraft draft);
  Future<MemberProfile> update(String id, Map<String, dynamic> patch);
}

class HttpMemberGateway implements MemberGateway {
  const HttpMemberGateway(this._client);
  final KairoApiClient _client;

  @override
  Future<List<MemberProfile>> list({String? query}) async {
    final String suffix = query == null || query.trim().isEmpty
        ? ''
        : '?q=${Uri.encodeQueryComponent(query.trim())}';
    final Object? payload = await _client.requestJson(
      'GET',
      'memberships/$suffix',
    );
    if (payload is! List<dynamic>) {
      throw const KairoApiException(
        statusCode: 200,
        message: 'Unexpected member directory response.',
      );
    }
    return payload
        .map(
          (dynamic item) =>
              MemberProfile.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  @override
  Future<MemberProfile> create(MemberDraft draft) async {
    final Object? payload = await _client.requestJson(
      'POST',
      'memberships/',
      body: draft.toJson(),
    );
    return MemberProfile.fromJson(payload as Map<String, dynamic>);
  }

  @override
  Future<MemberProfile> update(String id, Map<String, dynamic> patch) async {
    final Object? payload = await _client.requestJson(
      'PATCH',
      'memberships/$id',
      body: patch,
    );
    return MemberProfile.fromJson(payload as Map<String, dynamic>);
  }
}
