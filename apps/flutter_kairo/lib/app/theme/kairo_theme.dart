import 'package:flutter/material.dart';

import '../../design_system/theme/app_theme.dart';
import '../../design_system/theme/app_tokens.dart';

/// Compatibility facade retained while feature screens move to the design system.
/// New code should use AppTheme and AppPalette directly.
abstract final class KairoColors {
  static const Color primary = AppPalette.blue;
  static const Color primaryDark = AppPalette.navy;
  static const Color canvas = AppPalette.canvas;
  static const Color border = AppPalette.outline;
  static const Color success = AppPalette.green;
  static const Color warning = AppPalette.amber;
  static const Color danger = AppPalette.red;
}

abstract final class KairoTheme {
  static ThemeData light() => AppTheme.light();

  static ThemeData dark() => AppTheme.dark();
}
