import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';
import 'app_surface_card.dart';

class AppStatePanel extends StatelessWidget {
  const AppStatePanel({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
    this.action,
    this.tone = AppCardTone.standard,
  });

  final IconData icon;
  final String title;
  final String message;
  final Widget? action;
  final AppCardTone tone;

  @override
  Widget build(BuildContext context) => AppSurfaceCard(
    tone: tone,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Icon(icon, color: Theme.of(context).colorScheme.primary),
        const SizedBox(height: AppSpacing.md),
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: AppSpacing.xs),
        Text(message, style: Theme.of(context).textTheme.bodyMedium),
        if (action != null) ...<Widget>[
          const SizedBox(height: AppSpacing.md),
          action!,
        ],
      ],
    ),
  );
}
