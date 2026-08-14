import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../data/fcm_registration_state.dart';
import '../data/inbox_gateway.dart';

class InboxPage extends StatefulWidget {
  const InboxPage({
    super.key,
    required this.gateway,
    required this.locale,
    this.onOpenTarget,
    this.onEnableAndroidPush,
  });

  final InboxGateway gateway;
  final KairoLocale locale;
  final ValueChanged<String>? onOpenTarget;
  final Future<FcmRegistrationState> Function()? onEnableAndroidPush;

  @override
  State<InboxPage> createState() => _InboxPageState();
}

class _InboxPageState extends State<InboxPage> {
  NotificationInbox? _inbox;
  NotificationPreferences? _preferences;
  bool _loading = true;
  bool _failed = false;
  bool _savingPreferences = false;
  bool _enablingAndroidPush = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _failed = false;
    });
    try {
      final values = await Future.wait<Object>(<Future<Object>>[
        widget.gateway.load(),
        widget.gateway.preferences(),
      ]);
      if (!mounted) return;
      setState(() {
        _inbox = values[0] as NotificationInbox;
        _preferences = values[1] as NotificationPreferences;
      });
    } catch (_) {
      if (mounted) setState(() => _failed = true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _open(InboxNotification item) async {
    try {
      if (item.readAt == null) await widget.gateway.markRead(item.id);
      if (!mounted) return;
      widget.onOpenTarget?.call(item.targetPath);
      await _load();
    } catch (_) {
      if (mounted) _showFailure();
    }
  }

  Future<void> _markAllRead() async {
    try {
      await widget.gateway.markAllRead();
      await _load();
    } catch (_) {
      if (mounted) _showFailure();
    }
  }

  Future<void> _updatePreferences(NotificationPreferences values) async {
    if (_savingPreferences) return;
    setState(() => _savingPreferences = true);
    try {
      final saved = await widget.gateway.updatePreferences(values);
      if (mounted) setState(() => _preferences = saved);
    } catch (_) {
      if (mounted) _showFailure();
    } finally {
      if (mounted) setState(() => _savingPreferences = false);
    }
  }

  void _showFailure() => ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(_InboxText(widget.locale).actionFailure)),
  );

  Future<void> _enableAndroidPush() async {
    if (_enablingAndroidPush || widget.onEnableAndroidPush == null) return;
    setState(() => _enablingAndroidPush = true);
    try {
      final FcmRegistrationState result = await widget.onEnableAndroidPush!();
      if (!mounted) return;
      final String message = result.tokenRegistered
          ? _InboxText(widget.locale).androidPushEnabled
          : result.permissionGranted
          ? _InboxText(widget.locale).androidPushUnavailable
          : _InboxText(widget.locale).androidPushDenied;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    } catch (_) {
      if (mounted) _showFailure();
    } finally {
      if (mounted) setState(() => _enablingAndroidPush = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final text = _InboxText(widget.locale);
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _load,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: <Widget>[
              Row(
                children: <Widget>[
                  Expanded(
                    child: Text(
                      text.title,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                  ),
                  if ((_inbox?.unreadCount ?? 0) > 0)
                    TextButton(
                      onPressed: _markAllRead,
                      child: Text(text.markAll),
                    ),
                ],
              ),
              Text(text.intro),
              const SizedBox(height: 12),
              if (_preferences != null)
                _PreferencesCard(
                  text: text,
                  values: _preferences!,
                  saving: _savingPreferences,
                  onChanged: _updatePreferences,
                ),
              if (widget.onEnableAndroidPush != null) ...<Widget>[
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: _enablingAndroidPush ? null : _enableAndroidPush,
                  icon: _enablingAndroidPush
                      ? const SizedBox.square(
                          dimension: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.phone_android_outlined),
                  label: Text(text.enableAndroidPush),
                ),
              ],
              const SizedBox(height: 12),
              if (_loading)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: CircularProgressIndicator(),
                  ),
                )
              else if (_failed)
                _FeedbackCard(
                  text: text.failure,
                  onRetry: _load,
                  retry: text.retry,
                )
              else if (_inbox!.items.isEmpty)
                _FeedbackCard(text: text.empty)
              else
                ..._inbox!.items.map((item) => _item(context, item, text)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _item(BuildContext context, InboxNotification item, _InboxText text) =>
      Card(
        child: ListTile(
          leading: Icon(
            _iconFor(item.category),
            color: _colorFor(item.priority),
          ),
          title: Text(text.event(item.eventType)),
          subtitle: Text('${text.message(item.metadata)}\n${item.createdAt}'),
          trailing: item.readAt == null
              ? Icon(Icons.circle, size: 12, color: _colorFor(item.priority))
              : const Icon(Icons.chevron_right),
          onTap: () => _open(item),
        ),
      );

  IconData _iconFor(String category) => switch (category) {
    'finance' => Icons.account_balance_wallet_outlined,
    'discipline' => Icons.gavel_outlined,
    'events' => Icons.event_outlined,
    'announcements' => Icons.campaign_outlined,
    _ => Icons.notifications_outlined,
  };

  Color _colorFor(String priority) => switch (priority) {
    'critical' || 'high' => Colors.red.shade700,
    'medium' => Colors.orange.shade800,
    _ => Colors.blue.shade700,
  };
}

class _FeedbackCard extends StatelessWidget {
  const _FeedbackCard({required this.text, this.onRetry, this.retry});
  final String text;
  final VoidCallback? onRetry;
  final String? retry;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(text),
          if (onRetry != null)
            TextButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: Text(retry!),
            ),
        ],
      ),
    ),
  );
}

class _PreferencesCard extends StatelessWidget {
  const _PreferencesCard({
    required this.text,
    required this.values,
    required this.saving,
    required this.onChanged,
  });

  final _InboxText text;
  final NotificationPreferences values;
  final bool saving;
  final ValueChanged<NotificationPreferences> onChanged;

  @override
  Widget build(BuildContext context) => Card(
    child: ExpansionTile(
      leading: const Icon(Icons.tune_outlined),
      title: Text(text.preferences),
      subtitle: Text(text.preferencesLead),
      children: <Widget>[
        _switch(
          text.push,
          values.pushEnabled,
          (value) => onChanged(values.copyWith(pushEnabled: value)),
        ),
        _switch(
          text.finance,
          values.financeEnabled,
          (value) => onChanged(values.copyWith(financeEnabled: value)),
        ),
        _switch(
          text.discipline,
          values.disciplineEnabled,
          (value) => onChanged(values.copyWith(disciplineEnabled: value)),
        ),
        _switch(
          text.events,
          values.eventsEnabled,
          (value) => onChanged(values.copyWith(eventsEnabled: value)),
        ),
        _switch(
          text.announcements,
          values.announcementsEnabled,
          (value) => onChanged(values.copyWith(announcementsEnabled: value)),
        ),
        if (saving) const LinearProgressIndicator(),
      ],
    ),
  );

  Widget _switch(String label, bool value, ValueChanged<bool> onChanged) =>
      SwitchListTile(
        title: Text(label),
        value: value,
        onChanged: saving ? null : onChanged,
      );
}

class _InboxText {
  const _InboxText(this.locale);
  final KairoLocale locale;
  bool get _isEnglish => locale == KairoLocale.en;
  bool get _isGerman => locale == KairoLocale.de;
  String get title => _isEnglish
      ? 'Notifications'
      : _isGerman
      ? 'Benachrichtigungen'
      : 'Notifications';
  String get markAll => _isEnglish
      ? 'Mark all as read'
      : _isGerman
      ? 'Alle als gelesen markieren'
      : 'Tout marquer comme lu';
  String get intro => _isEnglish
      ? 'Important updates assigned to your account.'
      : _isGerman
      ? 'Wichtige, Ihrem Konto zugeordnete Aktualisierungen.'
      : 'Les mises à jour importantes attribuées à votre compte.';
  String get failure => _isEnglish
      ? 'Notifications could not be loaded.'
      : _isGerman
      ? 'Benachrichtigungen konnten nicht geladen werden.'
      : 'Les notifications n’ont pas pu être chargées.';
  String get actionFailure => _isEnglish
      ? 'The notification action could not be completed.'
      : _isGerman
      ? 'Die Benachrichtigungsaktion konnte nicht abgeschlossen werden.'
      : 'L’action de notification n’a pas pu être réalisée.';
  String get empty => _isEnglish
      ? 'No notifications for now.'
      : _isGerman
      ? 'Derzeit keine Benachrichtigungen.'
      : 'Aucune notification pour le moment.';
  String get retry => _isEnglish
      ? 'Retry'
      : _isGerman
      ? 'Erneut versuchen'
      : 'Réessayer';
  String get preferences => _isEnglish
      ? 'Notification preferences'
      : _isGerman
      ? 'Benachrichtigungseinstellungen'
      : 'Préférences de notification';
  String get preferencesLead => _isEnglish
      ? 'Choose the operational updates you want to receive.'
      : _isGerman
      ? 'Wählen Sie die operativen Aktualisierungen aus, die Sie erhalten möchten.'
      : 'Choisissez les mises à jour opérationnelles que vous souhaitez recevoir.';
  String get push => _isEnglish
      ? 'Push delivery'
      : _isGerman
      ? 'Push-Zustellung'
      : 'Réception push';
  String get finance => _isEnglish
      ? 'Finance'
      : _isGerman
      ? 'Finanzen'
      : 'Finances';
  String get discipline => _isEnglish
      ? 'Discipline'
      : _isGerman
      ? 'Disziplin'
      : 'Discipline';
  String get events => _isEnglish
      ? 'Events'
      : _isGerman
      ? 'Ereignisse'
      : 'Événements';
  String get announcements => _isEnglish
      ? 'Announcements'
      : _isGerman
      ? 'Ankündigungen'
      : 'Annonces';
  String get enableAndroidPush => _isEnglish
      ? 'Enable Android notifications'
      : _isGerman
      ? 'Android-Benachrichtigungen aktivieren'
      : 'Activer les notifications Android';
  String get androidPushEnabled => _isEnglish
      ? 'Android notifications are enabled for this account.'
      : _isGerman
      ? 'Android-Benachrichtigungen sind für dieses Konto aktiviert.'
      : 'Les notifications Android sont activées pour ce compte.';
  String get androidPushDenied => _isEnglish
      ? 'Notification permission was not granted.'
      : _isGerman
      ? 'Die Benachrichtigungsberechtigung wurde nicht erteilt.'
      : 'L’autorisation de notification n’a pas été accordée.';
  String get androidPushUnavailable => _isEnglish
      ? 'Android notifications are temporarily unavailable.'
      : _isGerman
      ? 'Android-Benachrichtigungen sind vorübergehend nicht verfügbar.'
      : 'Les notifications Android sont temporairement indisponibles.';
  String event(String value) {
    const labels = <String, List<String>>{
      'receipt_validated': <String>[
        'Receipt validated',
        'Einnahme bestätigt',
        'Encaissement validé',
      ],
      'receipt_rejected': <String>[
        'Receipt rejected',
        'Einnahme abgelehnt',
        'Encaissement rejeté',
      ],
      'cash_handover_due': <String>[
        'Cash handover reminder',
        'Erinnerung zur Kassenübergabe',
        'Rappel de remise en caisse',
      ],
      'disciplinary_record_created': <String>[
        'Disciplinary record created',
        'Disziplinarakte erstellt',
        'Dossier disciplinaire créé',
      ],
    };
    final label = labels[value];
    return label == null
        ? value.replaceAll('_', ' ')
        : label[_isEnglish
              ? 0
              : _isGerman
              ? 1
              : 2];
  }

  String message(Map<String, dynamic> metadata) =>
      metadata['message']?.toString() ??
      (_isEnglish
          ? 'Open this notification for its details.'
          : _isGerman
          ? 'Öffnen Sie diese Benachrichtigung für Details.'
          : 'Ouvrez cette notification pour voir les détails.');
}
