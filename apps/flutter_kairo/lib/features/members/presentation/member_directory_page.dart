import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../../../app/theme/kairo_theme.dart';
import '../../../design_system/components/app_section_header.dart';
import '../../../design_system/components/app_state_panel.dart';
import '../../../design_system/components/app_status_badge.dart';
import '../../../design_system/components/app_surface_card.dart';
import '../../../design_system/theme/app_tokens.dart';
import '../data/member_models.dart';
import 'member_controller.dart';

class MemberDirectoryPage extends StatefulWidget {
  const MemberDirectoryPage({
    super.key,
    required this.controller,
    required this.locale,
    required this.canCreate,
  });
  final MemberController controller;
  final KairoLocale locale;
  final bool canCreate;

  @override
  State<MemberDirectoryPage> createState() => _MemberDirectoryPageState();
}

class _MemberDirectoryPageState extends State<MemberDirectoryPage> {
  final TextEditingController _query = TextEditingController();
  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_changed);
    widget.controller.load();
  }

  @override
  void dispose() {
    _query.dispose();
    widget.controller.removeListener(_changed);
    super.dispose();
  }

  void _changed() {
    if (mounted) setState(() {});
  }

  void _search(String value) => widget.controller.load(query: value);

  @override
  Widget build(BuildContext context) {
    final _MembersText text = _MembersText(widget.locale);
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final bool desktop = constraints.maxWidth >= 900;
        final Widget directory = _Directory(
          text: text,
          controller: widget.controller,
          query: _query,
          onSearch: _search,
          onCreate: widget.canCreate ? () => _openCreate(text) : null,
          onStatus: _changeStatus,
        );
        final Widget detail = _MemberDetail(
          text: text,
          member: widget.controller.selected,
          onStatus: _changeStatus,
          onEdit: widget.canCreate ? _editMember : null,
        );
        return Padding(
          padding: const EdgeInsets.all(20),
          child: desktop
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Expanded(flex: 3, child: directory),
                    const SizedBox(width: 20),
                    SizedBox(width: 340, child: detail),
                  ],
                )
              : Column(
                  children: <Widget>[
                    Expanded(child: directory),
                    if (widget.controller.selected != null)
                      const SizedBox(height: 12),
                    if (widget.controller.selected != null) detail,
                  ],
                ),
        );
      },
    );
  }

  Future<void> _changeStatus(MemberProfile member, String next) async {
    final _MembersText text = _MembersText(widget.locale);
    final bool? approved = await showDialog<bool>(
      context: context,
      builder: (BuildContext dialogContext) => AlertDialog(
        title: Text(next == 'paused' ? text.pauseTitle : text.reactivateTitle),
        content: Text(text.statusConfirm(member.displayName, next)),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: Text(text.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: Text(text.confirm),
          ),
        ],
      ),
    );
    if (approved != true || !mounted) return;
    final bool ok = await widget.controller.changeStatus(member, next);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok
              ? text.statusSaved
              : (widget.controller.error ?? text.operationFailed),
        ),
        backgroundColor: ok ? KairoColors.success : Colors.red.shade700,
      ),
    );
  }

  Future<void> _openCreate(_MembersText text) async {
    final bool? saved = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (BuildContext context) =>
          _MemberCreateSheet(controller: widget.controller, text: text),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(text.memberCreated),
          backgroundColor: KairoColors.success,
        ),
      );
    }
  }

  Future<void> _editMember(MemberProfile member) async {
    final TextEditingController display = TextEditingController(
      text: member.displayName,
    );
    final TextEditingController phone = TextEditingController(
      text: member.phone ?? '',
    );
    final _MembersText text = _MembersText(widget.locale);
    final bool? confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) => AlertDialog(
        title: Text(text.editMember),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            TextField(
              controller: display,
              decoration: InputDecoration(labelText: text.displayName),
            ),
            TextField(
              controller: phone,
              decoration: InputDecoration(labelText: text.phone),
            ),
          ],
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(text.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(text.save),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      final bool ok = await widget.controller.update(member, <String, dynamic>{
        'display_name': display.text.trim(),
        'phone': phone.text.trim().isEmpty ? null : phone.text.trim(),
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              ok
                  ? text.memberSaved
                  : (widget.controller.error ?? text.operationFailed),
            ),
            backgroundColor: ok ? KairoColors.success : Colors.red.shade700,
          ),
        );
      }
    }
    display.dispose();
    phone.dispose();
  }
}

class _Directory extends StatelessWidget {
  const _Directory({
    required this.text,
    required this.controller,
    required this.query,
    required this.onSearch,
    required this.onCreate,
    required this.onStatus,
  });
  final _MembersText text;
  final MemberController controller;
  final TextEditingController query;
  final ValueChanged<String> onSearch;
  final VoidCallback? onCreate;
  final Future<void> Function(MemberProfile, String) onStatus;
  @override
  Widget build(BuildContext context) => AppSurfaceCard(
    padding: const EdgeInsets.all(AppSpacing.lg),
    child: ListView(
      shrinkWrap: true,
      children: <Widget>[
        AppSectionHeader(
          eyebrow: text.directoryKicker,
          title: text.title,
          trailing: onCreate == null
              ? null
              : FilledButton.icon(
                  onPressed: onCreate,
                  icon: const Icon(Icons.person_add_alt_1),
                  label: Text(text.addMember),
                ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: query,
          onChanged: onSearch,
          decoration: InputDecoration(
            prefixIcon: const Icon(Icons.search),
            hintText: text.searchHint,
            suffixIcon: IconButton(
              onPressed: () {
                query.clear();
                onSearch('');
              },
              icon: const Icon(Icons.refresh),
              tooltip: text.refresh,
            ),
          ),
        ),
        const SizedBox(height: 12),
        if (controller.error != null) _InlineError(message: controller.error!),
        if (controller.loading)
          const Padding(
            padding: EdgeInsets.all(24),
            child: Center(child: CircularProgressIndicator()),
          )
        else if (controller.members.isEmpty)
          AppStatePanel(icon: Icons.group_off_outlined, title: text.empty)
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: controller.members.length,
            separatorBuilder: (_, int index) => const Divider(height: 1),
            itemBuilder: (BuildContext context, int index) {
              final MemberProfile member = controller.members[index];
              return ListTile(
                selected: controller.selected?.id == member.id,
                onTap: () => controller.select(member),
                leading: CircleAvatar(
                  backgroundColor: member.status == 'active'
                      ? KairoColors.primary.withValues(alpha: .12)
                      : Colors.grey.shade200,
                  child: Text(
                    member.displayName.isEmpty
                        ? '?'
                        : member.displayName.substring(0, 1).toUpperCase(),
                  ),
                ),
                title: Text(member.displayName),
                subtitle: Text(
                  '${member.memberCode} · ${member.email ?? member.phone ?? text.noContact}',
                ),
                trailing: _StatusChip(
                  active: member.status == 'active',
                  text: text,
                ),
              );
            },
          ),
      ],
    ),
  );
}

class _MemberDetail extends StatelessWidget {
  const _MemberDetail({
    required this.text,
    required this.member,
    required this.onStatus,
    this.onEdit,
  });
  final _MembersText text;
  final MemberProfile? member;
  final Future<void> Function(MemberProfile, String) onStatus;
  final Future<void> Function(MemberProfile)? onEdit;
  @override
  Widget build(BuildContext context) {
    if (member == null) {
      return AppStatePanel(
        icon: Icons.touch_app_outlined,
        title: text.selectMember,
      );
    }
    return AppSurfaceCard(
      tone: AppCardTone.secondary,
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Row(
            children: <Widget>[
              CircleAvatar(
                radius: 24,
                child: Text(member!.displayName.substring(0, 1).toUpperCase()),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      member!.displayName,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    Text(member!.memberCode),
                  ],
                ),
              ),
              _StatusChip(active: member!.status == 'active', text: text),
            ],
          ),
          const Divider(height: 28),
          _InfoRow(
            label: text.contact,
            value: member!.email ?? member!.phone ?? text.noContact,
          ),
          _InfoRow(
            label: text.address,
            value: member!.address.isEmpty ? text.notProvided : member!.address,
          ),
          _InfoRow(
            label: text.membershipType,
            value: member!.membershipType == 'family'
                ? text.family
                : text.individual,
          ),
          _InfoRow(
            label: text.joined,
            value: member!.joinedAt?.toIso8601String().split('T').first ?? '—',
          ),
          const SizedBox(height: 16),
          if (onEdit != null)
            OutlinedButton.icon(
              onPressed: () => onEdit!(member!),
              icon: const Icon(Icons.edit_outlined),
              label: Text(text.editMember),
            ),
          if (onEdit != null) const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () => onStatus(
              member!,
              member!.status == 'active' ? 'paused' : 'active',
            ),
            icon: Icon(
              member!.status == 'active'
                  ? Icons.pause_circle_outline
                  : Icons.play_circle_outline,
            ),
            label: Text(
              member!.status == 'active' ? text.pause : text.reactivate,
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(label, style: Theme.of(context).textTheme.labelSmall),
        const SizedBox(height: 2),
        Text(value),
      ],
    ),
  );
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.active, required this.text});
  final bool active;
  final _MembersText text;
  @override
  Widget build(BuildContext context) => AppStatusBadge(
    status: active ? AppStatus.active : AppStatus.pending,
    label: active ? text.active : text.paused,
  );
}

class _InlineError extends StatelessWidget {
  const _InlineError({required this.message});
  final String message;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: AppSpacing.md),
    child: AppStatePanel(
      icon: Icons.error_outline,
      title: message,
      tone: AppCardTone.danger,
    ),
  );
}

class _MemberCreateSheet extends StatefulWidget {
  const _MemberCreateSheet({required this.controller, required this.text});
  final MemberController controller;
  final _MembersText text;
  @override
  State<_MemberCreateSheet> createState() => _MemberCreateSheetState();
}

class _MemberCreateSheetState extends State<_MemberCreateSheet> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final Map<String, TextEditingController> _fields =
      <String, TextEditingController>{
        for (final String key in <String>[
          'first',
          'last',
          'display',
          'street',
          'house',
          'postal',
          'city',
          'phone',
          'login',
          'password',
        ])
          key: TextEditingController(),
      };
  String _type = 'individual';
  bool _access = false;
  @override
  void dispose() {
    for (final TextEditingController controller in _fields.values) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => SafeArea(
    child: Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.viewInsetsOf(context).bottom + 20,
      ),
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              Text(
                widget.text.addMember,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 6),
              Text(widget.text.codePreview),
              const SizedBox(height: 16),
              _field('first', widget.text.firstName),
              _field('last', widget.text.lastName),
              _field('display', widget.text.displayName),
              _field('street', widget.text.street),
              _field('house', widget.text.house),
              _field('postal', widget.text.postal),
              _field('city', widget.text.city),
              DropdownButtonFormField<String>(
                initialValue: 'DE',
                decoration: InputDecoration(labelText: widget.text.country),
                items: const <DropdownMenuItem<String>>[
                  DropdownMenuItem(
                    value: 'DE',
                    child: Text('🇩🇪 Deutschland (+49)'),
                  ),
                ],
                onChanged: (_) {},
              ),
              _field('phone', widget.text.phone, required: false),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: _type,
                decoration: InputDecoration(
                  labelText: widget.text.contribution,
                ),
                items: <DropdownMenuItem<String>>[
                  DropdownMenuItem(
                    value: 'individual',
                    child: Text(widget.text.individual),
                  ),
                  DropdownMenuItem(
                    value: 'family',
                    child: Text(widget.text.family),
                  ),
                ],
                onChanged: (String? value) =>
                    setState(() => _type = value ?? _type),
              ),
              SwitchListTile(
                value: _access,
                onChanged: (bool value) => setState(() => _access = value),
                title: Text(widget.text.directAccess),
                subtitle: Text(widget.text.directAccessHelp),
              ),
              if (_access) ...<Widget>[
                _field('login', widget.text.login, required: false),
                _field(
                  'password',
                  widget.text.temporaryPassword,
                  obscure: true,
                ),
              ],
              const SizedBox(height: 12),
              if (widget.controller.error != null)
                _InlineError(message: widget.controller.error!),
              FilledButton(
                onPressed: widget.controller.saving ? null : _save,
                child: widget.controller.saving
                    ? const CircularProgressIndicator()
                    : Text(widget.text.create),
              ),
            ],
          ),
        ),
      ),
    ),
  );
  Widget _field(
    String key,
    String label, {
    bool required = true,
    bool obscure = false,
  }) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: TextFormField(
      controller: _fields[key],
      obscureText: obscure,
      decoration: InputDecoration(labelText: label),
      validator: required
          ? (String? value) => value == null || value.trim().isEmpty
                ? widget.text.required
                : null
          : null,
    ),
  );
  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    if (_access && _fields['password']!.text.length < 8) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(widget.text.passwordIssue)));
      return;
    }
    final bool ok = await widget.controller.create(
      MemberDraft(
        firstName: _fields['first']!.text,
        lastName: _fields['last']!.text,
        displayName: _fields['display']!.text,
        streetName: _fields['street']!.text,
        houseNumber: _fields['house']!.text,
        postalCode: _fields['postal']!.text,
        city: _fields['city']!.text,
        countryCode: 'DE',
        membershipType: _type,
        phone: _fields['phone']!.text,
        provisionAccess: _access,
        loginIdentifier: _fields['login']!.text,
        temporaryPassword: _fields['password']!.text,
      ),
    );
    if (ok && mounted) Navigator.pop(context, true);
  }
}

class _MembersText {
  const _MembersText(this.locale);
  final KairoLocale locale;
  bool get en => locale == KairoLocale.en;
  bool get de => locale == KairoLocale.de;
  String get directoryKicker => en
      ? 'MEMBER DIRECTORY'
      : de
      ? 'MITGLIEDERVERZEICHNIS'
      : 'ANNUAIRE DES MEMBRES';
  String get title => en
      ? 'Members'
      : de
      ? 'Mitglieder'
      : 'Membres';
  String get addMember => en
      ? 'Add member'
      : de
      ? 'Mitglied hinzufügen'
      : 'Ajouter un membre';
  String get editMember => en
      ? 'Edit member'
      : de
      ? 'Mitglied bearbeiten'
      : 'Modifier le membre';
  String get save => en
      ? 'Save'
      : de
      ? 'Speichern'
      : 'Enregistrer';
  String get memberSaved => en
      ? 'Member updated.'
      : de
      ? 'Mitglied aktualisiert.'
      : 'Membre mis à jour.';
  String get searchHint => en
      ? 'Search name, code, phone or email'
      : de
      ? 'Name, Code, Telefon oder E-Mail suchen'
      : 'Rechercher nom, matricule, téléphone ou e-mail';
  String get refresh => en
      ? 'Reset search'
      : de
      ? 'Suche zurücksetzen'
      : 'Réinitialiser la recherche';
  String get empty => en
      ? 'No member matches this search.'
      : de
      ? 'Kein Mitglied gefunden.'
      : 'Aucun membre ne correspond à cette recherche.';
  String get noContact => en
      ? 'No contact'
      : de
      ? 'Kein Kontakt'
      : 'Sans contact';
  String get selectMember => en
      ? 'Select a member to view their authorised profile.'
      : de
      ? 'Wählen Sie ein Mitglied, um das freigegebene Profil zu sehen.'
      : 'Sélectionnez un membre pour afficher son profil autorisé.';
  String get contact => en
      ? 'CONTACT'
      : de
      ? 'KONTAKT'
      : 'CONTACT';
  String get address => en
      ? 'ADDRESS'
      : de
      ? 'ADRESSE'
      : 'ADRESSE';
  String get membershipType => en
      ? 'MEMBERSHIP'
      : de
      ? 'MITGLIEDSCHAFT'
      : 'ADHÉSION';
  String get joined => en
      ? 'JOINED'
      : de
      ? 'BEIGETRETEN'
      : 'INSCRIT LE';
  String get notProvided => en
      ? 'Not provided'
      : de
      ? 'Nicht angegeben'
      : 'Non renseignée';
  String get individual => en
      ? 'Individual — €60/year'
      : de
      ? 'Einzelmitglied — 60 €/Jahr'
      : 'Membre individuel — 60 €/an';
  String get family => en
      ? 'Family — €100/year'
      : de
      ? 'Familienmitglied — 100 €/Jahr'
      : 'Membre famille — 100 €/an';
  String get active => en
      ? 'active'
      : de
      ? 'aktiv'
      : 'actif';
  String get paused => en
      ? 'paused'
      : de
      ? 'pausiert'
      : 'en pause';
  String get pause => en
      ? 'Pause member'
      : de
      ? 'Mitglied pausieren'
      : 'Mettre en pause';
  String get reactivate => en
      ? 'Reactivate member'
      : de
      ? 'Mitglied reaktivieren'
      : 'Réactiver';
  String get pauseTitle => en
      ? 'Pause this member?'
      : de
      ? 'Dieses Mitglied pausieren?'
      : 'Mettre ce membre en pause ?';
  String get reactivateTitle => en
      ? 'Reactivate this member?'
      : de
      ? 'Dieses Mitglied reaktivieren?'
      : 'Réactiver ce membre ?';
  String statusConfirm(String name, String status) => en
      ? 'Confirm the $status status for $name.'
      : de
      ? 'Status "$status" für $name bestätigen.'
      : 'Confirmez le statut "$status" pour $name.';
  String get cancel => en
      ? 'Cancel'
      : de
      ? 'Abbrechen'
      : 'Annuler';
  String get confirm => en
      ? 'Confirm'
      : de
      ? 'Bestätigen'
      : 'Confirmer';
  String get statusSaved => en
      ? 'Member status updated.'
      : de
      ? 'Mitgliedsstatus aktualisiert.'
      : 'Statut du membre mis à jour.';
  String get operationFailed => en
      ? 'Operation failed.'
      : de
      ? 'Vorgang fehlgeschlagen.'
      : 'L’opération a échoué.';
  String get memberCreated => en
      ? 'Member created.'
      : de
      ? 'Mitglied erstellt.'
      : 'Membre créé.';
  String get codePreview => en
      ? 'The member code and sign-in email are generated securely by the server.'
      : de
      ? 'Mitgliedscode und Anmelde-E-Mail werden sicher vom Server erstellt.'
      : 'Le code membre et l’e-mail de connexion sont générés de manière sécurisée par le serveur.';
  String get firstName => en
      ? 'First name'
      : de
      ? 'Vorname'
      : 'Prénom';
  String get lastName => en
      ? 'Last name'
      : de
      ? 'Nachname'
      : 'Nom de famille';
  String get displayName => en
      ? 'Display name'
      : de
      ? 'Anzeigename'
      : 'Nom d’affichage';
  String get street => en
      ? 'Street'
      : de
      ? 'Straße'
      : 'Rue';
  String get house => en
      ? 'House number'
      : de
      ? 'Hausnummer'
      : 'Numéro';
  String get postal => en
      ? 'Postal code'
      : de
      ? 'Postleitzahl'
      : 'Code postal';
  String get city => en
      ? 'City'
      : de
      ? 'Stadt'
      : 'Ville';
  String get country => en
      ? 'Country'
      : de
      ? 'Land'
      : 'Pays';
  String get phone => en
      ? 'Phone (optional)'
      : de
      ? 'Telefon (optional)'
      : 'Téléphone (facultatif)';
  String get contribution => en
      ? 'Annual contribution'
      : de
      ? 'Jahresbeitrag'
      : 'Cotisation annuelle';
  String get directAccess => en
      ? 'Create immediate access'
      : de
      ? 'Sofortzugang erstellen'
      : 'Créer un accès immédiat';
  String get directAccessHelp => en
      ? 'The member must replace the temporary password at first sign-in.'
      : de
      ? 'Das temporäre Passwort muss mindestens 8 Zeichen enthalten.'
      : 'Le membre devra remplacer le mot de passe provisoire à sa première connexion.';
  String get login => en
      ? 'Login identifier (optional)'
      : de
      ? 'Anmeldekennung (optional)'
      : 'Identifiant de connexion (facultatif)';
  String get temporaryPassword => en
      ? 'Temporary password'
      : de
      ? 'Temporäres Passwort'
      : 'Mot de passe provisoire';
  String get create => en
      ? 'Create member'
      : de
      ? 'Mitglied erstellen'
      : 'Créer le membre';
  String get required => en
      ? 'Required field'
      : de
      ? 'Pflichtfeld'
      : 'Champ obligatoire';
  String get passwordIssue => en
      ? 'The temporary password must contain at least 8 characters.'
      : de
      ? 'Das temporäre Passwort muss mindestens 8 Zeichen enthalten.'
      : 'Le mot de passe provisoire doit contenir au moins 8 caractères.';
}
