import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';

enum AppCardTone {
  standard,
  primary,
  secondary,
  tertiary,
  success,
  warning,
  danger,
}

class AppSurfaceCard extends StatelessWidget {
  const AppSurfaceCard({
    super.key,
    required this.child,
    this.tone = AppCardTone.standard,
    this.padding = const EdgeInsets.all(AppSpacing.lg),
    this.onTap,
  });

  final Widget child;
  final AppCardTone tone;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final ColorScheme scheme = Theme.of(context).colorScheme;
    final Brightness brightness = Theme.of(context).brightness;
    final Color color = switch (tone) {
      AppCardTone.standard => scheme.surfaceContainerLow,
      AppCardTone.primary => scheme.primaryContainer,
      AppCardTone.secondary => scheme.secondaryContainer,
      AppCardTone.tertiary => scheme.tertiaryContainer,
      AppCardTone.success => AppStatusVisual.of(
        AppStatus.paid,
        brightness,
      ).background,
      AppCardTone.warning => AppStatusVisual.of(
        AppStatus.pending,
        brightness,
      ).background,
      AppCardTone.danger => scheme.errorContainer,
    };
    return Card(
      color: color,
      child: InkWell(
        borderRadius: AppRadius.medium,
        onTap: onTap,
        child: Padding(padding: padding, child: child),
      ),
    );
  }
}
