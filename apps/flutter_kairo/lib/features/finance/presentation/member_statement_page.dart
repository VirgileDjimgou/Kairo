import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../data/member_statement_gateway.dart';

class MemberStatementPage extends StatefulWidget {
  const MemberStatementPage({
    super.key,
    required this.gateway,
    required this.locale,
  });
  final MemberStatementGateway gateway;
  final KairoLocale locale;
  @override
  State<MemberStatementPage> createState() => _MemberStatementPageState();
}

class _MemberStatementPageState extends State<MemberStatementPage> {
  MemberStatement? statement;
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
      statement = await widget.gateway.mine();
    } catch (_) {
      failed = true;
    }
    if (mounted) setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    final _StatementText text = _StatementText(widget.locale);
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
              const SizedBox(height: 8),
              Text(text.intro),
              const SizedBox(height: 20),
              if (loading)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: CircularProgressIndicator(),
                  ),
                )
              else if (failed)
                Card(
                  child: Padding(
                    padding: EdgeInsets.all(18),
                    child: Text(text.failure),
                  ),
                )
              else if (statement != null) ...<Widget>[
                _Header(statement: statement!, text: text),
                const SizedBox(height: 16),
                Text(
                  text.history,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                if (statement!.contributions.isEmpty)
                  Card(
                    child: Padding(
                      padding: EdgeInsets.all(18),
                      child: Text(text.empty),
                    ),
                  )
                else
                  ...statement!.contributions.map(
                    (MemberContribution item) =>
                        _Contribution(item: item, text: text),
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.statement, required this.text});
  final MemberStatement statement;
  final _StatementText text;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            statement.displayName,
            style: Theme.of(context).textTheme.titleLarge,
          ),
          Text(statement.memberCode),
          const SizedBox(height: 16),
          Row(
            children: <Widget>[
              Expanded(
                child: _Total(
                  label: text.expected,
                  amount: statement.totalExpected,
                ),
              ),
              Expanded(
                child: _Total(label: text.paid, amount: statement.totalPaid),
              ),
              Expanded(
                child: _Total(
                  label: text.balance,
                  amount: statement.totalBalance,
                ),
              ),
            ],
          ),
        ],
      ),
    ),
  );
}

class _Total extends StatelessWidget {
  const _Total({required this.label, required this.amount});
  final String label;
  final String amount;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(4),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(label),
        Text('$amount EUR', style: Theme.of(context).textTheme.titleMedium),
      ],
    ),
  );
}

class _Contribution extends StatelessWidget {
  const _Contribution({required this.item, required this.text});
  final MemberContribution item;
  final _StatementText text;
  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      title: Text(text.year(item.year)),
      subtitle: Text(
        '${text.expected} ${item.expectedAmount} EUR · ${text.paid} ${item.paidAmount} EUR · ${text.balance} ${item.balanceAmount} EUR',
      ),
      trailing: Chip(label: Text(item.status)),
    ),
  );
}

class _StatementText {
  const _StatementText(this.locale);
  final KairoLocale locale;
  bool get en => locale == KairoLocale.en;
  bool get de => locale == KairoLocale.de;
  String get title => en
      ? 'My contributions'
      : de
      ? 'Meine Beiträge'
      : 'Mes cotisations';
  String get intro => en
      ? 'Your official balance and payment history are provided by the association server.'
      : de
      ? 'Ihr offizieller Saldo und Zahlungsverlauf werden vom Vereinsserver bereitgestellt.'
      : 'Votre solde officiel et votre historique de paiements sont fournis par le serveur de l’association.';
  String get failure => en
      ? 'Your statement could not be loaded. Pull down to retry.'
      : de
      ? 'Ihr Kontoauszug konnte nicht geladen werden. Ziehen Sie zum Wiederholen nach unten.'
      : 'Votre relevé n’a pas pu être chargé. Faites glisser vers le bas pour réessayer.';
  String get history => en
      ? 'Contribution history'
      : de
      ? 'Beitragsverlauf'
      : 'Historique des cotisations';
  String get empty => en
      ? 'No contribution is available.'
      : de
      ? 'Keine Beiträge verfügbar.'
      : 'Aucune cotisation disponible.';
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
  String get balance => en
      ? 'Balance'
      : de
      ? 'Restbetrag'
      : 'Solde';
  String year(String value) => en
      ? 'Year $value'
      : de
      ? 'Jahr $value'
      : 'Année $value';
}
