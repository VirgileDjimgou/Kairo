import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/design_system/components/app_metric_card.dart';
import 'package:kairo_flutter/design_system/components/app_status_badge.dart';
import 'package:kairo_flutter/design_system/components/app_surface_card.dart';
import 'package:kairo_flutter/design_system/theme/app_theme.dart';
import 'package:kairo_flutter/design_system/theme/app_tokens.dart';

void main() {
  testWidgets(
    'design system renders semantic surfaces in light and dark mode',
    (WidgetTester tester) async {
      final SemanticsHandle semantics = tester.ensureSemantics();
      for (final ThemeData theme in <ThemeData>[
        AppTheme.light(),
        AppTheme.dark(),
      ]) {
        await tester.pumpWidget(
          MaterialApp(
            theme: theme,
            home: Scaffold(
              body: Column(
                children: const <Widget>[
                  AppMetricCard(
                    icon: Icons.account_balance_wallet_outlined,
                    title: 'Cotisations',
                    value: '100 €',
                    detail: 'Paiement validé',
                    tone: AppCardTone.success,
                  ),
                  AppStatusBadge(status: AppStatus.paid, label: 'Payé'),
                ],
              ),
            ),
          ),
        );

        expect(find.text('Cotisations'), findsOneWidget);
        expect(find.text('100 €'), findsOneWidget);
        expect(
          tester.getSemantics(find.byType(AppStatusBadge)),
          matchesSemantics(label: 'Payé'),
        );
        expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
      }
      semantics.dispose();
    },
  );

  testWidgets('semantic cards remain readable with Android text scaling', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.dark(),
        home: MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(1.4)),
          child: Scaffold(
            body: ListView(
              children: const <Widget>[
                AppMetricCard(
                  icon: Icons.event_available_outlined,
                  title: 'Événement à venir',
                  value: '18 août',
                  detail: 'Réunion générale de l’association',
                  tone: AppCardTone.tertiary,
                ),
                AppStatusBadge(
                  status: AppStatus.pending,
                  label: 'Validation en attente',
                ),
              ],
            ),
          ),
        ),
      ),
    );

    expect(find.text('Événement à venir'), findsOneWidget);
    expect(find.text('Validation en attente'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
