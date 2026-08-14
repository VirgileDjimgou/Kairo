import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../../../design_system/components/app_section_header.dart';
import '../../../design_system/components/app_state_panel.dart';
import '../../../design_system/components/app_surface_card.dart';
import '../../../design_system/theme/app_tokens.dart';
import '../data/auth_models.dart';
import 'session_controller.dart';

class AccountSecurityPage extends StatefulWidget {
  const AccountSecurityPage({
    super.key,
    required this.controller,
    required this.locale,
    required this.onBack,
  });
  final SessionController controller;
  final KairoLocale locale;
  final VoidCallback onBack;
  @override
  State<AccountSecurityPage> createState() => _AccountSecurityPageState();
}

class _AccountSecurityPageState extends State<AccountSecurityPage> {
  final _currentPassword = TextEditingController();
  final _newPassword = TextEditingController();
  final _confirmation = TextEditingController();
  final _mfaCode = TextEditingController();
  bool _loading = false;
  String? _message;
  String? _error;
  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _currentPassword.dispose();
    _newPassword.dispose();
    _confirmation.dispose();
    _mfaCode.dispose();
    super.dispose();
  }

  Future<void> _load() => _run(() => widget.controller.loadSecurityState());
  Future<void> _run(Future<void> Function() action, {String? success}) async {
    setState(() {
      _loading = true;
      _error = null;
      _message = null;
    });
    try {
      await action();
      if (mounted) {
        setState(() => _message = success);
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => _error = KairoLocalizations(
            widget.locale,
          ).text(KairoCopyKey.apiUnavailable),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final copy = KairoLocalizations(widget.locale);
    final MfaStatus? status = widget.controller.mfaStatus;
    return Scaffold(
      appBar: AppBar(title: Text(copy.text(KairoCopyKey.securityCenter))),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 900),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  if (_message != null)
                    _Notice(color: Colors.green, message: _message!),
                  if (_error != null)
                    _Notice(color: Colors.red, message: _error!),
                  AppSectionHeader(
                    title: copy.text(KairoCopyKey.securityCenter),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  _mfaCard(copy, status),
                  const SizedBox(height: 16),
                  _passwordCard(copy),
                  const SizedBox(height: 16),
                  _sessionsCard(copy),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _mfaCard(KairoLocalizations copy, MfaStatus? status) => _SectionCard(
    title: copy.text(KairoCopyKey.mfa),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Chip(
          label: Text(
            status?.enabled == true
                ? copy.text(KairoCopyKey.mfaEnabled)
                : copy.text(KairoCopyKey.mfaDisabled),
          ),
        ),
        if (widget.controller.mfaEnrollment == null && status?.enabled != true)
          FilledButton(
            onPressed: _loading
                ? null
                : () => _run(() => widget.controller.startMfaEnrollment()),
            child: Text(copy.text(KairoCopyKey.enableMfa)),
          ),
        if (widget.controller.mfaEnrollment != null) ...<Widget>[
          Text(copy.text(KairoCopyKey.mfaSetupInstructions)),
          SelectableText(
            '${copy.text(KairoCopyKey.manualMfaKey)}: ${widget.controller.mfaEnrollment!.secret}',
          ),
          TextField(
            controller: _mfaCode,
            maxLength: 6,
            decoration: InputDecoration(
              labelText: copy.text(KairoCopyKey.securityCode),
            ),
          ),
          FilledButton(
            onPressed: _loading
                ? null
                : () => _run(
                    () => widget.controller.verifyMfaEnrollment(_mfaCode.text),
                  ),
            child: Text(copy.text(KairoCopyKey.verifyMfa)),
          ),
        ],
        if (status?.enabled == true)
          OutlinedButton(
            onPressed: _loading
                ? null
                : () => _run(() => widget.controller.disableMfa()),
            child: Text(copy.text(KairoCopyKey.disableMfa)),
          ),
      ],
    ),
  );

  Widget _passwordCard(KairoLocalizations copy) => _SectionCard(
    title: copy.text(KairoCopyKey.changePassword),
    child: Column(
      children: <Widget>[
        TextField(
          controller: _currentPassword,
          obscureText: true,
          decoration: InputDecoration(
            labelText: copy.text(KairoCopyKey.currentPassword),
          ),
        ),
        TextField(
          controller: _newPassword,
          obscureText: true,
          decoration: InputDecoration(
            labelText: copy.text(KairoCopyKey.newPassword),
          ),
        ),
        TextField(
          controller: _confirmation,
          obscureText: true,
          decoration: InputDecoration(
            labelText: copy.text(KairoCopyKey.confirmPassword),
          ),
        ),
        FilledButton(
          onPressed: _loading
              ? null
              : () {
                  if (_newPassword.text.length < 8 ||
                      _newPassword.text != _confirmation.text) {
                    setState(
                      () =>
                          _error = copy.text(KairoCopyKey.passwordsDoNotMatch),
                    );
                    return;
                  }
                  _run(
                    () => widget.controller.changePassword(
                      _currentPassword.text,
                      _newPassword.text,
                    ),
                    success: copy.text(KairoCopyKey.passwordUpdated),
                  );
                },
          child: Text(copy.text(KairoCopyKey.changePassword)),
        ),
      ],
    ),
  );

  Widget _sessionsCard(KairoLocalizations copy) => _SectionCard(
    title: copy.text(KairoCopyKey.activeSessions),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        if (widget.controller.activeSessions.where((s) => !s.current).isEmpty)
          Text(copy.text(KairoCopyKey.noOtherSessions)),
        ...widget.controller.activeSessions.map(
          (ActiveSession session) => ListTile(
            title: Text(
              session.current
                  ? copy.text(KairoCopyKey.currentSession)
                  : (session.deviceLabel.isEmpty
                        ? copy.text(KairoCopyKey.unknownDevice)
                        : session.deviceLabel),
            ),
            trailing: session.current
                ? null
                : OutlinedButton(
                    onPressed: _loading
                        ? null
                        : () => _run(
                            () => widget.controller.revokeSession(session.id),
                          ),
                    child: Text(copy.text(KairoCopyKey.revoke)),
                  ),
          ),
        ),
        if (widget.controller.activeSessions.any((s) => !s.current))
          OutlinedButton(
            onPressed: _loading
                ? null
                : () => _run(() => widget.controller.revokeOtherSessions()),
            child: Text(copy.text(KairoCopyKey.revokeOtherSessions)),
          ),
        OutlinedButton(
          onPressed: _loading
              ? null
              : () => _run(() => widget.controller.revokeAllSessions()),
          child: Text(copy.text(KairoCopyKey.revokeAllSessions)),
        ),
      ],
    ),
  );
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child});
  final String title;
  final Widget child;
  @override
  Widget build(BuildContext context) => AppSurfaceCard(
    tone: AppCardTone.secondary,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(title, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 16),
        child,
      ],
    ),
  );
}

class _Notice extends StatelessWidget {
  const _Notice({required this.color, required this.message});
  final Color color;
  final String message;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
    child: AppStatePanel(
      icon: color == Colors.red ? Icons.error_outline : Icons.check_circle,
      title: message,
      tone: color == Colors.red ? AppCardTone.danger : AppCardTone.success,
    ),
  );
}
