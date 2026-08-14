import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';
import 'app_surface_card.dart';

class AppMetricCard extends StatelessWidget {
  const AppMetricCard({
    super.key,
    required this.icon,
    required this.title,
    required this.value,
    this.detail,
    this.tone = AppCardTone.standard,
    this.onTap,
  });

  final IconData icon;
  final String title;
  final String value;
  final String? detail;
  final AppCardTone tone;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final ColorScheme scheme = Theme.of(context).colorScheme;
    return AppSurfaceCard(
      tone: tone,
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Icon(icon, color: scheme.primary),
          const SizedBox(height: AppSpacing.lg),
          Text(title, style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: AppSpacing.xs),
          Text(value, style: Theme.of(context).textTheme.headlineSmall),
          if (detail != null) ...<Widget>[
            const SizedBox(height: AppSpacing.xs),
            Text(detail!, style: Theme.of(context).textTheme.bodySmall),
          ],
        ],
      ),
    );
  }
}
