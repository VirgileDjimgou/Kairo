import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/features/finance/data/receipt_gateway.dart';
import 'package:kairo_flutter/features/finance/presentation/receipt_controller.dart';

void main() {
  test(
    'treasurer validates then confirms custody through the API gateway',
    () async {
      final _FakeReceiptGateway gateway = _FakeReceiptGateway();
      final ReceiptController controller = ReceiptController(gateway: gateway);

      await controller.load(review: true);
      expect(controller.reviewItems.single.status, 'submitted');

      await controller.process('receipt-1', <String, dynamic>{
        'action': 'validated',
        'processed_amount': '60.00',
        'handover_reminder_days': 2,
      });
      expect(gateway.processed, isTrue);

      await controller.confirmTreasury('receipt-1');
      expect(gateway.confirmed, isTrue);
    },
  );
}

class _FakeReceiptGateway implements ReceiptGateway {
  bool processed = false;
  bool confirmed = false;
  ReceiptDeclaration get _submitted => const ReceiptDeclaration(
    id: 'receipt-1',
    amount: '60.00',
    status: 'submitted',
    incomeType: 'membership_contribution',
  );
  ReceiptDeclaration get _validated => const ReceiptDeclaration(
    id: 'receipt-1',
    amount: '60.00',
    status: 'validated',
    incomeType: 'membership_contribution',
    cashHandoverStatus: 'pending_handover',
    handoverReminderDays: 2,
  );
  @override
  Future<ReceiptDeclaration> confirmTreasury(
    String id,
    Map<String, dynamic> payload,
  ) async {
    confirmed = true;
    return _validated;
  }

  @override
  Future<ReceiptDeclaration> create(Map<String, dynamic> draft) async =>
      _submitted;
  @override
  Future<List<ReceiptMemberOption>> memberOptions({String? query}) async =>
      const <ReceiptMemberOption>[];
  @override
  Future<List<ReceiptDeclaration>> mine() async => <ReceiptDeclaration>[
    _submitted,
  ];
  @override
  Future<ReceiptDeclaration> process(
    String id,
    Map<String, dynamic> payload,
  ) async {
    processed = true;
    return _validated;
  }

  @override
  Future<List<ReceiptDeclaration>> review() async => <ReceiptDeclaration>[
    _submitted,
  ];
  @override
  Future<ReceiptDeclaration> submit(String id) async => _submitted;
  @override
  Future<ReceiptDeclaration> updateReminder(
    String id,
    Map<String, dynamic> payload,
  ) async => _validated;
}
