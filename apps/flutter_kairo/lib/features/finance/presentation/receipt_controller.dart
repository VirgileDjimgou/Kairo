import 'package:flutter/foundation.dart';

import '../data/receipt_gateway.dart';

class ReceiptController extends ChangeNotifier {
  ReceiptController({required this.gateway});
  final ReceiptGateway gateway;
  List<ReceiptDeclaration> mineItems = const <ReceiptDeclaration>[];
  List<ReceiptDeclaration> reviewItems = const <ReceiptDeclaration>[];
  bool loading = false;
  String? error;

  Future<void> load({required bool review}) async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      if (review) {
        reviewItems = await gateway.review();
      } else {
        mineItems = await gateway.mine();
      }
    } catch (_) {
      error = 'receipt_load_failed';
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> declare(Map<String, dynamic> draft) async {
    final ReceiptDeclaration saved = await gateway.create(draft);
    await gateway.submit(saved.id);
    await load(review: false);
  }

  Future<void> process(String id, Map<String, dynamic> payload) async {
    await gateway.process(id, payload);
    await load(review: true);
  }

  Future<void> confirmTreasury(String id) async {
    await gateway.confirmTreasury(id, <String, dynamic>{'method': 'cash'});
    await load(review: true);
  }

  Future<void> changeReminder(String id, int days) async {
    await gateway.updateReminder(id, <String, dynamic>{'reminder_days': days});
    await load(review: true);
  }
}
