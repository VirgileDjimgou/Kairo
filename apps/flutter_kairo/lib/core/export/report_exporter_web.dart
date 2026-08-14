// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use

import 'dart:html' as html;

class ReportExportResult {
  const ReportExportResult({required this.message});
  final String message;
}

Future<ReportExportResult> saveReport({
  required List<int> bytes,
  required String filename,
  required String mediaType,
}) async {
  final html.Blob blob = html.Blob(<List<int>>[bytes], mediaType);
  final String url = html.Url.createObjectUrlFromBlob(blob);
  html.AnchorElement(href: url)
    ..download = filename
    ..click();
  html.Url.revokeObjectUrl(url);
  return const ReportExportResult(message: 'downloaded');
}
