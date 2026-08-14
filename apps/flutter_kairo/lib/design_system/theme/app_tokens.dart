import 'package:flutter/material.dart';

/// Brand and semantic colours shared by every Kairo surface.
abstract final class AppPalette {
  static const Color blue = Color(0xFF195AA6);
  static const Color navy = Color(0xFF102A43);
  static const Color teal = Color(0xFF007C83);
  static const Color violet = Color(0xFF635BBD);
  static const Color green = Color(0xFF147A43);
  static const Color amber = Color(0xFF9A6200);
  static const Color red = Color(0xFFB4233A);
  static const Color canvas = Color(0xFFF6F8FC);
  static const Color outline = Color(0xFFCDD6E1);
}

abstract final class AppSpacing {
  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 20;
  static const double xl = 24;
  static const double xxl = 32;
  static const double xxxl = 40;
}

abstract final class AppRadius {
  static const BorderRadius small = BorderRadius.all(Radius.circular(10));
  static const BorderRadius medium = BorderRadius.all(Radius.circular(16));
  static const BorderRadius large = BorderRadius.all(Radius.circular(24));
}

abstract final class AppMotion {
  static const Duration quick = Duration(milliseconds: 160);
  static const Duration standard = Duration(milliseconds: 240);
  static const Curve emphasis = Curves.easeOutCubic;
}

enum AppStatus { paid, pending, overdue, active, suspended, open, closed, info }

class AppStatusVisual {
  const AppStatusVisual({
    required this.icon,
    required this.foreground,
    required this.background,
  });

  final IconData icon;
  final Color foreground;
  final Color background;

  static AppStatusVisual of(AppStatus status, Brightness brightness) {
    final bool dark = brightness == Brightness.dark;
    Color container(Color light, Color darkValue) => dark ? darkValue : light;
    return switch (status) {
      AppStatus.paid || AppStatus.active || AppStatus.closed => AppStatusVisual(
        icon: status == AppStatus.closed
            ? Icons.task_alt_rounded
            : Icons.check_circle_rounded,
        foreground: dark ? const Color(0xFF8FE8B4) : AppPalette.green,
        background: container(const Color(0xFFDDF5E6), const Color(0xFF173D2B)),
      ),
      AppStatus.pending || AppStatus.open => AppStatusVisual(
        icon: status == AppStatus.open
            ? Icons.folder_open_rounded
            : Icons.schedule_rounded,
        foreground: dark ? const Color(0xFFFFD18A) : AppPalette.amber,
        background: container(const Color(0xFFFFEED0), const Color(0xFF49350D)),
      ),
      AppStatus.overdue || AppStatus.suspended => AppStatusVisual(
        icon: status == AppStatus.suspended
            ? Icons.pause_circle_rounded
            : Icons.error_outline_rounded,
        foreground: dark ? const Color(0xFFFFB1B8) : AppPalette.red,
        background: container(const Color(0xFFFFE1E4), const Color(0xFF4A1D25)),
      ),
      AppStatus.info => AppStatusVisual(
        icon: Icons.info_outline_rounded,
        foreground: dark ? const Color(0xFF9DCCFF) : AppPalette.blue,
        background: container(const Color(0xFFDCEBFF), const Color(0xFF173A62)),
      ),
    };
  }
}
