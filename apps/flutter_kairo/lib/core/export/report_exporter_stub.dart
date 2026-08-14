class ReportExportResult {
  const ReportExportResult({required this.message});
  final String message;
}

Future<ReportExportResult> saveReport({
  required List<int> bytes,
  required String filename,
  required String mediaType,
}) async => const ReportExportResult(message: 'unsupported');
