import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../../../app/theme/kairo_theme.dart';
import '../../../core/export/report_exporter.dart';
import '../../../core/offline/offline_workspace_controller.dart';
import '../../members/data/member_gateway.dart';
import '../../members/data/member_models.dart';
import '../data/finance_gateway.dart';

String _paymentMethodLabel(KairoLocale locale, String method) {
  const Map<String, List<String>> labels = <String, List<String>>{
    'cash': <String>['Cash', 'Bargeld', 'Espèces'],
    'bank_transfer': <String>['Bank transfer', 'Überweisung', 'Virement'],
    'card': <String>['Card', 'Karte', 'Carte'],
  };
  return labels[method]![locale == KairoLocale.en
      ? 0
      : locale == KairoLocale.de
      ? 1
      : 2];
}

class FinanceWorkspacePage extends StatefulWidget {
  const FinanceWorkspacePage({
    super.key,
    required this.gateway,
    required this.memberGateway,
    required this.locale,
    required this.canWriteExpenses,
    this.offlineWorkspace,
  });
  final FinanceGateway gateway;
  final MemberGateway memberGateway;
  final KairoLocale locale;
  final bool canWriteExpenses;
  final OfflineWorkspaceController? offlineWorkspace;

  @override
  State<FinanceWorkspacePage> createState() => _FinanceWorkspacePageState();
}

class _FinanceWorkspacePageState extends State<FinanceWorkspacePage> {
  late int _year;
  FinanceSummary? _summary;
  AnnualBudget? _budget;
  List<FinanceContribution> _contributions = const <FinanceContribution>[];
  List<MemberProfile> _results = const <MemberProfile>[];
  List<FinanceContribution> _memberHistory = const <FinanceContribution>[];
  MemberProfile? _selected;
  bool _loading = true;
  bool _saving = false;
  String? _error;
  final TextEditingController _search = TextEditingController();
  final TextEditingController _amount = TextEditingController();
  final TextEditingController _description = TextEditingController();
  final TextEditingController _payee = TextEditingController();
  String _category = 'sport_equipment';
  String _method = 'cash';

  @override
  void initState() {
    super.initState();
    _year = DateTime.now().year;
    _restoreExpenseDraft();
    _load();
  }

  @override
  void dispose() {
    _search.dispose();
    _amount.dispose();
    _description.dispose();
    _payee.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final List<Object?> result = await Future.wait<Object?>(<Future<Object?>>[
        widget.gateway.summary(_year),
        widget.gateway.contributions(_year),
        if (widget.canWriteExpenses) widget.gateway.annualBudget(_year),
      ]);
      _summary = result[0] as FinanceSummary;
      _contributions = result[1] as List<FinanceContribution>;
      _budget = result.length > 2 ? result[2] as AnnualBudget : null;
    } catch (error) {
      _error = error.toString();
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _restoreExpenseDraft() async {
    final draft = await widget.offlineWorkspace?.readDraft('expense');
    if (!mounted || draft == null) return;
    setState(() {
      _amount.text = draft['amount'] as String? ?? '';
      _description.text = draft['description'] as String? ?? '';
      _payee.text = draft['payee'] as String? ?? '';
      _category = draft['category'] as String? ?? _category;
      _method = draft['method'] as String? ?? _method;
    });
  }

  void _saveExpenseDraft() =>
      widget.offlineWorkspace?.saveDraft('expense', <String, dynamic>{
        'amount': _amount.text,
        'description': _description.text,
        'payee': _payee.text,
        'category': _category,
        'method': _method,
      });

  Future<void> _searchMembers(String value) async {
    if (value.trim().length < 2) {
      if (mounted) setState(() => _results = const <MemberProfile>[]);
      return;
    }
    try {
      final List<MemberProfile> members = await widget.memberGateway.list(
        query: value.trim(),
      );
      if (mounted) setState(() => _results = members);
    } catch (_) {
      if (mounted) setState(() => _results = const <MemberProfile>[]);
    }
  }

  Future<void> _selectMember(MemberProfile member) async {
    setState(() {
      _selected = member;
      _search.text = member.displayName;
      _results = const <MemberProfile>[];
      _memberHistory = const <FinanceContribution>[];
    });
    try {
      final List<FinanceContribution> items = await widget.gateway
          .memberContributions(member.id);
      if (mounted) setState(() => _memberHistory = items);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    }
  }

  Future<void> _saveExpense() async {
    final _FinanceText text = _FinanceText(widget.locale);
    final double? amount = double.tryParse(_amount.text.replaceAll(',', '.'));
    if (amount == null || amount <= 0 || _description.text.trim().length < 3) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(text.invalidExpense)));
      return;
    }
    final bool confirmed = await _confirm(text.confirmExpense);
    if (!confirmed) return;
    setState(() => _saving = true);
    try {
      await widget.gateway.createExpense(<String, dynamic>{
        'category': _category,
        'amount': amount.toStringAsFixed(2),
        'spent_at': DateTime.now().toUtc().toIso8601String(),
        'description': _description.text.trim(),
        'payee': _payee.text.trim().isEmpty ? null : _payee.text.trim(),
        'payment_method': _method,
      });
      _amount.clear();
      _description.clear();
      _payee.clear();
      await widget.offlineWorkspace?.clearDraft('expense');
      await _load();
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(text.expenseSaved)));
      }
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<bool> _confirm(String message) async =>
      await showDialog<bool>(
        context: context,
        builder: (BuildContext context) => AlertDialog(
          content: Text(message),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text(_FinanceText(widget.locale).cancel),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: Text(_FinanceText(widget.locale).confirm),
            ),
          ],
        ),
      ) ??
      false;

  Future<void> _export(String format) async {
    final _FinanceText text = _FinanceText(widget.locale);
    setState(() => _saving = true);
    try {
      final List<int> data = await widget.gateway.exportReport(format, _year);
      final String extension = format == 'whatsapp' ? 'txt' : format;
      final String media = format == 'xlsx'
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : format == 'pdf'
          ? 'application/pdf'
          : 'text/plain';
      await saveReport(
        bytes: data,
        filename: 'kairo-finance-$_year.$extension',
        mediaType: media,
      );
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(text.exportReady(format))));
      }
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final _FinanceText text = _FinanceText(widget.locale);
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _load,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: <Widget>[
              _header(text),
              const SizedBox(height: 16),
              if (_loading)
                const Padding(
                  padding: EdgeInsets.all(40),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (_error != null)
                _ErrorCard(message: _error!, retry: _load, text: text)
              else ...<Widget>[
                _summaryCards(text),
                const SizedBox(height: 16),
                _memberLookup(text),
                const SizedBox(height: 16),
                if (_budget != null) _budgetSection(text),
                if (_budget != null) const SizedBox(height: 16),
                if (widget.canWriteExpenses) _expenseSection(text),
                if (widget.canWriteExpenses) const SizedBox(height: 16),
                _contributionOverview(text),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _header(_FinanceText text) => LayoutBuilder(
    builder: (BuildContext context, BoxConstraints constraints) {
      final List<Widget> actions = <Widget>[
        DropdownButton<int>(
          value: _year,
          onChanged: (int? value) {
            if (value != null) {
              setState(() => _year = value);
              _load();
            }
          },
          items: <int>[_year - 1, _year, _year + 1]
              .map(
                (int item) =>
                    DropdownMenuItem(value: item, child: Text('$item')),
              )
              .toList(),
        ),
        IconButton(
          onPressed: _loading ? null : _load,
          tooltip: text.refresh,
          icon: const Icon(Icons.refresh),
        ),
        OutlinedButton.icon(
          onPressed: _saving ? null : () => _export('xlsx'),
          icon: const Icon(Icons.table_view_outlined),
          label: Text(text.excel),
        ),
        OutlinedButton.icon(
          onPressed: _saving ? null : () => _export('pdf'),
          icon: const Icon(Icons.picture_as_pdf_outlined),
          label: Text(text.pdf),
        ),
        OutlinedButton.icon(
          onPressed: _saving ? null : () => _export('whatsapp'),
          icon: const Icon(Icons.share_outlined),
          label: Text(text.share),
        ),
      ];
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(text.kicker, style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 4),
          Text(text.title, style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 4),
          Text(widget.canWriteExpenses ? text.treasurerLead : text.auditLead),
          const SizedBox(height: 12),
          Wrap(spacing: 8, runSpacing: 8, children: actions),
        ],
      );
    },
  );

  Widget _summaryCards(_FinanceText text) => LayoutBuilder(
    builder: (BuildContext context, BoxConstraints constraints) {
      final List<Widget> cards = <Widget>[
        _Metric(
          label: text.expected,
          value: _summary!.totalExpected,
          color: KairoColors.primary,
        ),
        _Metric(
          label: text.paid,
          value: _summary!.totalPaid,
          color: KairoColors.success,
        ),
        _Metric(
          label: text.outstanding,
          value: _summary!.totalBalance,
          color: KairoColors.warning,
        ),
      ];
      return constraints.maxWidth < 680
          ? Column(
              children: cards
                  .map(
                    (Widget card) => Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: card,
                    ),
                  )
                  .toList(),
            )
          : Row(
              children: <Widget>[
                Expanded(child: cards[0]),
                const SizedBox(width: 10),
                Expanded(child: cards[1]),
                const SizedBox(width: 10),
                Expanded(child: cards[2]),
              ],
            );
    },
  );

  Widget _memberLookup(_FinanceText text) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            text.memberSearch,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _search,
            onChanged: _searchMembers,
            decoration: InputDecoration(
              prefixIcon: const Icon(Icons.search),
              labelText: text.memberSearchHint,
            ),
          ),
          if (_results.isNotEmpty)
            ..._results
                .take(6)
                .map(
                  (MemberProfile item) => ListTile(
                    title: Text(item.displayName),
                    subtitle: Text(
                      '${item.memberCode} · ${item.email ?? item.phone ?? ''}',
                    ),
                    onTap: () => _selectMember(item),
                  ),
                ),
          if (_selected != null)
            _MemberFinancialHistory(
              member: _selected!,
              values: _memberHistory,
              text: text,
            ),
        ],
      ),
    ),
  );

  Widget _budgetSection(_FinanceText text) {
    final AnnualBudget budget = _budget!;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(
              '${text.budget} · $_year',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 4),
            Text(text.budgetLead),
            const SizedBox(height: 16),
            _Metric(
              label: text.available,
              value: budget.availableBalance,
              color: (double.tryParse(budget.availableBalance) ?? 0) < 0
                  ? KairoColors.danger
                  : KairoColors.primary,
            ),
            const SizedBox(height: 16),
            LayoutBuilder(
              builder: (BuildContext context, BoxConstraints constraints) =>
                  constraints.maxWidth < 760
                  ? Column(
                      children: <Widget>[
                        _Breakdown(
                          title: text.income,
                          total: budget.incomeTotal,
                          values: budget.incomeByCategory,
                          colors: const <Color>[
                            KairoColors.primary,
                            KairoColors.success,
                            Colors.deepPurple,
                          ],
                        ),
                        const SizedBox(height: 14),
                        _Breakdown(
                          title: text.expenses,
                          total: budget.expenseTotal,
                          values: budget.expensesByCategory,
                          colors: const <Color>[
                            KairoColors.danger,
                            Colors.orange,
                            Colors.deepPurple,
                          ],
                        ),
                      ],
                    )
                  : Row(
                      children: <Widget>[
                        Expanded(
                          child: _Breakdown(
                            title: text.income,
                            total: budget.incomeTotal,
                            values: budget.incomeByCategory,
                            colors: const <Color>[
                              KairoColors.primary,
                              KairoColors.success,
                              Colors.deepPurple,
                            ],
                          ),
                        ),
                        const SizedBox(width: 18),
                        Expanded(
                          child: _Breakdown(
                            title: text.expenses,
                            total: budget.expenseTotal,
                            values: budget.expensesByCategory,
                            colors: const <Color>[
                              KairoColors.danger,
                              Colors.orange,
                              Colors.deepPurple,
                            ],
                          ),
                        ),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _expenseSection(_FinanceText text) {
    final AnnualBudget budget = _budget!;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(
              text.recordExpense,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 4),
            Text(text.expenseLead),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: _category,
              decoration: InputDecoration(labelText: text.category),
              items: _FinanceText.categories
                  .map(
                    (String value) => DropdownMenuItem(
                      value: value,
                      child: Text(text.categoryName(value)),
                    ),
                  )
                  .toList(),
              onChanged: (String? value) => setState(() {
                _category = value!;
                _saveExpenseDraft();
              }),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _amount,
              onChanged: (_) => _saveExpenseDraft(),
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: InputDecoration(labelText: text.amount),
            ),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              initialValue: _method,
              decoration: InputDecoration(labelText: text.method),
              items: <DropdownMenuItem<String>>[
                DropdownMenuItem(
                  value: 'cash',
                  child: Text(_paymentMethodLabel(widget.locale, 'cash')),
                ),
                DropdownMenuItem(
                  value: 'bank_transfer',
                  child: Text(
                    _paymentMethodLabel(widget.locale, 'bank_transfer'),
                  ),
                ),
                DropdownMenuItem(
                  value: 'card',
                  child: Text(_paymentMethodLabel(widget.locale, 'card')),
                ),
              ],
              onChanged: (String? value) => setState(() {
                _method = value!;
                _saveExpenseDraft();
              }),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _payee,
              onChanged: (_) => _saveExpenseDraft(),
              decoration: InputDecoration(labelText: text.payee),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _description,
              onChanged: (_) => _saveExpenseDraft(),
              maxLines: 3,
              decoration: InputDecoration(labelText: text.description),
            ),
            const SizedBox(height: 14),
            FilledButton.icon(
              onPressed: _saving ? null : _saveExpense,
              icon: const Icon(Icons.remove_circle_outline),
              label: Text(text.recordExpense),
            ),
            if (budget.recentExpenses.isNotEmpty) ...<Widget>[
              const SizedBox(height: 20),
              Text(
                text.recentExpenses,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              ...budget.recentExpenses.map(
                (FinanceExpense expense) => ListTile(
                  leading: const Icon(
                    Icons.arrow_upward,
                    color: KairoColors.danger,
                  ),
                  title: Text(text.categoryName(expense.category)),
                  subtitle: Text(
                    '${expense.description}\n${expense.payee ?? ''}',
                  ),
                  trailing: Text(
                    '− ${expense.amount} EUR',
                    style: const TextStyle(color: KairoColors.danger),
                  ),
                  isThreeLine: true,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _contributionOverview(_FinanceText text) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            text.contributionOverview,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Text(text.contributionCount(_contributions.length)),
          ..._contributions
              .take(8)
              .map(
                (FinanceContribution item) => ListTile(
                  title: Text('${text.year} ${item.year}'),
                  subtitle: Text(
                    '${text.expected} ${item.expectedAmount} EUR · ${text.paid} ${item.paidAmount} EUR',
                  ),
                  trailing: Text('${item.balance} EUR'),
                ),
              ),
        ],
      ),
    ),
  );
}

class _Metric extends StatelessWidget {
  const _Metric({
    required this.label,
    required this.value,
    required this.color,
  });
  final String label;
  final String value;
  final Color color;
  @override
  Widget build(BuildContext context) => Card(
    color: color.withValues(alpha: .10),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(label),
          const SizedBox(height: 6),
          Text(
            '$value EUR',
            style: Theme.of(
              context,
            ).textTheme.titleLarge?.copyWith(color: color),
          ),
        ],
      ),
    ),
  );
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({
    required this.message,
    required this.retry,
    required this.text,
  });
  final String message;
  final VoidCallback retry;
  final _FinanceText text;
  @override
  Widget build(BuildContext context) => Card(
    color: Colors.red.shade50,
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            text.unavailable,
            style: const TextStyle(color: KairoColors.danger),
          ),
          Text(message),
          TextButton(onPressed: retry, child: Text(text.retry)),
        ],
      ),
    ),
  );
}

class _MemberFinancialHistory extends StatelessWidget {
  const _MemberFinancialHistory({
    required this.member,
    required this.values,
    required this.text,
  });
  final MemberProfile member;
  final List<FinanceContribution> values;
  final _FinanceText text;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(top: 14),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          member.displayName,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        Text(member.memberCode),
        if (values.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(text.noHistory),
          )
        else
          ...values.map(
            (FinanceContribution item) => ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('${text.year} ${item.year}'),
              subtitle: Text(
                '${text.expected} ${item.expectedAmount} EUR · ${text.paid} ${item.paidAmount} EUR',
              ),
              trailing: Text('${item.balance} EUR'),
            ),
          ),
      ],
    ),
  );
}

class _Breakdown extends StatelessWidget {
  const _Breakdown({
    required this.title,
    required this.total,
    required this.values,
    required this.colors,
  });
  final String title;
  final String total;
  final List<BudgetSlice> values;
  final List<Color> colors;

  @override
  Widget build(BuildContext context) {
    final double sum = values.fold(
      0,
      (double total, BudgetSlice item) =>
          total + (double.tryParse(item.amount) ?? 0),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 10),
        SizedBox(
          height: 150,
          child: Center(
            child: CustomPaint(
              size: const Size(150, 150),
              painter: _DonutPainter(values: values, colors: colors),
            ),
          ),
        ),
        Text('$total EUR', style: Theme.of(context).textTheme.titleMedium),
        ...values.asMap().entries.map((MapEntry<int, BudgetSlice> entry) {
          final double percentage = sum == 0
              ? 0
              : ((double.tryParse(entry.value.amount) ?? 0) * 100 / sum);
          return Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Row(
              children: <Widget>[
                Container(
                  width: 10,
                  height: 10,
                  color: colors[entry.key % colors.length],
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(entry.value.category.replaceAll('_', ' ')),
                ),
                Text('${percentage.toStringAsFixed(0)}%'),
              ],
            ),
          );
        }),
      ],
    );
  }
}

class _DonutPainter extends CustomPainter {
  const _DonutPainter({required this.values, required this.colors});
  final List<BudgetSlice> values;
  final List<Color> colors;
  @override
  void paint(Canvas canvas, Size size) {
    final double total = values.fold(
      0,
      (double value, BudgetSlice slice) =>
          value + (double.tryParse(slice.amount) ?? 0),
    );
    final Rect rect = Offset.zero & size;
    final Paint paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 26;
    if (total <= 0) {
      paint.color = KairoColors.border;
      canvas.drawCircle(size.center(Offset.zero), 55, paint);
      return;
    }
    double start = -math.pi / 2;
    for (int i = 0; i < values.length; i++) {
      final double sweep =
          (double.tryParse(values[i].amount) ?? 0) / total * math.pi * 2;
      paint.color = colors[i % colors.length];
      canvas.drawArc(rect.deflate(16), start, sweep, false, paint);
      start += sweep;
    }
  }

  @override
  bool shouldRepaint(covariant _DonutPainter oldDelegate) =>
      oldDelegate.values != values;
}

class _FinanceText {
  const _FinanceText(this.locale);
  final KairoLocale locale;
  bool get en => locale == KairoLocale.en;
  bool get de => locale == KairoLocale.de;
  static const List<String> categories = <String>[
    'sport_equipment',
    'fuel_transport',
    'tournament',
    'cultural_event',
    'administration',
    'other',
  ];
  String get kicker => en
      ? 'FINANCE WORKSPACE'
      : de
      ? 'FINANZBEREICH'
      : 'ESPACE FINANCES';
  String get title => en
      ? 'Treasury operations'
      : de
      ? 'Kassenverwaltung'
      : 'Opérations de trésorerie';
  String get treasurerLead => en
      ? 'Validate the annual budget and record authorised expenses.'
      : de
      ? 'Prüfen Sie das Jahresbudget und erfassen Sie berechtigte Ausgaben.'
      : 'Consultez le budget annuel et enregistrez les dépenses autorisées.';
  String get auditLead => en
      ? 'Read-only financial oversight and exports.'
      : de
      ? 'Schreibgeschützte Finanzaufsicht und Exporte.'
      : 'Consultation financière en lecture seule et exports.';
  String get expected => en
      ? 'Expected'
      : de
      ? 'Fällig'
      : 'Attendu';
  String get paid => en
      ? 'Paid'
      : de
      ? 'Bezahlt'
      : 'Payé';
  String get outstanding => en
      ? 'Outstanding'
      : de
      ? 'Offen'
      : 'Solde restant';
  String get available => en
      ? 'Available treasury'
      : de
      ? 'Verfügbare Kasse'
      : 'Trésorerie disponible';
  String get budget => en
      ? 'Annual budget'
      : de
      ? 'Jahresbudget'
      : 'Budget annuel';
  String get budgetLead => en
      ? 'Validated income and recorded expenses are grouped by category.'
      : de
      ? 'Bestätigte Einnahmen und erfasste Ausgaben sind nach Kategorie gruppiert.'
      : 'Les entrées validées et dépenses enregistrées sont regroupées par catégorie.';
  String get income => en
      ? 'Income'
      : de
      ? 'Einnahmen'
      : 'Entrées';
  String get expenses => en
      ? 'Expenses'
      : de
      ? 'Ausgaben'
      : 'Dépenses';
  String get memberSearch => en
      ? 'Member financial search'
      : de
      ? 'Finanzsuche Mitglied'
      : 'Recherche financière d’un membre';
  String get memberSearchHint => en
      ? 'Name, code, phone or email'
      : de
      ? 'Name, Code, Telefon oder E-Mail'
      : 'Nom, matricule, téléphone ou e-mail';
  String get noHistory => en
      ? 'No financial history.'
      : de
      ? 'Kein Finanzverlauf.'
      : 'Aucun historique financier.';
  String get recordExpense => en
      ? 'Record an expense'
      : de
      ? 'Ausgabe erfassen'
      : 'Enregistrer une dépense';
  String get expenseLead => en
      ? 'This action immediately affects the available treasury and is audited.'
      : de
      ? 'Diese Aktion wirkt sich sofort auf die verfügbare Kasse aus und wird protokolliert.'
      : 'Cette opération impacte immédiatement la trésorerie disponible et est journalisée.';
  String get category => en
      ? 'Expense category'
      : de
      ? 'Ausgabenkategorie'
      : 'Catégorie de dépense';
  String get amount => en
      ? 'Amount (EUR)'
      : de
      ? 'Betrag (EUR)'
      : 'Montant (EUR)';
  String get method => en
      ? 'Payment method'
      : de
      ? 'Zahlungsart'
      : 'Mode de paiement';
  String get payee => en
      ? 'Payee / supplier'
      : de
      ? 'Empfänger / Lieferant'
      : 'Bénéficiaire / fournisseur';
  String get description => en
      ? 'Reason / description'
      : de
      ? 'Grund / Beschreibung'
      : 'Motif / description';
  String get recentExpenses => en
      ? 'Recent expenses'
      : de
      ? 'Letzte Ausgaben'
      : 'Dernières dépenses';
  String get invalidExpense => en
      ? 'Enter a valid amount and description.'
      : de
      ? 'Geben Sie einen gültigen Betrag und eine Beschreibung ein.'
      : 'Saisissez un montant et une description valides.';
  String get confirmExpense => en
      ? 'Confirm this expense? The budget will be updated.'
      : de
      ? 'Diese Ausgabe bestätigen? Das Budget wird aktualisiert.'
      : 'Confirmer cette dépense ? Le budget sera mis à jour.';
  String get expenseSaved => en
      ? 'Expense recorded in the budget.'
      : de
      ? 'Ausgabe wurde im Budget erfasst.'
      : 'La dépense a été enregistrée dans le budget.';
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
  String get unavailable => en
      ? 'Finance workspace unavailable'
      : de
      ? 'Finanzbereich nicht verfügbar'
      : 'Espace finances indisponible';
  String get retry => en
      ? 'Retry'
      : de
      ? 'Wiederholen'
      : 'Réessayer';
  String get refresh => en
      ? 'Refresh'
      : de
      ? 'Aktualisieren'
      : 'Actualiser';
  String get excel => 'Excel';
  String get pdf => 'PDF';
  String get share => en
      ? 'Share'
      : de
      ? 'Teilen'
      : 'Partager';
  String exportReady(String format) => en
      ? '$format export is ready.'
      : de
      ? '$format-Export ist bereit.'
      : 'L’export $format est prêt.';
  String get contributionOverview => en
      ? 'Contribution overview'
      : de
      ? 'Beitragsübersicht'
      : 'Vue des cotisations';
  String contributionCount(int count) => en
      ? '$count records'
      : de
      ? '$count Einträge'
      : '$count enregistrements';
  String get year => en
      ? 'Year'
      : de
      ? 'Jahr'
      : 'Année';
  String categoryName(String value) {
    const Map<String, List<String>> names = <String, List<String>>{
      'sport_equipment': <String>[
        'Sport equipment',
        'Sportausrüstung',
        'Sport et matériel',
      ],
      'fuel_transport': <String>[
        'Fuel and transport',
        'Kraftstoff und Transport',
        'Carburant et transport',
      ],
      'tournament': <String>['Tournament', 'Turnier', 'Tournoi'],
      'cultural_event': <String>[
        'Cultural event',
        'Kulturveranstaltung',
        'Événement culturel',
      ],
      'administration': <String>[
        'Administration',
        'Verwaltung',
        'Administration',
      ],
      'other': <String>['Other', 'Andere', 'Autre'],
    };
    return names[value]![en
        ? 0
        : de
        ? 1
        : 2];
  }
}
