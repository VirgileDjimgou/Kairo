import 'package:flutter/foundation.dart';

import '../../../core/api/kairo_api_client.dart';
import '../data/member_gateway.dart';
import '../data/member_models.dart';

class MemberController extends ChangeNotifier {
  MemberController({required this.gateway});
  final MemberGateway gateway;
  List<MemberProfile> members = const <MemberProfile>[];
  MemberProfile? selected;
  bool loading = false;
  bool saving = false;
  String? error;

  Future<void> load({String? query}) async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      members = await gateway.list(query: query);
    } on KairoApiException catch (exception) {
      error = exception.message;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  void select(MemberProfile member) {
    selected = member;
    notifyListeners();
  }

  Future<bool> create(MemberDraft draft) async {
    saving = true;
    error = null;
    notifyListeners();
    try {
      final MemberProfile created = await gateway.create(draft);
      members = <MemberProfile>[created, ...members];
      selected = created;
      return true;
    } on KairoApiException catch (exception) {
      error = exception.message;
      return false;
    } finally {
      saving = false;
      notifyListeners();
    }
  }

  Future<bool> changeStatus(MemberProfile member, String status) async {
    return update(member, <String, dynamic>{'status': status});
  }

  Future<bool> update(MemberProfile member, Map<String, dynamic> patch) async {
    saving = true;
    error = null;
    notifyListeners();
    try {
      final MemberProfile updated = await gateway.update(member.id, patch);
      members = members
          .map((MemberProfile item) => item.id == updated.id ? updated : item)
          .toList();
      selected = updated;
      return true;
    } on KairoApiException catch (exception) {
      error = exception.message;
      return false;
    } finally {
      saving = false;
      notifyListeners();
    }
  }
}
