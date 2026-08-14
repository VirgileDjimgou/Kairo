import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/core/offline/offline_status_banner.dart';
import 'package:kairo_flutter/core/offline/offline_workspace_controller.dart';

void main() {
  testWidgets('F7 proof Android offline status and queued draft', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final controller = OfflineWorkspaceController(storage: _MemoryStorage());
    await controller.activate(
      const OfflineScope(userId: 'treasurer', tenantId: 'tenant-a'),
    );
    controller.reportConnectivity(false);
    await controller.saveDraft('receipt', <String, dynamic>{'amount': '20.00'});
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Column(
            children: <Widget>[
              OfflineStatusBanner(controller: controller, locale: 'fr'),
              const Expanded(
                child: Center(child: Text('Déclaration conservée localement')),
              ),
            ],
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f7/android-offline-draft.png'),
    );
  });

  testWidgets('F7 proof Web sync status', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final controller = OfflineWorkspaceController(storage: _MemoryStorage());
    await controller.activate(
      const OfflineScope(userId: 'president', tenantId: 'tenant-a'),
    );
    controller.reportConnectivity(true);
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Column(
            children: <Widget>[
              OfflineStatusBanner(controller: controller, locale: 'fr'),
              const Expanded(
                child: Center(child: Text('Données autorisées synchronisées')),
              ),
            ],
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../artifacts/sprint-f7/web-sync-status.png'),
    );
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
