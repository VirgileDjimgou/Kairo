import 'package:flutter/material.dart';

import 'offline_workspace_controller.dart';

class OfflineStatusBanner extends StatelessWidget {
  const OfflineStatusBanner({
    super.key,
    required this.controller,
    required this.locale,
  });

  final OfflineWorkspaceController controller;
  final String locale;

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: controller,
    builder: (context, _) {
      final text = _OfflineText(locale);
      final label = !controller.isOnline
          ? text.offline
          : controller.lastSynchronizedAt == null
          ? text.syncing
          : text.synced(controller.lastSynchronizedAt!);
      return Semantics(
        liveRegion: true,
        label: label,
        child: Container(
          width: double.infinity,
          color: controller.isOnline
              ? const Color(0xFFE6F4EA)
              : const Color(0xFFFFF3CD),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: <Widget>[
              Icon(
                controller.isOnline
                    ? Icons.cloud_done_outlined
                    : Icons.cloud_off_outlined,
                size: 18,
                color: controller.isOnline
                    ? const Color(0xFF137333)
                    : const Color(0xFF7A5200),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(label)),
              if (controller.pendingCommands.isNotEmpty)
                Chip(
                  label: Text(text.drafts(controller.pendingCommands.length)),
                ),
            ],
          ),
        ),
      );
    },
  );
}

class _OfflineText {
  const _OfflineText(this.locale);
  final String locale;
  bool get _en => locale == 'en';
  bool get _de => locale == 'de';
  String get offline => _en
      ? 'Offline — authorised cached data and local drafts remain available.'
      : _de
      ? 'Offline — berechtigte Zwischenspeicher und lokale Entwürfe bleiben verfügbar.'
      : 'Hors ligne — les données autorisées en cache et les brouillons locaux restent disponibles.';
  String get syncing => _en
      ? 'Synchronising authorised data…'
      : _de
      ? 'Berechtigte Daten werden synchronisiert…'
      : 'Synchronisation des données autorisées…';
  String synced(DateTime value) => _en
      ? 'Last synchronised ${_time(value)}'
      : _de
      ? 'Zuletzt synchronisiert: ${_time(value)}'
      : 'Dernière synchronisation : ${_time(value)}';
  String drafts(int count) => _en
      ? '$count draft${count == 1 ? '' : 's'}'
      : _de
      ? '$count Entwurf${count == 1 ? '' : 'e'}'
      : '$count brouillon${count == 1 ? '' : 's'}';
  String _time(DateTime value) =>
      '${value.hour.toString().padLeft(2, '0')}:${value.minute.toString().padLeft(2, '0')}';
}
