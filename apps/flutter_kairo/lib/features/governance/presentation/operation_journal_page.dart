import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../data/operation_journal_gateway.dart';

class OperationJournalPage extends StatefulWidget {
  const OperationJournalPage({
    super.key,
    required this.gateway,
    required this.locale,
  });
  final OperationJournalGateway gateway;
  final KairoLocale locale;
  @override
  State<OperationJournalPage> createState() => _OperationJournalPageState();
}

class _OperationJournalPageState extends State<OperationJournalPage> {
  List<OperationJournalEntry> entries = const <OperationJournalEntry>[];
  bool loading = true;
  bool failed = false;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    setState(() {
      loading = true;
      failed = false;
    });
    try {
      entries = await widget.gateway.load();
    } catch (_) {
      failed = true;
    }
    if (mounted) setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    final _JournalText text = _JournalText(widget.locale);
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: load,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: <Widget>[
              Text(
                text.title,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              Text(text.intro),
              const SizedBox(height: 16),
              if (loading)
                const Center(child: CircularProgressIndicator())
              else if (failed)
                Card(
                  child: Padding(
                    padding: EdgeInsets.all(18),
                    child: Text(text.failure),
                  ),
                )
              else if (entries.isEmpty)
                Card(
                  child: Padding(
                    padding: EdgeInsets.all(18),
                    child: Text(text.empty),
                  ),
                )
              else ...<Widget>[
                for (final OperationJournalEntry entry in entries)
                  _entry(entry, text),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _entry(OperationJournalEntry entry, _JournalText text) => Card(
    child: ListTile(
      title: Text(text.action(entry.action)),
      subtitle: Text(
        '${entry.actorName ?? text.system} · ${text.roles(entry.actorRoles)}\n${_details(entry.details, text)}\n${entry.createdAt}',
      ),
      isThreeLine: true,
    ),
  );

  String _details(Map<String, dynamic> details, _JournalText text) {
    if (details.isEmpty) return text.noDetails;
    return details.entries
        .map(
          (MapEntry<String, dynamic> entry) =>
              '${text.detailKey(entry.key)} : ${entry.value}',
        )
        .join(' · ');
  }
}

class _JournalText {
  const _JournalText(this.locale);
  final KairoLocale locale;
  bool get en => locale == KairoLocale.en;
  bool get de => locale == KairoLocale.de;
  String get title => en
      ? 'Operation journal'
      : de
      ? 'Vorgangsjournal'
      : 'Journal des opérations';
  String get intro => en
      ? 'Human-readable activity for authorised association roles.'
      : de
      ? 'Verständliche Aktivitäten für berechtigte Vereinsrollen.'
      : 'Activité compréhensible pour les rôles autorisés de l’association.';
  String get failure => en
      ? 'The journal could not be loaded.'
      : de
      ? 'Das Journal konnte nicht geladen werden.'
      : 'Le journal n’a pas pu être chargé.';
  String get empty => en
      ? 'No operation is available.'
      : de
      ? 'Keine Vorgänge verfügbar.'
      : 'Aucune opération disponible.';
  String get system => en
      ? 'Association system'
      : de
      ? 'Vereinssystem'
      : 'Système de l’association';
  String get noDetails => en
      ? 'No additional details.'
      : de
      ? 'Keine zusätzlichen Details.'
      : 'Aucun détail complémentaire.';
  String action(String value) {
    const Map<String, List<String>> labels = <String, List<String>>{
      'receipt_declared': <String>[
        'Receipt declared',
        'Einnahme gemeldet',
        'Encaissement déclaré',
      ],
      'receipt_validated': <String>[
        'Receipt validated by treasurer',
        'Einnahme vom Schatzmeister bestätigt',
        'Encaissement validé par le trésorier',
      ],
      'receipt_rejected': <String>[
        'Receipt rejected by treasurer',
        'Einnahme vom Schatzmeister abgelehnt',
        'Encaissement rejeté par le trésorier',
      ],
      'treasury_receipt_confirmed': <String>[
        'Cash received in association treasury',
        'Geld in der Vereinskasse bestätigt',
        'Remise en caisse confirmée',
      ],
      'disciplinary_record_created': <String>[
        'Disciplinary record created',
        'Disziplinarakte erstellt',
        'Dossier disciplinaire créé',
      ],
    };
    final List<String>? label = labels[value];
    return label == null
        ? value.replaceAll('_', ' ')
        : label[en
              ? 0
              : de
              ? 1
              : 2];
  }

  String roles(List<String> values) => values.isEmpty
      ? system
      : values.map((String role) => role.replaceAll('_', ' ')).join(', ');
  String detailKey(String value) {
    const Map<String, List<String>> labels = <String, List<String>>{
      'member': <String>['Member', 'Mitglied', 'Membre'],
      'amount': <String>['Amount', 'Betrag', 'Montant'],
      'result': <String>['Result', 'Ergebnis', 'Résultat'],
      'reason': <String>['Reason', 'Begründung', 'Motif'],
    };
    final List<String>? label = labels[value];
    return label == null
        ? value.replaceAll('_', ' ')
        : label[en
              ? 0
              : de
              ? 1
              : 2];
  }
}
