import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';

abstract final class AppFeedback {
  static void show(
    BuildContext context, {
    required String message,
    AppStatus status = AppStatus.info,
    SnackBarAction? action,
  }) {
    final AppStatusVisual visual = AppStatusVisual.of(
      status,
      Theme.of(context).brightness,
    );
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Row(
            children: <Widget>[
              Icon(
                visual.icon,
                color: Theme.of(context).colorScheme.onInverseSurface,
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(child: Text(message)),
            ],
          ),
          action: action,
        ),
      );
  }
}
