import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';
import 'app_surface_card.dart';

class AppStatePanel extends StatelessWidget {
  const AppStatePanel({
    super.key,
    required this.icon,
    required this.title,
    this.message,
    this.action,
    this.tone = AppCardTone.standard,
  });

  final IconData icon;
  final String title;
  final String? message;
  final Widget? action;
  final AppCardTone tone;

  @override
  Widget build(BuildContext context) {
    final ColorScheme scheme = Theme.of(context).colorScheme;
    final Color iconColor = switch (tone) {
      AppCardTone.success => AppStatusVisual.of(
        AppStatus.paid,
        Theme.of(context).brightness,
      ).foreground,
      AppCardTone.warning => AppStatusVisual.of(
        AppStatus.pending,
        Theme.of(context).brightness,
      ).foreground,
      AppCardTone.danger => scheme.error,
      AppCardTone.secondary => scheme.secondary,
      AppCardTone.tertiary => scheme.tertiary,
      AppCardTone.standard || AppCardTone.primary => scheme.primary,
    };
    return AppSurfaceCard(
      tone: tone,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Icon(icon, color: iconColor),
          const SizedBox(height: AppSpacing.md),
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          if (message != null && message!.isNotEmpty) ...<Widget>[
            const SizedBox(height: AppSpacing.xs),
            Text(message!, style: Theme.of(context).textTheme.bodyMedium),
          ],
          if (action != null) ...<Widget>[
            const SizedBox(height: AppSpacing.md),
            action!,
          ],
        ],
      ),
    );
  }
}
