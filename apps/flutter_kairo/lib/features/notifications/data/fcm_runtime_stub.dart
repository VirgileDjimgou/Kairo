import 'fcm_registration_state.dart';
import 'inbox_gateway.dart';

class FcmRuntime {
  const FcmRuntime();

  Future<void> configureNotificationOpens(
    void Function(String targetPath) onTargetPath,
  ) async {}

  Future<FcmRegistrationState> activate({
    required DeviceRegistrationGateway gateway,
    required String installationId,
  }) async => const FcmRegistrationState.unsupported();

  Future<void> clearSessionBinding() async {}
}
