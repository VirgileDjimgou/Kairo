import 'dart:io';

import 'package:share_plus/share_plus.dart';

class ReportExportResult {
  const ReportExportResult({required this.message});
  final String message;
}

Future<ReportExportResult> saveReport({
  required List<int> bytes,
  required String filename,
  required String mediaType,
}) async {
  final File file = File(
    '${Directory.systemTemp.path}${Platform.pathSeparator}$filename',
  );
  await file.writeAsBytes(bytes, flush: true);
  await SharePlus.instance.share(
    ShareParams(
      files: <XFile>[XFile(file.path, mimeType: mediaType)],
      subject: filename,
    ),
  );
  return ReportExportResult(message: file.path);
}
