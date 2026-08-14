import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';

class AppSectionHeader extends StatelessWidget {
  const AppSectionHeader({
    super.key,
    required this.title,
    this.eyebrow,
    this.trailing,
  });

  final String title;
  final String? eyebrow;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.end,
    children: <Widget>[
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            if (eyebrow != null) ...<Widget>[
              Text(
                eyebrow!.toUpperCase(),
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: AppSpacing.xs),
            ],
            Text(title, style: Theme.of(context).textTheme.titleLarge),
          ],
        ),
      ),
      if (trailing != null) ...<Widget>[
        const SizedBox(width: AppSpacing.md),
        trailing!,
      ],
    ],
  );
}
