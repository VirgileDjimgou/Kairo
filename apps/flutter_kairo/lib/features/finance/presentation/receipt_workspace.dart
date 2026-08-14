import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../../../app/theme/kairo_theme.dart';
import '../../../core/offline/offline_workspace_controller.dart';
import '../data/receipt_gateway.dart';
import 'receipt_controller.dart';

class ReceiptWorkspace extends StatefulWidget {
  const ReceiptWorkspace({
    super.key,
    required this.gateway,
    required this.controller,
    required this.canProcess,
    required this.locale,
    this.offlineWorkspace,
  });
  final ReceiptGateway gateway;
  final ReceiptController controller;
  final bool canProcess;
  final KairoLocale locale;
  final OfflineWorkspaceController? offlineWorkspace;
  @override
  State<ReceiptWorkspace> createState() => _ReceiptWorkspaceState();
}

class _ReceiptWorkspaceState extends State<ReceiptWorkspace> {
  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_changed);
    widget.controller.load(review: widget.canProcess);
  }

  @override
  void dispose() {
    widget.controller.removeListener(_changed);
    super.dispose();
  }

  void _changed() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final _FinanceText text = _FinanceText(widget.locale);
    final List<ReceiptDeclaration> items = widget.canProcess
        ? widget.controller.reviewItems
        : widget.controller.mineItems;
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () => widget.controller.load(review: widget.canProcess),
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: <Widget>[
              Text(
                widget.canProcess ? text.finance : text.declare,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(widget.canProcess ? text.financeBody : text.declareBody),
              const SizedBox(height: 20),
              if (!widget.canProcess)
                _NewReceipt(
                  gateway: widget.gateway,
                  controller: widget.controller,
                  text: text,
                  offlineWorkspace: widget.offlineWorkspace,
                ),
              if (widget.canProcess)
                _TreasuryIntro(
                  text: text,
                  count: items
                      .where(
                        (ReceiptDeclaration value) =>
                            value.status == 'submitted',
                      )
                      .length,
                ),
              const SizedBox(height: 16),
              if (widget.controller.loading)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(28),
                    child: CircularProgressIndicator(),
                  ),
                )
              else if (widget.controller.error != null)
                _Notice(text.loadFailed, error: true)
              else if (items.isEmpty)
                _Notice(text.empty, error: false)
              else
                ...items.map(
                  (ReceiptDeclaration item) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _ReceiptCard(
                      receipt: item,
                      canProcess: widget.canProcess,
                      controller: widget.controller,
                      text: text,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TreasuryIntro extends StatelessWidget {
  const _TreasuryIntro({required this.text, required this.count});
  final _FinanceText text;
  final int count;
  @override
  Widget build(BuildContext context) => Card(
    color: const Color(0xffeff6ff),
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Row(
        children: <Widget>[
          const Icon(
            Icons.account_balance_wallet_outlined,
            color: KairoColors.primary,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  text.validation,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(text.validationBody),
              ],
            ),
          ),
          Chip(label: Text('$count')),
        ],
      ),
    ),
  );
}

class _NewReceipt extends StatefulWidget {
  const _NewReceipt({
    required this.gateway,
    required this.controller,
    required this.text,
    this.offlineWorkspace,
  });
  final ReceiptGateway gateway;
  final ReceiptController controller;
  final _FinanceText text;
  final OfflineWorkspaceController? offlineWorkspace;
  @override
  State<_NewReceipt> createState() => _NewReceiptState();
}

class _NewReceiptState extends State<_NewReceipt> {
  final TextEditingController _amount = TextEditingController();
  final TextEditingController _source = TextEditingController();
  final TextEditingController _note = TextEditingController();
  final TextEditingController _search = TextEditingController();
  String _type = 'membership_contribution';
  String? _memberId;
  List<ReceiptMemberOption> _options = const <ReceiptMemberOption>[];
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _search.addListener(_findMembers);
    _restoreDraft();
  }

  @override
  void dispose() {
    _amount.dispose();
    _source.dispose();
    _note.dispose();
    _search.dispose();
    super.dispose();
  }

  Future<void> _findMembers() async {
    if (_type != 'membership_contribution') return;
    try {
      final List<ReceiptMemberOption> result = await widget.gateway
          .memberOptions(query: _search.text);
      if (mounted) setState(() => _options = result);
    } catch (_) {
      // The backend remains responsible for permissions and availability.
    }
  }

  Future<void> _restoreDraft() async {
    final values = await widget.offlineWorkspace?.readDraft('receipt');
    if (!mounted || values == null) return;
    setState(() {
      _type = values['income_type'] as String? ?? _type;
      _amount.text = values['amount'] as String? ?? '';
      _source.text = values['source_name'] as String? ?? '';
      _note.text = values['note'] as String? ?? '';
    });
  }

  void _saveDraft() {
    widget.offlineWorkspace?.saveDraft('receipt', <String, dynamic>{
      'income_type': _type,
      'amount': _amount.text,
      'source_name': _source.text,
      'note': _note.text,
    });
  }

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Text(
            widget.text.newDeclaration,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Text(widget.text.newDeclarationBody),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            initialValue: _type,
            decoration: InputDecoration(labelText: widget.text.incomeType),
            items: <DropdownMenuItem<String>>[
              DropdownMenuItem(
                value: 'membership_contribution',
                child: Text(widget.text.contribution),
              ),
              DropdownMenuItem(
                value: 'donation',
                child: Text(widget.text.donation),
              ),
              DropdownMenuItem(
                value: 'sponsorship',
                child: Text(widget.text.sponsorship),
              ),
              DropdownMenuItem(
                value: 'tournament_proceeds',
                child: Text(widget.text.tournament),
              ),
              DropdownMenuItem(
                value: 'other_income',
                child: Text(widget.text.otherIncome),
              ),
            ],
            onChanged: (String? value) => setState(() {
              _type = value!;
              _memberId = null;
              _options = const <ReceiptMemberOption>[];
              _saveDraft();
            }),
          ),
          const SizedBox(height: 12),
          if (_type == 'membership_contribution') ...<Widget>[
            TextField(
              controller: _search,
              decoration: InputDecoration(
                labelText: widget.text.memberSearch,
                prefixIcon: const Icon(Icons.search),
              ),
            ),
            if (_options.isNotEmpty)
              Container(
                margin: const EdgeInsets.only(top: 6),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.blueGrey.shade100),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: _options
                      .take(5)
                      .map(
                        (ReceiptMemberOption option) => ListTile(
                          title: Text(option.label),
                          trailing: _memberId == option.id
                              ? const Icon(
                                  Icons.check,
                                  color: KairoColors.success,
                                )
                              : null,
                          onTap: () => setState(() {
                            _memberId = option.id;
                            _search.text = option.label;
                            _options = const <ReceiptMemberOption>[];
                          }),
                        ),
                      )
                      .toList(),
                ),
              ),
          ] else
            TextField(
              controller: _source,
              decoration: InputDecoration(labelText: widget.text.source),
            ),
          const SizedBox(height: 12),
          TextField(
            controller: _amount,
            onChanged: (_) => _saveDraft(),
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: InputDecoration(labelText: widget.text.amount),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _note,
            onChanged: (_) => _saveDraft(),
            minLines: 2,
            maxLines: 4,
            decoration: InputDecoration(labelText: widget.text.note),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: _saving ? null : _submit,
            icon: const Icon(Icons.send_outlined),
            label: Text(_saving ? widget.text.saving : widget.text.submit),
          ),
        ],
      ),
    ),
  );

  Future<void> _submit() async {
    final double? amount = double.tryParse(
      _amount.text.trim().replaceAll(',', '.'),
    );
    final bool validSource = _type == 'membership_contribution'
        ? _memberId != null
        : _source.text.trim().isNotEmpty;
    if (amount == null || amount <= 0 || !validSource) {
      _feedback(widget.text.requiredFields, error: true);
      return;
    }
    setState(() => _saving = true);
    try {
      await widget.controller.declare(<String, dynamic>{
        'income_type': _type,
        if (_memberId != null) 'membership_profile_id': _memberId,
        if (_type != 'membership_contribution')
          'source_name': _source.text.trim(),
        'amount': amount.toStringAsFixed(2),
        'currency': 'EUR',
        'payment_method': 'cash',
        if (_note.text.trim().isNotEmpty) 'note': _note.text.trim(),
      });
      _amount.clear();
      _source.clear();
      _note.clear();
      _search.clear();
      await widget.offlineWorkspace?.clearDraft('receipt');
      setState(() => _memberId = null);
      _feedback(widget.text.sent, error: false);
    } catch (_) {
      _feedback(widget.text.operationFailed, error: true);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  void _feedback(String message, {required bool error}) =>
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: error ? Colors.red.shade700 : KairoColors.success,
        ),
      );
}

class _ReceiptCard extends StatelessWidget {
  const _ReceiptCard({
    required this.receipt,
    required this.canProcess,
    required this.controller,
    required this.text,
  });
  final ReceiptDeclaration receipt;
  final bool canProcess;
  final ReceiptController controller;
  final _FinanceText text;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: Text(
                  '${receipt.amount} EUR',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              _StatusChip(status: receipt.status, text: text),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            text.incomeLabel(receipt.incomeType),
            style: Theme.of(context).textTheme.titleMedium,
          ),
          if (receipt.sourceName != null) Text(receipt.sourceName!),
          if (receipt.note != null && receipt.note!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Text(receipt.note!),
            ),
          if (receipt.cashHandoverStatus != null)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: _CustodyBanner(receipt: receipt, text: text),
            ),
          if (canProcess && receipt.status == 'submitted')
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: <Widget>[
                  FilledButton(
                    onPressed: () => _confirmProcess(context, false),
                    child: Text(text.validate),
                  ),
                  OutlinedButton(
                    onPressed: () => _confirmProcess(context, true),
                    child: Text(text.reject),
                  ),
                ],
              ),
            ),
          if (canProcess &&
              receipt.status == 'validated' &&
              receipt.cashHandoverStatus != 'received_in_treasury')
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: <Widget>[
                  OutlinedButton.icon(
                    onPressed: () => _reminder(context),
                    icon: const Icon(Icons.schedule),
                    label: Text(text.changeReminder),
                  ),
                  FilledButton.icon(
                    onPressed: () => _confirmCashbox(context),
                    icon: const Icon(Icons.lock_outline),
                    label: Text(text.closeCashbox),
                  ),
                ],
              ),
            ),
        ],
      ),
    ),
  );

  Future<void> _confirmProcess(BuildContext context, bool rejected) async {
    final TextEditingController reason = TextEditingController();
    final int? reminder = await showDialog<int>(
      context: context,
      builder: (BuildContext dialogContext) => AlertDialog(
        title: Text(rejected ? text.rejectTitle : text.validateTitle),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            if (rejected)
              TextField(
                controller: reason,
                decoration: InputDecoration(labelText: text.reason),
              ),
            if (!rejected) Text(text.validationReminder),
          ],
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: Text(text.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, 2),
            child: Text(rejected ? text.reject : text.validate),
          ),
        ],
      ),
    );
    if (reminder == null || (rejected && reason.text.trim().isEmpty)) {
      return;
    }
    try {
      await controller.process(receipt.id, <String, dynamic>{
        'action': rejected ? 'rejected' : 'validated',
        if (!rejected) 'processed_amount': receipt.amount,
        if (rejected) 'note': reason.text.trim(),
        if (!rejected) 'handover_reminder_days': reminder,
      });
      if (context.mounted) {
        _snack(context, rejected ? text.rejected : text.validated, false);
      }
    } catch (_) {
      if (context.mounted) _snack(context, text.operationFailed, true);
    }
  }

  Future<void> _reminder(BuildContext context) async {
    int days = receipt.handoverReminderDays ?? 2;
    final int? selected = await showDialog<int>(
      context: context,
      builder: (BuildContext dialogContext) => AlertDialog(
        title: Text(text.changeReminder),
        content: DropdownButtonFormField<int>(
          initialValue: days,
          items: List<DropdownMenuItem<int>>.generate(
            7,
            (int index) => DropdownMenuItem(
              value: index + 1,
              child: Text('${index + 1} ${text.days}'),
            ),
          ),
          onChanged: (int? value) => days = value ?? days,
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: Text(text.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, days),
            child: Text(text.save),
          ),
        ],
      ),
    );
    if (selected == null) return;
    try {
      await controller.changeReminder(receipt.id, selected);
      if (context.mounted) _snack(context, text.reminderSaved, false);
    } catch (_) {
      if (context.mounted) _snack(context, text.operationFailed, true);
    }
  }

  Future<void> _confirmCashbox(BuildContext context) async {
    final bool? confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext dialogContext) => AlertDialog(
        title: Text(text.closeCashbox),
        content: Text(text.closeCashboxBody),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: Text(text.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: Text(text.confirm),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await controller.confirmTreasury(receipt.id);
      if (context.mounted) _snack(context, text.closed, false);
    } catch (_) {
      if (context.mounted) _snack(context, text.operationFailed, true);
    }
  }

  void _snack(BuildContext context, String message, bool error) =>
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: error ? Colors.red.shade700 : KairoColors.success,
        ),
      );
}

class _CustodyBanner extends StatelessWidget {
  const _CustodyBanner({required this.receipt, required this.text});
  final ReceiptDeclaration receipt;
  final _FinanceText text;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: receipt.cashHandoverStatus == 'received_in_treasury'
          ? const Color(0xffe6f4ea)
          : const Color(0xfffff4d6),
      borderRadius: BorderRadius.circular(10),
    ),
    child: Text(
      '${text.cashbox}: ${text.handoverLabel(receipt.cashHandoverStatus!)}${receipt.handoverReminderDays == null ? '' : ' · ${text.reminder}: ${receipt.handoverReminderDays} ${text.days}'}',
    ),
  );
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status, required this.text});
  final String status;
  final _FinanceText text;
  @override
  Widget build(BuildContext context) => Chip(
    backgroundColor: status == 'rejected'
        ? const Color(0xffffe5e5)
        : status == 'validated'
        ? const Color(0xffe6f4ea)
        : const Color(0xffe8f0fe),
    label: Text(text.statusLabel(status)),
  );
}

class _Notice extends StatelessWidget {
  const _Notice(this.message, {required this.error});
  final String message;
  final bool error;
  @override
  Widget build(BuildContext context) => Card(
    color: error ? const Color(0xffffe7e7) : const Color(0xfff6f8fa),
    child: Padding(padding: const EdgeInsets.all(18), child: Text(message)),
  );
}

class _FinanceText {
  const _FinanceText(this.locale);
  final KairoLocale locale;
  bool get en => locale == KairoLocale.en;
  bool get de => locale == KairoLocale.de;
  String get finance => en
      ? 'Finance workspace'
      : de
      ? 'Finanzbereich'
      : 'Espace finances';
  String get declare => en
      ? 'Declare received funds'
      : de
      ? 'Einnahme erklären'
      : 'Déclarer un encaissement';
  String get financeBody => en
      ? 'Validate accounting entries, follow custody and close the cashbox only after receipt.'
      : de
      ? 'Buchungen validieren, Übergaben verfolgen und die Kasse erst nach Erhalt schließen.'
      : 'Validez les écritures, suivez la remise en caisse et clôturez seulement après réception.';
  String get declareBody => en
      ? 'Report funds received in person. The treasurer controls the official accounting entry.'
      : de
      ? 'Melden Sie persönlich erhaltene Mittel. Der Schatzmeister kontrolliert die offizielle Buchung.'
      : 'Signalez un encaissement reçu en main propre. Le trésorier contrôle l’écriture officielle.';
  String get validation => en
      ? 'Treasury validation'
      : de
      ? 'Treasury-Freigabe'
      : 'Validation de trésorerie';
  String get validationBody => en
      ? 'Only the treasurer validates or rejects declarations.'
      : de
      ? 'Nur der Schatzmeister validiert oder lehnt Erklärungen ab.'
      : 'Seul le trésorier valide ou rejette les déclarations.';
  String get newDeclaration => en
      ? 'New declaration'
      : de
      ? 'Neue Erklärung'
      : 'Nouvelle déclaration';
  String get newDeclarationBody => en
      ? 'Choose the income type and its source.'
      : de
      ? 'Wählen Sie die Einnahmeart und ihre Quelle.'
      : 'Choisissez le type d’entrée financière et sa source.';
  String get incomeType => en
      ? 'Income type'
      : de
      ? 'Einnahmeart'
      : 'Type d’entrée financière';
  String get contribution => en
      ? 'Member contribution'
      : de
      ? 'Mitgliedsbeitrag'
      : 'Cotisation d’un membre';
  String get donation => en
      ? 'Donation'
      : de
      ? 'Spende'
      : 'Don';
  String get sponsorship => en
      ? 'Sponsorship'
      : de
      ? 'Sponsoring'
      : 'Mécénat / sponsoring';
  String get tournament => en
      ? 'Tournament proceeds'
      : de
      ? 'Turniereinnahme'
      : 'Recette de tournoi';
  String get otherIncome => en
      ? 'Other income'
      : de
      ? 'Sonstige Einnahme'
      : 'Autre entrée';
  String get memberSearch => en
      ? 'Search a member'
      : de
      ? 'Mitglied suchen'
      : 'Rechercher un membre';
  String get source => en
      ? 'Source or organisation'
      : de
      ? 'Quelle oder Organisation'
      : 'Source / organisme';
  String get amount => en
      ? 'Amount in EUR'
      : de
      ? 'Betrag in EUR'
      : 'Montant en EUR';
  String get note => en
      ? 'Optional note'
      : de
      ? 'Optionale Notiz'
      : 'Note facultative';
  String get submit => en
      ? 'Send declaration'
      : de
      ? 'Erklärung senden'
      : 'Soumettre la déclaration';
  String get saving => en
      ? 'Sending…'
      : de
      ? 'Wird gesendet…'
      : 'Envoi…';
  String get requiredFields => en
      ? 'Enter a valid amount and required source.'
      : de
      ? 'Geben Sie einen gültigen Betrag und die erforderliche Quelle ein.'
      : 'Indiquez un montant valide et la source requise.';
  String get sent => en
      ? 'Declaration sent to the treasurer.'
      : de
      ? 'Erklärung wurde an den Schatzmeister gesendet.'
      : 'Déclaration envoyée au trésorier.';
  String get operationFailed => en
      ? 'Operation failed. Please retry.'
      : de
      ? 'Vorgang fehlgeschlagen. Bitte erneut versuchen.'
      : 'L’opération a échoué. Réessayez.';
  String get loadFailed => en
      ? 'Authorised entries could not be loaded.'
      : de
      ? 'Berechtigte Einträge konnten nicht geladen werden.'
      : 'Les encaissements autorisés n’ont pas pu être chargés.';
  String get empty => en
      ? 'No receipt declaration at the moment.'
      : de
      ? 'Zurzeit keine Einnahmeerklärung.'
      : 'Aucune déclaration pour le moment.';
  String get validate => en
      ? 'Validate'
      : de
      ? 'Validieren'
      : 'Valider';
  String get reject => en
      ? 'Reject'
      : de
      ? 'Ablehnen'
      : 'Rejeter';
  String get validateTitle => en
      ? 'Confirm validation'
      : de
      ? 'Validierung bestätigen'
      : 'Confirmer la validation';
  String get rejectTitle => en
      ? 'Reject declaration'
      : de
      ? 'Erklärung ablehnen'
      : 'Rejeter la déclaration';
  String get reason => en
      ? 'Rejection reason'
      : de
      ? 'Grund der Ablehnung'
      : 'Motif du rejet';
  String get validationReminder => en
      ? 'The default reminder is set to 2 days. You can change it before the cashbox is closed.'
      : de
      ? 'Die Standarderinnerung beträgt 2 Tage und kann vor dem Kassenabschluss geändert werden.'
      : 'Le rappel est fixé à 2 jours par défaut et peut être modifié avant la clôture.';
  String get cancel => en
      ? 'Cancel'
      : de
      ? 'Abbrechen'
      : 'Annuler';
  String get rejected => en
      ? 'Declaration rejected with a reason.'
      : de
      ? 'Erklärung wurde mit Begründung abgelehnt.'
      : 'Déclaration rejetée avec un motif.';
  String get validated => en
      ? 'Accounting entry validated. Cashbox handover remains open.'
      : de
      ? 'Buchung validiert. Kassenübergabe bleibt offen.'
      : 'Écriture validée. La remise en caisse reste ouverte.';
  String get changeReminder => en
      ? 'Change reminder'
      : de
      ? 'Erinnerung ändern'
      : 'Modifier le rappel';
  String get closeCashbox => en
      ? 'Close cashbox'
      : de
      ? 'Kasseneingang bestätigen'
      : 'Clore la remise en caisse';
  String get closeCashboxBody => en
      ? 'Confirm that the money has been received in the association cashbox.'
      : de
      ? 'Bestätigen Sie, dass das Geld in der Vereinskasse eingegangen ist.'
      : 'Confirmez que l’argent a bien été reçu dans la caisse de l’association.';
  String get confirm => en
      ? 'Confirm'
      : de
      ? 'Bestätigen'
      : 'Confirmer';
  String get save => en
      ? 'Save'
      : de
      ? 'Speichern'
      : 'Enregistrer';
  String get reminderSaved => en
      ? 'Reminder updated.'
      : de
      ? 'Erinnerung aktualisiert.'
      : 'Rappel mis à jour.';
  String get closed => en
      ? 'Cashbox receipt confirmed and operation closed.'
      : de
      ? 'Kasseneingang bestätigt und Vorgang geschlossen.'
      : 'Remise en caisse confirmée et opération clôturée.';
  String get cashbox => en
      ? 'Cashbox custody'
      : de
      ? 'Kassenübergabe'
      : 'Remise en caisse';
  String get reminder => en
      ? 'Reminder'
      : de
      ? 'Erinnerung'
      : 'Rappel';
  String get days => en
      ? 'days'
      : de
      ? 'Tage'
      : 'jours';
  String statusLabel(String value) =>
      <String, String>{
        'submitted': en
            ? 'Submitted'
            : de
            ? 'Eingereicht'
            : 'Soumise',
        'validated': en
            ? 'Validated'
            : de
            ? 'Validiert'
            : 'Validée',
        'rejected': en
            ? 'Rejected'
            : de
            ? 'Abgelehnt'
            : 'Rejetée',
      }[value] ??
      value;
  String handoverLabel(String value) =>
      <String, String>{
        'pending_handover': en
            ? 'Pending handover'
            : de
            ? 'Übergabe ausstehend'
            : 'Remise attendue',
        'handover_reported': en
            ? 'Handover reported'
            : de
            ? 'Übergabe gemeldet'
            : 'Remise déclarée',
        'received_in_treasury': en
            ? 'Received in treasury'
            : de
            ? 'In Kasse eingegangen'
            : 'Reçu en caisse',
      }[value] ??
      value;
  String incomeLabel(String value) =>
      <String, String>{
        'membership_contribution': contribution,
        'donation': donation,
        'sponsorship': sponsorship,
        'tournament_proceeds': tournament,
        'other_income': otherIncome,
      }[value] ??
      value;
}
