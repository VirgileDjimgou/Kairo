import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../../../app/theme/kairo_theme.dart';
import '../../members/data/member_gateway.dart';
import '../../members/data/member_models.dart';
import '../data/governance_gateway.dart';

class GovernanceWorkspacePage extends StatefulWidget {
  const GovernanceWorkspacePage({
    super.key,
    required this.gateway,
    required this.memberGateway,
    required this.locale,
    required this.roles,
  });
  final GovernanceGateway gateway;
  final MemberGateway memberGateway;
  final KairoLocale locale;
  final List<String> roles;
  @override
  State<GovernanceWorkspacePage> createState() =>
      _GovernanceWorkspacePageState();
}

class _GovernanceWorkspacePageState extends State<GovernanceWorkspacePage>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs = TabController(length: 5, vsync: this);
  late final _Text text = _Text(widget.locale);
  bool get _censor => widget.roles.contains('censor');
  bool get _recovery => widget.roles.any(
    <String>['principal_admin', 'president', 'secretary_general'].contains,
  );
  bool _loading = true;
  String? _error;
  List<DisciplineRecord> _records = <DisciplineRecord>[];
  List<GovernanceItem> _policies = <GovernanceItem>[],
      _documents = <GovernanceItem>[],
      _events = <GovernanceItem>[],
      _announcements = <GovernanceItem>[];
  BackupOverview? _backup;
  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final values = await Future.wait<Object>(<Future<Object>>[
        widget.gateway.discipline(
          ownOnly:
              !_censor &&
              !widget.roles.any(
                <String>[
                  'president',
                  'secretary_general',
                  'principal_admin',
                ].contains,
              ),
        ),
        widget.gateway.policies(),
        widget.gateway.documents(),
        widget.gateway.events(),
        widget.gateway.announcements(),
        if (_recovery) widget.gateway.backupOverview(),
      ]);
      if (!mounted) return;
      setState(() {
        _records = values[0] as List<DisciplineRecord>;
        _policies = values[1] as List<GovernanceItem>;
        _documents = values[2] as List<GovernanceItem>;
        _events = values[3] as List<GovernanceItem>;
        _announcements = values[4] as List<GovernanceItem>;
        _backup = _recovery ? values[5] as BackupOverview : null;
      });
    } catch (error) {
      if (mounted) setState(() => _error = '$error');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? _Error(text: text, error: _error!, onRetry: _load)
          : Column(
              children: <Widget>[
                _Header(text: text, censor: _censor, onRefresh: _load),
                TabBar(
                  controller: _tabs,
                  isScrollable: true,
                  tabs: <Widget>[
                    Tab(text: text.discipline),
                    Tab(text: text.policies),
                    Tab(text: text.documents),
                    Tab(text: text.events),
                    Tab(text: text.announcements),
                  ],
                ),
                Expanded(
                  child: TabBarView(
                    controller: _tabs,
                    children: <Widget>[
                      _DisciplineTab(
                        text: text,
                        records: _records,
                        writable: _censor,
                        gateway: widget.gateway,
                        memberGateway: widget.memberGateway,
                        onChanged: _load,
                      ),
                      _ItemsTab(
                        title: text.policies,
                        items: _policies,
                        text: text,
                      ),
                      _ItemsTab(
                        title: text.documents,
                        items: _documents,
                        text: text,
                        canUpload:
                            widget.gateway is DocumentUploadGateway &&
                            widget.roles.any(
                              <String>[
                                'principal_admin',
                                'secretary_general',
                              ].contains,
                            ),
                        onUpload: _uploadDocument,
                      ),
                      _ItemsTab(title: text.events, items: _events, text: text),
                      _ItemsTab(
                        title: text.announcements,
                        items: _announcements,
                        text: text,
                        backup: _backup,
                        onBackup: _requestBackup,
                      ),
                    ],
                  ),
                ),
              ],
            ),
    ),
  );
  Future<void> _uploadDocument() async {
    final DocumentUploadGateway? uploader =
        widget.gateway is DocumentUploadGateway
        ? widget.gateway as DocumentUploadGateway
        : null;
    if (uploader == null) return;
    final FilePickerResult? selected = await FilePicker.platform.pickFiles(
      withData: true,
      allowMultiple: false,
    );
    if (selected == null || selected.files.single.bytes == null) return;
    final PlatformFile file = selected.files.single;
    final String title = file.name.replaceFirst(RegExp(r'\\.[^.]+$'), '');
    try {
      await uploader.uploadDocument(
        filename: file.name,
        bytes: file.bytes!,
        title: title,
      );
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(text.uploaded)));
      }
      await _load();
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(text.uploadFailed)));
      }
    }
  }

  Future<void> _requestBackup() async {
    final bool? confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(text.backup),
        content: Text(text.backupConfirm),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(text.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(text.confirm),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await widget.gateway.requestBackup('Flutter governance workspace');
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(text.backupQueued)));
      }
      await _load();
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('$error')));
      }
    }
  }
}

class _Header extends StatelessWidget {
  const _Header({
    required this.text,
    required this.censor,
    required this.onRefresh,
  });
  final _Text text;
  final bool censor;
  final VoidCallback onRefresh;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
    child: Row(
      children: <Widget>[
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(text.kicker, style: Theme.of(context).textTheme.labelLarge),
              Text(
                text.title,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              Text(censor ? text.writeLead : text.readLead),
            ],
          ),
        ),
        IconButton(
          onPressed: onRefresh,
          icon: const Icon(Icons.refresh),
          tooltip: text.refresh,
        ),
      ],
    ),
  );
}

class _Error extends StatelessWidget {
  const _Error({
    required this.text,
    required this.error,
    required this.onRetry,
  });
  final _Text text;
  final String error;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          const Icon(Icons.error_outline, color: KairoColors.danger),
          const SizedBox(height: 8),
          Text(text.unavailable, style: Theme.of(context).textTheme.titleLarge),
          Text(error, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh),
            label: Text(text.retry),
          ),
        ],
      ),
    ),
  );
}

class _ItemsTab extends StatelessWidget {
  const _ItemsTab({
    required this.title,
    required this.items,
    required this.text,
    this.backup,
    this.onBackup,
    this.canUpload = false,
    this.onUpload,
  });
  final String title;
  final List<GovernanceItem> items;
  final _Text text;
  final BackupOverview? backup;
  final VoidCallback? onBackup;
  final bool canUpload;
  final VoidCallback? onUpload;
  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.all(20),
    children: <Widget>[
      if (backup != null)
        _BackupCard(text: text, backup: backup!, onBackup: onBackup!),
      Row(
        children: <Widget>[
          Expanded(
            child: Text(title, style: Theme.of(context).textTheme.titleLarge),
          ),
          if (canUpload)
            FilledButton.icon(
              onPressed: onUpload,
              icon: const Icon(Icons.upload_file_outlined),
              label: Text(text.importDocument),
            ),
        ],
      ),
      const SizedBox(height: 10),
      if (items.isEmpty)
        _Empty(text: text)
      else
        ...items.map(
          (item) => Card(
            child: ListTile(
              title: Text(item.title),
              subtitle: Text(
                [item.body, item.meta].where((v) => v.isNotEmpty).join('\n'),
              ),
              trailing: _Status(value: item.status),
            ),
          ),
        ),
    ],
  );
}

class _BackupCard extends StatelessWidget {
  const _BackupCard({
    required this.text,
    required this.backup,
    required this.onBackup,
  });
  final _Text text;
  final BackupOverview backup;
  final VoidCallback onBackup;
  @override
  Widget build(BuildContext context) => Card(
    color: const Color(0xFFE8F1FD),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(text.backup, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Text(
            '${text.retention}: ${backup.retention} ${text.days} · ${text.runs}: ${backup.runCount}',
          ),
          Text(
            '${text.external}: ${backup.externalStorage ? text.enabled : text.disabled} · PITR: ${backup.pitr ? text.enabled : text.disabled}',
          ),
          const SizedBox(height: 10),
          FilledButton.icon(
            onPressed: onBackup,
            icon: const Icon(Icons.backup_outlined),
            label: Text(text.createBackup),
          ),
        ],
      ),
    ),
  );
}

class _Empty extends StatelessWidget {
  const _Empty({required this.text});
  final _Text text;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(24),
    child: Text(text.empty, textAlign: TextAlign.center),
  );
}

class _Status extends StatelessWidget {
  const _Status({required this.value});
  final String value;
  @override
  Widget build(BuildContext context) {
    final bool open = value == 'open' || value == 'published';
    return Chip(
      label: Text(value.replaceAll('_', ' ')),
      backgroundColor: open ? const Color(0xFFDDF3E7) : const Color(0xFFFFF0C9),
    );
  }
}

class _DisciplineTab extends StatefulWidget {
  const _DisciplineTab({
    required this.text,
    required this.records,
    required this.writable,
    required this.gateway,
    required this.memberGateway,
    required this.onChanged,
  });
  final _Text text;
  final List<DisciplineRecord> records;
  final bool writable;
  final GovernanceGateway gateway;
  final MemberGateway memberGateway;
  final Future<void> Function() onChanged;
  @override
  State<_DisciplineTab> createState() => _DisciplineTabState();
}

class _DisciplineTabState extends State<_DisciplineTab> {
  String _query = '';
  final _title = TextEditingController();
  final _description = TextEditingController();
  final _amount = TextEditingController();
  MemberProfile? _member;
  List<MemberProfile> _options = <MemberProfile>[];
  @override
  void dispose() {
    _title.dispose();
    _description.dispose();
    _amount.dispose();
    super.dispose();
  }

  Future<void> _search(String value) async {
    setState(() => _query = value);
    if (value.trim().length < 2) {
      return setState(() => _options = <MemberProfile>[]);
    }
    try {
      final results = await widget.memberGateway.list(query: value);
      if (mounted) setState(() => _options = results.take(6).toList());
    } catch (_) {}
  }

  Future<void> _create() async {
    final amount = double.tryParse(_amount.text.replaceAll(',', '.'));
    if (_member == null || _title.text.trim().isEmpty || amount == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(widget.text.disciplineInvalid)));
      return;
    }
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(widget.text.confirm),
        content: Text(widget.text.disciplineConfirm),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(widget.text.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(widget.text.confirm),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await widget.gateway.createDiscipline(<String, dynamic>{
        'membership_profile_id': _member!.id,
        'title': _title.text.trim(),
        'description': _description.text.trim(),
        'amount': amount,
        'currency': 'EUR',
        'status': 'open',
      });
      if (!mounted) return;
      _title.clear();
      _description.clear();
      _amount.clear();
      setState(() => _member = null);
      await widget.onChanged();
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('$error')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final visible = widget.records
        .where(
          (r) =>
              _query.isEmpty ||
              '${r.memberName} ${r.title} ${r.description}'
                  .toLowerCase()
                  .contains(_query.toLowerCase()),
        )
        .toList();
    return ListView(
      padding: const EdgeInsets.all(20),
      children: <Widget>[
        Text(
          widget.writable
              ? widget.text.disciplineWrite
              : widget.text.disciplineRead,
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 10),
        TextField(
          onChanged: (v) {
            setState(() => _query = v);
            if (widget.writable) _search(v);
          },
          decoration: InputDecoration(
            prefixIcon: const Icon(Icons.search),
            hintText: widget.text.search,
          ),
        ),
        if (widget.writable) ...<Widget>[
          const SizedBox(height: 10),
          if (_options.isNotEmpty)
            Card(
              child: Column(
                children: _options
                    .map(
                      (m) => ListTile(
                        title: Text(m.displayName),
                        subtitle: Text(m.memberCode),
                        onTap: () => setState(() {
                          _member = m;
                          _options = <MemberProfile>[];
                          _query = '';
                        }),
                      ),
                    )
                    .toList(),
              ),
            ),
          if (_member != null)
            Chip(label: Text('${widget.text.member}: ${_member!.displayName}')),
          TextField(
            controller: _title,
            decoration: InputDecoration(labelText: widget.text.recordTitle),
          ),
          TextField(
            controller: _description,
            decoration: InputDecoration(labelText: widget.text.context),
          ),
          TextField(
            controller: _amount,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(labelText: widget.text.amount),
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            onPressed: _create,
            icon: const Icon(Icons.gavel_outlined),
            label: Text(widget.text.createRecord),
          ),
        ],
        const SizedBox(height: 16),
        if (visible.isEmpty)
          _Empty(text: widget.text)
        else
          ...visible.map(
            (r) => Card(
              child: ListTile(
                title: Text(r.title),
                subtitle: Text(
                  '${r.memberName}\n${r.description}\n${r.recordedAt.toLocal().toString().substring(0, 10)} · ${r.status.replaceAll('_', ' ')}',
                ),
                isThreeLine: true,
                trailing: Text(
                  '${r.amount}\n${r.currency}',
                  textAlign: TextAlign.end,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _Text {
  const _Text(this.locale);
  final KairoLocale locale;
  bool get en => locale == KairoLocale.en;
  bool get de => locale == KairoLocale.de;
  String get kicker => en
      ? 'GOVERNANCE'
      : de
      ? 'GOVERNANCE'
      : 'GOUVERNANCE';
  String get title => en
      ? 'Association workspaces'
      : de
      ? 'Vereinsbereiche'
      : 'Espaces de l’association';
  String get readLead => en
      ? 'Consult authorised information in read-only mode.'
      : de
      ? 'Autorisierte Informationen schreibgeschützt einsehen.'
      : 'Consultez les informations autorisées en lecture seule.';
  String get writeLead => en
      ? 'Manage disciplinary records within your authorised scope.'
      : de
      ? 'Verwalten Sie Disziplinarakten innerhalb Ihres Berechtigungsbereichs.'
      : 'Gérez les dossiers disciplinaires dans votre périmètre autorisé.';
  String get discipline => en
      ? 'Discipline'
      : de
      ? 'Disziplin'
      : 'Discipline';
  String get policies => en
      ? 'Policies'
      : de
      ? 'Regeln'
      : 'Règles';
  String get documents => en
      ? 'Documents'
      : de
      ? 'Dokumente'
      : 'Documents';
  String get events => en
      ? 'Events'
      : de
      ? 'Veranstaltungen'
      : 'Événements';
  String get announcements => en
      ? 'Announcements'
      : de
      ? 'Ankündigungen'
      : 'Annonces';
  String get disciplineWrite => en
      ? 'Disciplinary records'
      : de
      ? 'Disziplinarakten'
      : 'Dossiers disciplinaires';
  String get disciplineRead => en
      ? 'My disciplinary history'
      : de
      ? 'Mein Disziplinarverlauf'
      : 'Mon historique disciplinaire';
  String get search => en
      ? 'Search member, title or context'
      : de
      ? 'Mitglied, Titel oder Kontext suchen'
      : 'Rechercher un membre, un titre ou un contexte';
  String get member => en
      ? 'Member'
      : de
      ? 'Mitglied'
      : 'Membre';
  String get recordTitle => en
      ? 'Sanction title'
      : de
      ? 'Titel der Sanktion'
      : 'Titre de la sanction';
  String get context => en
      ? 'Context'
      : de
      ? 'Kontext'
      : 'Contexte';
  String get amount => en
      ? 'Amount (EUR)'
      : de
      ? 'Betrag (EUR)'
      : 'Montant (EUR)';
  String get createRecord => en
      ? 'Create disciplinary record'
      : de
      ? 'Disziplinarakte erstellen'
      : 'Créer le dossier disciplinaire';
  String get disciplineInvalid => en
      ? 'Select a member and enter a valid title and amount.'
      : de
      ? 'Wählen Sie ein Mitglied und geben Sie Titel und Betrag ein.'
      : 'Sélectionnez un membre et saisissez un titre et un montant valides.';
  String get disciplineConfirm => en
      ? 'Create this disciplinary record?'
      : de
      ? 'Diese Disziplinarakte erstellen?'
      : 'Créer ce dossier disciplinaire ?';
  String get backup => en
      ? 'Backup centre'
      : de
      ? 'Sicherungszentrum'
      : 'Centre de sauvegarde';
  String get backupConfirm => en
      ? 'Queue a verified encrypted backup?'
      : de
      ? 'Eine verifizierte verschlüsselte Sicherung anfordern?'
      : 'Demander une sauvegarde chiffrée et vérifiée ?';
  String get createBackup => en
      ? 'Create backup'
      : de
      ? 'Sicherung erstellen'
      : 'Créer une sauvegarde';
  String get backupQueued => en
      ? 'Backup request queued.'
      : de
      ? 'Sicherungsauftrag eingeplant.'
      : 'Demande de sauvegarde envoyée.';
  String get retention => en
      ? 'Retention'
      : de
      ? 'Aufbewahrung'
      : 'Rétention';
  String get days => en
      ? 'days'
      : de
      ? 'Tage'
      : 'jours';
  String get runs => en
      ? 'runs'
      : de
      ? 'Läufe'
      : 'sauvegardes';
  String get external => en
      ? 'External storage'
      : de
      ? 'Externer Speicher'
      : 'Stockage externe';
  String get enabled => en
      ? 'enabled'
      : de
      ? 'aktiv'
      : 'activé';
  String get disabled => en
      ? 'disabled'
      : de
      ? 'deaktiviert'
      : 'désactivé';
  String get importDocument => en
      ? 'Import document'
      : de
      ? 'Dokument importieren'
      : 'Importer un document';
  String get uploaded => en
      ? 'Document queued for ingestion.'
      : de
      ? 'Dokument zur Verarbeitung eingereiht.'
      : 'Document envoyé pour traitement.';
  String get uploadFailed => en
      ? 'The document could not be imported.'
      : de
      ? 'Das Dokument konnte nicht importiert werden.'
      : 'Le document n’a pas pu être importé.';
  String get empty => en
      ? 'Nothing is available here yet.'
      : de
      ? 'Hier ist noch nichts verfügbar.'
      : 'Aucun élément disponible pour le moment.';
  String get unavailable => en
      ? 'Governance workspace unavailable'
      : de
      ? 'Governance-Bereich nicht verfügbar'
      : 'Espace de gouvernance indisponible';
  String get retry => en
      ? 'Retry'
      : de
      ? 'Erneut versuchen'
      : 'Réessayer';
  String get refresh => en
      ? 'Refresh'
      : de
      ? 'Aktualisieren'
      : 'Actualiser';
  String get cancel => en
      ? 'Cancel'
      : de
      ? 'Abbrechen'
      : 'Annuler';
  String get confirm => en
      ? 'Confirm'
      : de
      ? 'Bestätigen'
      : 'Confirmer';
}
