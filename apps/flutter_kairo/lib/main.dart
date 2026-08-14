import 'package:flutter/widgets.dart';

import 'app/app_environment.dart';
import 'app/kairo_app.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(KairoApp(environment: KairoEnvironment.fromDartDefines()));
}
