import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/core/offline/offline_workspace_controller.dart';

void main() {
  test(
    'drafts are isolated between tenants and removed on scope cleanup',
    () async {
      final storage = _MemoryStorage();
      final controller = OfflineWorkspaceController(storage: storage);
      await controller.activate(
        const OfflineScope(userId: 'user-a', tenantId: 'tenant-a'),
      );
      await controller.saveDraft('receipt', <String, dynamic>{
        'amount': '20.00',
      });
      expect(await controller.readDraft('receipt'), <String, dynamic>{
        'amount': '20.00',
      });

      await controller.activate(
        const OfflineScope(userId: 'user-b', tenantId: 'tenant-b'),
      );
      expect(await controller.readDraft('receipt'), isNull);
      await controller.saveDraft('receipt', <String, dynamic>{
        'amount': '50.00',
      });
      await controller.clearCurrentScope();
      expect(await controller.readDraft('receipt'), isNull);

      await controller.activate(
        const OfflineScope(userId: 'user-a', tenantId: 'tenant-a'),
      );
      expect(await controller.readDraft('receipt'), <String, dynamic>{
        'amount': '20.00',
      });
    },
  );

  test(
    'offline state preserves drafts and records unique queued draft metadata',
    () async {
      final controller = OfflineWorkspaceController(storage: _MemoryStorage());
      await controller.activate(
        const OfflineScope(userId: 'user-a', tenantId: 'tenant-a'),
      );
      controller.reportConnectivity(false);
      await controller.saveDraft('discipline', <String, dynamic>{
        'title': 'Late arrival',
      });
      await controller.saveDraft('discipline', <String, dynamic>{
        'title': 'Repeated late arrival',
      });
      expect(controller.isOnline, isFalse);
      expect(controller.pendingCommands, hasLength(1));
      expect(controller.pendingCommands.single.kind, 'draft:discipline');
      expect(await controller.readDraft('discipline'), <String, dynamic>{
        'title': 'Repeated late arrival',
      });
    },
  );

  test('cached GET data can be read without a network connection', () async {
    final controller = OfflineWorkspaceController(storage: _MemoryStorage());
    await controller.activate(
      const OfflineScope(userId: 'user-a', tenantId: 'tenant-a'),
    );
    await controller.cacheRead('contributions/mine', <String, dynamic>{
      'items': <String>['safe'],
    });
    controller.reportConnectivity(false);
    expect(await controller.readCached('contributions/mine'), <String, dynamic>{
      'items': <String>['safe'],
    });
  });

  test('secure scope helper does not expose raw identity values', () {
    const scope = OfflineScope(
      userId: 'member@example.org',
      tenantId: 'tenant-sensitive',
    );
    expect(scope.key, isNot(contains('member@example.org')));
    expect(scope.key, isNot(contains('tenant-sensitive')));
  });
}

class _MemoryStorage implements OfflineStorage {
  final Map<String, String> values = <String, String>{};
  @override
  Future<void> delete({required String key}) async {
    values.remove(key);
  }

  @override
  Future<String?> read({required String key}) async => values[key];
  @override
  Future<Map<String, String>> readAll() async =>
      Map<String, String>.from(values);
  @override
  Future<void> write({required String key, required String? value}) async {
    if (value == null) {
      values.remove(key);
    } else {
      values[key] = value;
    }
  }
}
