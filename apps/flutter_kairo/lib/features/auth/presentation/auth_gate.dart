import 'dart:async';

import 'package:flutter/material.dart';

import '../../../app/app_environment.dart';
import '../../../app/localization/kairo_localizations.dart';
import '../../chat/data/chat_gateway.dart';
import '../../finance/data/finance_gateway.dart';
import '../../finance/data/member_statement_gateway.dart';
import '../../finance/data/receipt_gateway.dart';
import '../../finance/presentation/receipt_controller.dart';
import '../../foundation/presentation/role_shell.dart';
import '../../governance/data/governance_gateway.dart';
import '../../governance/data/operation_journal_gateway.dart';
import '../../members/data/member_gateway.dart';
import '../../members/presentation/member_controller.dart';
import '../../notifications/data/device_registration.dart';
import '../../notifications/data/inbox_gateway.dart';
import '../data/auth_models.dart';
import 'account_security_page.dart';
import 'session_controller.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({
    super.key,
    required this.controller,
    required this.locale,
    required this.onLocaleChanged,
    required this.environment,
  });
  final SessionController controller;
  final KairoLocale locale;
  final ValueChanged<KairoLocale> onLocaleChanged;
  final KairoEnvironment environment;
  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _tenantChosen = false;
  bool _securityOpen = false;
  late final MemberController _memberController;
  late final ReceiptController _receiptController;
  late final ReceiptGateway _receiptGateway;
  late final MemberStatementGateway _memberStatementGateway;
  late final FinanceGateway _financeGateway;
  late final HttpInboxGateway _inboxGateway;
  late final DeviceRegistration _deviceRegistration;
  late final OperationJournalGateway _operationJournalGateway;
  late final GovernanceGateway _governanceGateway;
  late final ChatGateway _chatGateway;
  String? _pendingNotificationTarget;
  @override
  void initState() {
    super.initState();
    widget.controller.apiClient.offlineWorkspace =
        widget.controller.offlineWorkspace;
    _memberController = MemberController(
      gateway: HttpMemberGateway(widget.controller.apiClient),
    );
    _receiptGateway = HttpReceiptGateway(widget.controller.apiClient);
    _memberStatementGateway = HttpMemberStatementGateway(
      widget.controller.apiClient,
    );
    _financeGateway = HttpFinanceGateway(widget.controller.apiClient);
    _inboxGateway = HttpInboxGateway(widget.controller.apiClient);
    _deviceRegistration = DeviceRegistration();
    _operationJournalGateway = HttpOperationJournalGateway(
      widget.controller.apiClient,
    );
    _governanceGateway = HttpGovernanceGateway(widget.controller.apiClient);
    _chatGateway = HttpChatGateway(widget.controller.apiClient);
    _receiptController = ReceiptController(gateway: _receiptGateway);
    widget.controller.addListener(_changed);
    widget.controller.restore();
  }

  @override
  void dispose() {
    widget.controller.removeListener(_changed);
    _memberController.dispose();
    _receiptController.dispose();
    super.dispose();
  }

  void _changed() {
    final KairoUser? user = widget.controller.user;
    if (widget.controller.phase == SessionPhase.authenticated && user != null) {
      _registerDevice(user);
    } else {
      unawaited(_deviceRegistration.clearSessionBinding());
    }
    if (mounted) setState(() {});
  }

  Future<void> _registerDevice(KairoUser user) async {
    try {
      await _deviceRegistration.registerForSession(
        gateway: _inboxGateway,
        userId: user.id,
        tenantId: user.tenantId,
      );
      await _deviceRegistration.configureNotificationOpens((String targetPath) {
        if (mounted) setState(() => _pendingNotificationTarget = targetPath);
      });
    } catch (_) {
      // Device registration must never block a valid authenticated session.
    }
  }

  @override
  Widget build(BuildContext context) {
    switch (widget.controller.phase) {
      case SessionPhase.checking:
        return const Scaffold(body: Center(child: CircularProgressIndicator()));
      case SessionPhase.signedOut:
      case SessionPhase.mfaRequired:
        return LoginPage(controller: widget.controller, locale: widget.locale);
      case SessionPhase.passwordChangeRequired:
        return PasswordReplacementPage(
          controller: widget.controller,
          locale: widget.locale,
        );
      case SessionPhase.authenticated:
        final user = widget.controller.user!;
        if (_securityOpen) {
          return AccountSecurityPage(
            controller: widget.controller,
            locale: widget.locale,
            onBack: () => setState(() => _securityOpen = false),
          );
        }
        if (!_tenantChosen && user.memberships.length > 1) {
          return TenantSelectionPage(
            controller: widget.controller,
            locale: widget.locale,
            onChosen: () => setState(() => _tenantChosen = true),
          );
        }
        return RoleShell(
          environment: widget.environment,
          locale: widget.locale,
          onLocaleChanged: widget.onLocaleChanged,
          user: user,
          onSignOut: widget.controller.signOut,
          onAccountSecurity: () => setState(() => _securityOpen = true),
          memberController: _memberController,
          receiptGateway: _receiptGateway,
          receiptController: _receiptController,
          memberStatementGateway: _memberStatementGateway,
          financeGateway: _financeGateway,
          inboxGateway: _inboxGateway,
          operationJournalGateway: _operationJournalGateway,
          governanceGateway: _governanceGateway,
          chatGateway: _chatGateway,
          offlineWorkspace: widget.controller.offlineWorkspace,
          onEnableAndroidPush: () =>
              _deviceRegistration.activatePush(gateway: _inboxGateway),
          notificationTargetPath: _pendingNotificationTarget,
          onNotificationTargetHandled: () =>
              setState(() => _pendingNotificationTarget = null),
        );
    }
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.controller, required this.locale});
  final SessionController controller;
  final KairoLocale locale;
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _identifier = TextEditingController();
  final _password = TextEditingController();
  final _mfaCode = TextEditingController();
  bool _visible = false;
  @override
  void dispose() {
    _identifier.dispose();
    _password.dispose();
    _mfaCode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final copy = KairoLocalizations(widget.locale);
    final bool mfa = widget.controller.phase == SessionPhase.mfaRequired;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: <Widget>[
                        const Icon(
                          Icons.shield_outlined,
                          size: 48,
                          color: Color(0xff1457a6),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          copy.text(KairoCopyKey.appName),
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          copy.text(KairoCopyKey.signInHelp),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 24),
                        if (!mfa) ...<Widget>[
                          TextFormField(
                            controller: _identifier,
                            autofocus: true,
                            decoration: InputDecoration(
                              labelText: copy.text(KairoCopyKey.identifier),
                            ),
                            validator: (v) => v == null || v.trim().isEmpty
                                ? copy.text(KairoCopyKey.identifier)
                                : null,
                          ),
                          const SizedBox(height: 16),
                          TextFormField(
                            controller: _password,
                            obscureText: !_visible,
                            decoration: InputDecoration(
                              labelText: copy.text(KairoCopyKey.password),
                              suffixIcon: Semantics(
                                button: true,
                                label: _visible
                                    ? copy.text(KairoCopyKey.hidePassword)
                                    : copy.text(KairoCopyKey.showPassword),
                                child: IconButton(
                                  tooltip: _visible
                                      ? copy.text(KairoCopyKey.hidePassword)
                                      : copy.text(KairoCopyKey.showPassword),
                                  onPressed: () =>
                                      setState(() => _visible = !_visible),
                                  icon: Icon(
                                    _visible
                                        ? Icons.visibility_off
                                        : Icons.visibility,
                                  ),
                                ),
                              ),
                            ),
                            validator: (v) => v == null || v.isEmpty
                                ? copy.text(KairoCopyKey.password)
                                : null,
                          ),
                        ] else
                          TextFormField(
                            controller: _mfaCode,
                            keyboardType: TextInputType.number,
                            maxLength: 6,
                            autofocus: true,
                            decoration: InputDecoration(
                              labelText: copy.text(KairoCopyKey.mfaCode),
                            ),
                            validator: (v) => v == null || v.length != 6
                                ? copy.text(KairoCopyKey.mfaCode)
                                : null,
                          ),
                        if (widget.controller.errorMessage != null) ...<Widget>[
                          const SizedBox(height: 16),
                          _ErrorBox(
                            message:
                                widget.controller.errorMessage ==
                                    'service_unavailable'
                                ? copy.text(KairoCopyKey.apiUnavailable)
                                : widget.controller.errorMessage!,
                          ),
                        ],
                        const SizedBox(height: 24),
                        FilledButton(
                          onPressed: () async {
                            if (!_formKey.currentState!.validate()) return;
                            if (mfa) {
                              await widget.controller.completeMfa(
                                _mfaCode.text,
                              );
                            } else {
                              await widget.controller.login(
                                _identifier.text,
                                _password.text,
                              );
                            }
                          },
                          child: Text(
                            mfa
                                ? copy.text(KairoCopyKey.verifyMfa)
                                : copy.text(KairoCopyKey.signIn),
                          ),
                        ),
                        if (!mfa)
                          TextButton(
                            onPressed: () async {
                              final ScaffoldMessengerState messenger =
                                  ScaffoldMessenger.of(context);
                              if (_identifier.text.trim().isEmpty) {
                                _formKey.currentState!.validate();
                                return;
                              }
                              try {
                                await widget.controller.requestPasswordReset(
                                  _identifier.text.trim(),
                                );
                                if (mounted) {
                                  messenger.showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        copy.text(
                                          KairoCopyKey.passwordResetRequested,
                                        ),
                                      ),
                                    ),
                                  );
                                }
                              } catch (_) {
                                if (mounted) {
                                  messenger.showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        copy.text(KairoCopyKey.apiUnavailable),
                                      ),
                                    ),
                                  );
                                }
                              }
                            },
                            child: Text(copy.text(KairoCopyKey.forgotPassword)),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class PasswordReplacementPage extends StatefulWidget {
  const PasswordReplacementPage({
    super.key,
    required this.controller,
    required this.locale,
  });
  final SessionController controller;
  final KairoLocale locale;
  @override
  State<PasswordReplacementPage> createState() =>
      _PasswordReplacementPageState();
}

class _PasswordReplacementPageState extends State<PasswordReplacementPage> {
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  @override
  void dispose() {
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final copy = KairoLocalizations(widget.locale);
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 460),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    Text(
                      copy.text(KairoCopyKey.passwordUpdateTitle),
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    Text(copy.text(KairoCopyKey.passwordUpdateBody)),
                    const SizedBox(height: 20),
                    TextField(
                      controller: _password,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: copy.text(KairoCopyKey.newPassword),
                        helperText: copy.text(KairoCopyKey.passwordRules),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _confirm,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: copy.text(KairoCopyKey.confirmPassword),
                      ),
                    ),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: () async {
                        if (_password.text.length < 8 ||
                            _password.text != _confirm.text) {
                          return;
                        }
                        await widget.controller.replaceInitialPassword(
                          _password.text,
                        );
                      },
                      child: Text(copy.text(KairoCopyKey.savePassword)),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class TenantSelectionPage extends StatelessWidget {
  const TenantSelectionPage({
    super.key,
    required this.controller,
    required this.locale,
    required this.onChosen,
  });
  final SessionController controller;
  final KairoLocale locale;
  final VoidCallback onChosen;
  @override
  Widget build(BuildContext context) {
    final copy = KairoLocalizations(locale);
    final user = controller.user!;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 540),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    Text(
                      copy.text(KairoCopyKey.tenantSelectionTitle),
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    Text(copy.text(KairoCopyKey.tenantSelectionBody)),
                    const SizedBox(height: 16),
                    ...user.memberships.map(
                      (membership) => ListTile(
                        title: Text(membership.name),
                        subtitle: Text(membership.roles.join(', ')),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () async {
                          await controller.switchTenant(membership.tenantId);
                          onChosen();
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ErrorBox extends StatelessWidget {
  const _ErrorBox({required this.message});
  final String message;
  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: true,
    child: Container(
      padding: const EdgeInsets.all(12),
      color: Colors.red.shade50,
      child: Text(message, style: TextStyle(color: Colors.red.shade900)),
    ),
  );
}
