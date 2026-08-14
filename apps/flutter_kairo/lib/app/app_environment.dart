enum KairoDeployment { development, staging, production }

class KairoConfigurationException implements Exception {
  const KairoConfigurationException(this.message);

  final String message;

  @override
  String toString() => 'KairoConfigurationException: $message';
}

class KairoEnvironment {
  const KairoEnvironment._({
    required this.deployment,
    required this.apiBaseUrl,
  });

  factory KairoEnvironment.fromDartDefines() {
    return KairoEnvironment.fromValues(
      flavor: const String.fromEnvironment(
        'KAIRO_FLAVOR',
        defaultValue: 'development',
      ),
      apiBaseUrl: const String.fromEnvironment('KAIRO_API_BASE_URL'),
    );
  }

  factory KairoEnvironment.fromValues({
    required String flavor,
    required String apiBaseUrl,
  }) {
    final KairoDeployment deployment = switch (flavor.trim().toLowerCase()) {
      'staging' => KairoDeployment.staging,
      'production' => KairoDeployment.production,
      _ => KairoDeployment.development,
    };
    final String normalizedBaseUrl = apiBaseUrl.trim().replaceFirst(
      RegExp(r'/+$'),
      '',
    );

    if (normalizedBaseUrl.isEmpty &&
        deployment != KairoDeployment.development) {
      throw const KairoConfigurationException(
        'KAIRO_API_BASE_URL is required for staging and production builds.',
      );
    }

    if (normalizedBaseUrl.isNotEmpty) {
      final Uri? parsedUrl = Uri.tryParse(normalizedBaseUrl);
      if (parsedUrl == null ||
          !parsedUrl.hasScheme ||
          !parsedUrl.hasAuthority) {
        throw const KairoConfigurationException(
          'KAIRO_API_BASE_URL must be an absolute URL.',
        );
      }
      if (deployment != KairoDeployment.development &&
          parsedUrl.scheme != 'https') {
        throw const KairoConfigurationException(
          'Production and staging API URLs must use HTTPS.',
        );
      }
    }

    return KairoEnvironment._(
      deployment: deployment,
      apiBaseUrl: normalizedBaseUrl,
    );
  }

  final KairoDeployment deployment;
  final String apiBaseUrl;

  bool get hasApiBaseUrl => apiBaseUrl.isNotEmpty;

  Uri resolveApiUri(String path) {
    final String normalizedPath = path.replaceFirst(RegExp(r'^/+'), '');
    if (!hasApiBaseUrl) {
      return Uri.base.resolve('api/v1/$normalizedPath');
    }
    return Uri.parse('$apiBaseUrl/$normalizedPath');
  }
}
