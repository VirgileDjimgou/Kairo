import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';

class AppStatusBadge extends StatelessWidget {
  const AppStatusBadge({super.key, required this.status, required this.label});

  final AppStatus status;
  final String label;

  @override
  Widget build(BuildContext context) {
    final AppStatusVisual visual = AppStatusVisual.of(
      status,
      Theme.of(context).brightness,
    );
    return Semantics(
      container: true,
      excludeSemantics: true,
      label: label,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: visual.background,
          borderRadius: const BorderRadius.all(Radius.circular(99)),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.sm,
            vertical: AppSpacing.xs,
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              Icon(visual.icon, size: 16, color: visual.foreground),
              const SizedBox(width: AppSpacing.xs),
              Flexible(
                child: Text(
                  label,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: visual.foreground,
                    fontWeight: FontWeight.w700,
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
