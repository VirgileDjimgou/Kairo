import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../app/app_environment.dart';
import '../offline/offline_workspace_controller.dart';

class KairoApiException implements Exception {
  const KairoApiException({required this.statusCode, required this.message});

  factory KairoApiException.fromResponse(http.Response response) {
    String message = 'The Kairo API request failed.';
    try {
      final Object? payload = jsonDecode(response.body);
      if (payload is Map<String, dynamic> && payload['detail'] is String) {
        message = payload['detail'] as String;
      }
    } on FormatException {
      // API errors are allowed to be plain text.
    }
    return KairoApiException(statusCode: response.statusCode, message: message);
  }

  final int statusCode;
  final String message;

  @override
  String toString() => 'KairoApiException($statusCode): $message';
}

class KairoApiClient {
  KairoApiClient({required this.environment, http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client();

  final KairoEnvironment environment;
  final http.Client _httpClient;
  static const Duration _requestTimeout = Duration(seconds: 20);
  String? _accessToken;
  OfflineWorkspaceController? offlineWorkspace;

  set accessToken(String? value) => _accessToken = value;

  Future<Map<String, dynamic>> getJson(String path) async {
    final Object? payload = await requestJson('GET', path);
    if (payload is! Map<String, dynamic>) {
      throw const KairoApiException(
        statusCode: 200,
        message: 'The Kairo API returned an unexpected response.',
      );
    }
    return payload;
  }

  Future<Object?> requestJson(
    String method,
    String path, {
    Object? body,
    String? bearerToken,
  }) async {
    final Map<String, String> headers = <String, String>{
      'Accept': 'application/json',
    };
    final String? token = bearerToken ?? _accessToken;
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    if (body != null) {
      headers['Content-Type'] = 'application/json';
    }
    final http.Request request = http.Request(
      method,
      environment.resolveApiUri(path),
    )..headers.addAll(headers);
    if (body != null) request.body = jsonEncode(body);
    final http.StreamedResponse streamed;
    try {
      streamed = await _httpClient.send(request).timeout(_requestTimeout);
      offlineWorkspace?.reportConnectivity(true);
    } catch (_) {
      offlineWorkspace?.reportConnectivity(false);
      if (method == 'GET') {
        final cached = await offlineWorkspace?.readCached(path);
        if (cached != null) return cached;
      }
      rethrow;
    }
    final http.Response response = await http.Response.fromStream(streamed);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw KairoApiException.fromResponse(response);
    }
    if (response.body.trim().isEmpty) return null;
    final payload = jsonDecode(response.body);
    if (method == 'GET') await offlineWorkspace?.cacheRead(path, payload);
    return payload;
  }

  Future<List<int>> requestBytes(String path) async {
    final Map<String, String> headers = <String, String>{};
    if (_accessToken != null && _accessToken!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    final http.Response response;
    try {
      response = await _httpClient
          .get(environment.resolveApiUri(path), headers: headers)
          .timeout(_requestTimeout);
      offlineWorkspace?.reportConnectivity(true);
    } catch (_) {
      offlineWorkspace?.reportConnectivity(false);
      rethrow;
    }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw KairoApiException.fromResponse(response);
    }
    return response.bodyBytes;
  }

  Future<Map<String, dynamic>> uploadFile({
    required String path,
    required String filename,
    required List<int> bytes,
    required Map<String, String> fields,
  }) async {
    final http.MultipartRequest request =
        http.MultipartRequest('POST', environment.resolveApiUri(path))
          ..headers['Accept'] = 'application/json'
          ..fields.addAll(fields)
          ..files.add(
            http.MultipartFile.fromBytes('file', bytes, filename: filename),
          );
    if (_accessToken != null && _accessToken!.isNotEmpty) {
      request.headers['Authorization'] = 'Bearer $_accessToken';
    }
    final http.StreamedResponse streamed;
    try {
      streamed = await request.send().timeout(_requestTimeout);
      offlineWorkspace?.reportConnectivity(true);
    } catch (_) {
      offlineWorkspace?.reportConnectivity(false);
      rethrow;
    }
    final http.Response response = await http.Response.fromStream(streamed);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw KairoApiException.fromResponse(response);
    }
    final Object? payload = jsonDecode(response.body);
    if (payload is! Map<String, dynamic>) {
      throw const KairoApiException(
        statusCode: 200,
        message: 'The Kairo API returned an unexpected upload response.',
      );
    }
    return payload;
  }

  Stream<Map<String, dynamic>> requestSse(
    String path, {
    required Object body,
  }) async* {
    final Map<String, String> headers = <String, String>{
      'Accept': 'text/event-stream',
      'Content-Type': 'application/json',
    };
    if (_accessToken != null && _accessToken!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    final http.Request request =
        http.Request('POST', environment.resolveApiUri(path))
          ..headers.addAll(headers)
          ..body = jsonEncode(body);
    final http.StreamedResponse response;
    try {
      response = await _httpClient.send(request).timeout(_requestTimeout);
      offlineWorkspace?.reportConnectivity(true);
    } catch (_) {
      offlineWorkspace?.reportConnectivity(false);
      rethrow;
    }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw KairoApiException.fromResponse(
        await http.Response.fromStream(response),
      );
    }
    await for (final String line
        in response.stream
            .transform(utf8.decoder)
            .transform(const LineSplitter())) {
      if (!line.startsWith('data: ')) continue;
      final Object? decoded = jsonDecode(line.substring(6));
      if (decoded is Map<String, dynamic>) yield decoded;
    }
  }

  void dispose() => _httpClient.close();
}
