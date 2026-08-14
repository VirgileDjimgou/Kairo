import 'package:flutter_test/flutter_test.dart';
import 'package:kairo_flutter/app/app_environment.dart';

void main() {
  test(
    'allows a relative development API path when no endpoint is provided',
    () {
      final KairoEnvironment environment = KairoEnvironment.fromValues(
        flavor: 'development',
        apiBaseUrl: '',
      );

      expect(
        environment.resolveApiUri('health').path,
        contains('api/v1/health'),
      );
    },
  );

  test('requires HTTPS for production endpoints', () {
    expect(
      () => KairoEnvironment.fromValues(
        flavor: 'production',
        apiBaseUrl: 'http://api.example.test',
      ),
      throwsA(isA<KairoConfigurationException>()),
    );
  });

  test('resolves configured production paths', () {
    final KairoEnvironment environment = KairoEnvironment.fromValues(
      flavor: 'production',
      apiBaseUrl: 'https://api.example.test/api/v1',
    );

    expect(
      environment.resolveApiUri('members').toString(),
      'https://api.example.test/api/v1/members',
    );
  });
}
