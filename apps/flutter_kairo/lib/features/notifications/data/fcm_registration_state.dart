class FcmRegistrationState {
  const FcmRegistrationState({
    required this.available,
    required this.permissionGranted,
    required this.tokenRegistered,
    this.reason,
  });

  const FcmRegistrationState.unsupported()
    : available = false,
      permissionGranted = false,
      tokenRegistered = false,
      reason = 'unsupported';

  final bool available;
  final bool permissionGranted;
  final bool tokenRegistered;
  final String? reason;
}
