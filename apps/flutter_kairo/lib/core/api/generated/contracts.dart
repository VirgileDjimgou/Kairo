// AUTO-GENERATED from docs/api/openapi.json — do not edit by hand.
// Regenerate with: node scripts/generate-client-contracts.mjs
// dart format off

// ignore_for_file: prefer_const_constructors, sort_constructors_first, always_use_package_imports, non_constant_identifier_names, camel_case_types

class AcceptInviteRequest {
  const AcceptInviteRequest({this.display_name, this.password, this.token});

  factory AcceptInviteRequest.fromJson(Map<String, dynamic> json) => AcceptInviteRequest(
        display_name: json['display_name'] as String?,
        password: json['password'] as String?,
        token: json['token'] as String?,
      );

  final String? display_name;
  final String? password;
  final String? token;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (display_name != null) 'display_name': display_name,
        if (password != null) 'password': password,
        if (token != null) 'token': token,
      };
}

class AcceptInviteResponse {
  const AcceptInviteResponse({this.access_token, this.expires_in, this.tenant_id, this.token_type, this.user_id});

  factory AcceptInviteResponse.fromJson(Map<String, dynamic> json) => AcceptInviteResponse(
        access_token: json['access_token'] as String?,
        expires_in: json['expires_in'] as int?,
        tenant_id: json['tenant_id'] as String?,
        token_type: json['token_type'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? access_token;
  final int? expires_in;
  final String? tenant_id;
  final String? token_type;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_token != null) 'access_token': access_token,
        if (expires_in != null) 'expires_in': expires_in,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (token_type != null) 'token_type': token_type,
        if (user_id != null) 'user_id': user_id,
      };
}

class ActiveSessionResponse {
  const ActiveSessionResponse({this.created_at, this.created_ip, this.created_user_agent, this.current, this.current_tenant_id, this.id, this.last_seen_at, this.last_seen_ip, this.last_seen_user_agent});

  factory ActiveSessionResponse.fromJson(Map<String, dynamic> json) => ActiveSessionResponse(
        created_at: json['created_at'] as String?,
        created_ip: json['created_ip'] as String?,
        created_user_agent: json['created_user_agent'] as String?,
        current: json['current'] as bool?,
        current_tenant_id: json['current_tenant_id'] as String?,
        id: json['id'] as String?,
        last_seen_at: json['last_seen_at'] as String?,
        last_seen_ip: json['last_seen_ip'] as String?,
        last_seen_user_agent: json['last_seen_user_agent'] as String?,
      );

  final String? created_at;
  final String? created_ip;
  final String? created_user_agent;
  final bool? current;
  final String? current_tenant_id;
  final String? id;
  final String? last_seen_at;
  final String? last_seen_ip;
  final String? last_seen_user_agent;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (created_at != null) 'created_at': created_at,
        if (created_ip != null) 'created_ip': created_ip,
        if (created_user_agent != null) 'created_user_agent': created_user_agent,
        if (current != null) 'current': current,
        if (current_tenant_id != null) 'current_tenant_id': current_tenant_id,
        if (id != null) 'id': id,
        if (last_seen_at != null) 'last_seen_at': last_seen_at,
        if (last_seen_ip != null) 'last_seen_ip': last_seen_ip,
        if (last_seen_user_agent != null) 'last_seen_user_agent': last_seen_user_agent,
      };
}

class AnnouncementCreate {
  const AnnouncementCreate({this.body, this.expires_at, this.published_at, this.title, this.visibility_scope});

  factory AnnouncementCreate.fromJson(Map<String, dynamic> json) => AnnouncementCreate(
        body: json['body'] as String?,
        expires_at: json['expires_at'] as String?,
        published_at: json['published_at'] as String?,
        title: json['title'] as String?,
        visibility_scope: json['visibility_scope'] as String?,
      );

  final String? body;
  final String? expires_at;
  final String? published_at;
  final String? title;
  final AnnouncementVisibility? visibility_scope;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (body != null) 'body': body,
        if (expires_at != null) 'expires_at': expires_at,
        if (published_at != null) 'published_at': published_at,
        if (title != null) 'title': title,
        if (visibility_scope != null) 'visibility_scope': visibility_scope,
      };
}

class AnnouncementResponse {
  const AnnouncementResponse({this.body, this.created_at, this.created_by, this.expires_at, this.id, this.published_at, this.tenant_id, this.title, this.updated_at, this.visibility_scope});

  factory AnnouncementResponse.fromJson(Map<String, dynamic> json) => AnnouncementResponse(
        body: json['body'] as String?,
        created_at: json['created_at'] as String?,
        created_by: json['created_by'] as String?,
        expires_at: json['expires_at'] as String?,
        id: json['id'] as String?,
        published_at: json['published_at'] as String?,
        tenant_id: json['tenant_id'] as String?,
        title: json['title'] as String?,
        updated_at: json['updated_at'] as String?,
        visibility_scope: json['visibility_scope'] as String?,
      );

  final String? body;
  final String? created_at;
  final String? created_by;
  final String? expires_at;
  final String? id;
  final String? published_at;
  final String? tenant_id;
  final String? title;
  final String? updated_at;
  final String? visibility_scope;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (body != null) 'body': body,
        if (created_at != null) 'created_at': created_at,
        if (created_by != null) 'created_by': created_by,
        if (expires_at != null) 'expires_at': expires_at,
        if (id != null) 'id': id,
        if (published_at != null) 'published_at': published_at,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (title != null) 'title': title,
        if (updated_at != null) 'updated_at': updated_at,
        if (visibility_scope != null) 'visibility_scope': visibility_scope,
      };
}

class AnnouncementUpdate {
  const AnnouncementUpdate({this.body, this.expires_at, this.published_at, this.title, this.visibility_scope});

  factory AnnouncementUpdate.fromJson(Map<String, dynamic> json) => AnnouncementUpdate(
        body: json['body'] as String?,
        expires_at: json['expires_at'] as String?,
        published_at: json['published_at'] as String?,
        title: json['title'] as String?,
        visibility_scope: json['visibility_scope'] as String?,
      );

  final String? body;
  final String? expires_at;
  final String? published_at;
  final String? title;
  final AnnouncementVisibility? visibility_scope;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (body != null) 'body': body,
        if (expires_at != null) 'expires_at': expires_at,
        if (published_at != null) 'published_at': published_at,
        if (title != null) 'title': title,
        if (visibility_scope != null) 'visibility_scope': visibility_scope,
      };
}

typedef AnnouncementVisibility = String;

class AnnualBudgetResponse {
  const AnnualBudgetResponse({this.available_balance, this.currency, this.expense_total, this.expenses_by_category, this.income_by_category, this.income_total, this.recent_expenses, this.year});

  factory AnnualBudgetResponse.fromJson(Map<String, dynamic> json) => AnnualBudgetResponse(
        available_balance: json['available_balance'] as String?,
        currency: json['currency'] as String?,
        expense_total: json['expense_total'] as String?,
        expenses_by_category: (json['expenses_by_category'] as List<dynamic>?)?.map((dynamic item) => BudgetCategoryTotal.fromJson(item as Map<String, dynamic>)).toList(),
        income_by_category: (json['income_by_category'] as List<dynamic>?)?.map((dynamic item) => BudgetCategoryTotal.fromJson(item as Map<String, dynamic>)).toList(),
        income_total: json['income_total'] as String?,
        recent_expenses: (json['recent_expenses'] as List<dynamic>?)?.map((dynamic item) => ExpenseRecordResponse.fromJson(item as Map<String, dynamic>)).toList(),
        year: json['year'] as int?,
      );

  final String? available_balance;
  final String? currency;
  final String? expense_total;
  final List<BudgetCategoryTotal>? expenses_by_category;
  final List<BudgetCategoryTotal>? income_by_category;
  final String? income_total;
  final List<ExpenseRecordResponse>? recent_expenses;
  final int? year;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (available_balance != null) 'available_balance': available_balance,
        if (currency != null) 'currency': currency,
        if (expense_total != null) 'expense_total': expense_total,
        if (expenses_by_category != null) 'expenses_by_category': expenses_by_category!.map((item) => item.toJson()).toList(),
        if (income_by_category != null) 'income_by_category': income_by_category!.map((item) => item.toJson()).toList(),
        if (income_total != null) 'income_total': income_total,
        if (recent_expenses != null) 'recent_expenses': recent_expenses!.map((item) => item.toJson()).toList(),
        if (year != null) 'year': year,
      };
}

class AssistedAccessRecoveryRequest {
  const AssistedAccessRecoveryRequest({this.reason});

  factory AssistedAccessRecoveryRequest.fromJson(Map<String, dynamic> json) => AssistedAccessRecoveryRequest(
        reason: json['reason'] as String?,
      );

  final String? reason;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (reason != null) 'reason': reason,
      };
}

class AssistedAccessRecoveryResponse {
  const AssistedAccessRecoveryResponse({this.expires_at, this.message, this.revoked_session_count, this.target_display_name, this.target_user_id, this.temporary_password});

  factory AssistedAccessRecoveryResponse.fromJson(Map<String, dynamic> json) => AssistedAccessRecoveryResponse(
        expires_at: json['expires_at'] as String?,
        message: json['message'] as String?,
        revoked_session_count: json['revoked_session_count'] as int?,
        target_display_name: json['target_display_name'] as String?,
        target_user_id: json['target_user_id'] as String?,
        temporary_password: json['temporary_password'] as String?,
      );

  final String? expires_at;
  final String? message;
  final int? revoked_session_count;
  final String? target_display_name;
  final String? target_user_id;
  final String? temporary_password;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (expires_at != null) 'expires_at': expires_at,
        if (message != null) 'message': message,
        if (revoked_session_count != null) 'revoked_session_count': revoked_session_count,
        if (target_display_name != null) 'target_display_name': target_display_name,
        if (target_user_id != null) 'target_user_id': target_user_id,
        if (temporary_password != null) 'temporary_password': temporary_password,
      };
}

class AttentionItem {
  const AttentionItem({this.category, this.count, this.id, this.priority, this.target_path, this.title_key});

  factory AttentionItem.fromJson(Map<String, dynamic> json) => AttentionItem(
        category: json['category'] as String?,
        count: json['count'] as int?,
        id: json['id'] as String?,
        priority: json['priority'] as String?,
        target_path: json['target_path'] as String?,
        title_key: json['title_key'] as String?,
      );

  final String? category;
  final int? count;
  final String? id;
  final String? priority;
  final String? target_path;
  final String? title_key;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (category != null) 'category': category,
        if (count != null) 'count': count,
        if (id != null) 'id': id,
        if (priority != null) 'priority': priority,
        if (target_path != null) 'target_path': target_path,
        if (title_key != null) 'title_key': title_key,
      };
}

class AttentionOverview {
  const AttentionOverview({this.items});

  factory AttentionOverview.fromJson(Map<String, dynamic> json) => AttentionOverview(
        items: (json['items'] as List<dynamic>?)?.map((dynamic item) => AttentionItem.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final List<AttentionItem>? items;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (items != null) 'items': items!.map((item) => item.toJson()).toList(),
      };
}

class AuditActorSummary {
  const AuditActorSummary({this.display_name, this.email, this.roles});

  factory AuditActorSummary.fromJson(Map<String, dynamic> json) => AuditActorSummary(
        display_name: json['display_name'] as String?,
        email: json['email'] as String?,
        roles: (json['roles'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
      );

  final String? display_name;
  final String? email;
  final List<String>? roles;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (display_name != null) 'display_name': display_name,
        if (email != null) 'email': email,
        if (roles != null) 'roles': roles,
      };
}

class AuditEventResponse {
  const AuditEventResponse({this.action, this.actor, this.actor_user_id, this.created_at, this.details, this.entity_id, this.entity_type, this.id, this.module_key, this.tenant_id});

  factory AuditEventResponse.fromJson(Map<String, dynamic> json) => AuditEventResponse(
        action: json['action'] as String?,
        actor: json['actor'] == null ? null : AuditActorSummary.fromJson(json['actor'] as Map<String, dynamic>),
        actor_user_id: json['actor_user_id'] as String?,
        created_at: json['created_at'] as String?,
        details: json['details'] as Map<String, dynamic>?,
        entity_id: json['entity_id'] as String?,
        entity_type: json['entity_type'] as String?,
        id: json['id'] as String?,
        module_key: json['module_key'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final String? action;
  final AuditActorSummary? actor;
  final String? actor_user_id;
  final String? created_at;
  final Map<String, dynamic>? details;
  final String? entity_id;
  final String? entity_type;
  final String? id;
  final String? module_key;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (action != null) 'action': action,
        if (actor != null) 'actor': actor!.toJson(),
        if (actor_user_id != null) 'actor_user_id': actor_user_id,
        if (created_at != null) 'created_at': created_at,
        if (details != null) 'details': details,
        if (entity_id != null) 'entity_id': entity_id,
        if (entity_type != null) 'entity_type': entity_type,
        if (id != null) 'id': id,
        if (module_key != null) 'module_key': module_key,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class BackupOverviewResponse {
  const BackupOverviewResponse({this.automatic_enabled, this.external_storage_configured, this.last_restore_drill_at, this.last_successful_backup_at, this.point_in_time_recovery_enabled, this.retention_days, this.runs});

  factory BackupOverviewResponse.fromJson(Map<String, dynamic> json) => BackupOverviewResponse(
        automatic_enabled: json['automatic_enabled'] as bool?,
        external_storage_configured: json['external_storage_configured'] as bool?,
        last_restore_drill_at: json['last_restore_drill_at'] as String?,
        last_successful_backup_at: json['last_successful_backup_at'] as String?,
        point_in_time_recovery_enabled: json['point_in_time_recovery_enabled'] as bool?,
        retention_days: json['retention_days'] as int?,
        runs: (json['runs'] as List<dynamic>?)?.map((dynamic item) => BackupRunResponse.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final bool? automatic_enabled;
  final bool? external_storage_configured;
  final String? last_restore_drill_at;
  final String? last_successful_backup_at;
  final bool? point_in_time_recovery_enabled;
  final int? retention_days;
  final List<BackupRunResponse>? runs;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (automatic_enabled != null) 'automatic_enabled': automatic_enabled,
        if (external_storage_configured != null) 'external_storage_configured': external_storage_configured,
        if (last_restore_drill_at != null) 'last_restore_drill_at': last_restore_drill_at,
        if (last_successful_backup_at != null) 'last_successful_backup_at': last_successful_backup_at,
        if (point_in_time_recovery_enabled != null) 'point_in_time_recovery_enabled': point_in_time_recovery_enabled,
        if (retention_days != null) 'retention_days': retention_days,
        if (runs != null) 'runs': runs!.map((item) => item.toJson()).toList(),
      };
}

class BackupRequest {
  const BackupRequest({this.reason});

  factory BackupRequest.fromJson(Map<String, dynamic> json) => BackupRequest(
        reason: json['reason'] as String?,
      );

  final String? reason;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (reason != null) 'reason': reason,
      };
}

class BackupRunResponse {
  const BackupRunResponse({this.archive_sha256, this.archive_size_bytes, this.completed_at, this.components, this.error_code, this.id, this.manifest_sha256, this.requested_at, this.started_at, this.status, this.storage_reference, this.tenant_id, this.trigger, this.verified_at});

  factory BackupRunResponse.fromJson(Map<String, dynamic> json) => BackupRunResponse(
        archive_sha256: json['archive_sha256'] as String?,
        archive_size_bytes: json['archive_size_bytes'] as int?,
        completed_at: json['completed_at'] as String?,
        components: json['components'] as Map<String, dynamic>?,
        error_code: json['error_code'] as String?,
        id: json['id'] as String?,
        manifest_sha256: json['manifest_sha256'] as String?,
        requested_at: json['requested_at'] as String?,
        started_at: json['started_at'] as String?,
        status: json['status'] as String?,
        storage_reference: json['storage_reference'] as String?,
        tenant_id: json['tenant_id'] as String?,
        trigger: json['trigger'] as String?,
        verified_at: json['verified_at'] as String?,
      );

  final String? archive_sha256;
  final int? archive_size_bytes;
  final String? completed_at;
  final Map<String, dynamic>? components;
  final String? error_code;
  final String? id;
  final String? manifest_sha256;
  final String? requested_at;
  final String? started_at;
  final String? status;
  final String? storage_reference;
  final String? tenant_id;
  final String? trigger;
  final String? verified_at;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (archive_sha256 != null) 'archive_sha256': archive_sha256,
        if (archive_size_bytes != null) 'archive_size_bytes': archive_size_bytes,
        if (completed_at != null) 'completed_at': completed_at,
        if (components != null) 'components': components,
        if (error_code != null) 'error_code': error_code,
        if (id != null) 'id': id,
        if (manifest_sha256 != null) 'manifest_sha256': manifest_sha256,
        if (requested_at != null) 'requested_at': requested_at,
        if (started_at != null) 'started_at': started_at,
        if (status != null) 'status': status,
        if (storage_reference != null) 'storage_reference': storage_reference,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (trigger != null) 'trigger': trigger,
        if (verified_at != null) 'verified_at': verified_at,
      };
}

class Body_bulk_upload_documents_api_v1_documents_bulk_upload_post {
  const Body_bulk_upload_documents_api_v1_documents_bulk_upload_post({this.access_scope, this.allowed_role_ids, this.description, this.files, this.title_prefix});

  factory Body_bulk_upload_documents_api_v1_documents_bulk_upload_post.fromJson(Map<String, dynamic> json) => Body_bulk_upload_documents_api_v1_documents_bulk_upload_post(
        access_scope: json['access_scope'] as String?,
        allowed_role_ids: (json['allowed_role_ids'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        description: json['description'] as String?,
        files: (json['files'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        title_prefix: json['title_prefix'] as String?,
      );

  final String? access_scope;
  final List<String>? allowed_role_ids;
  final String? description;
  final List<String>? files;
  final String? title_prefix;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_scope != null) 'access_scope': access_scope,
        if (allowed_role_ids != null) 'allowed_role_ids': allowed_role_ids,
        if (description != null) 'description': description,
        if (files != null) 'files': files,
        if (title_prefix != null) 'title_prefix': title_prefix,
      };
}

class Body_import_backup_api_v1_recovery_backups_import_post {
  const Body_import_backup_api_v1_recovery_backups_import_post({this.archive, this.manifest});

  factory Body_import_backup_api_v1_recovery_backups_import_post.fromJson(Map<String, dynamic> json) => Body_import_backup_api_v1_recovery_backups_import_post(
        archive: json['archive'] as String?,
        manifest: json['manifest'] as String?,
      );

  final String? archive;
  final String? manifest;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (archive != null) 'archive': archive,
        if (manifest != null) 'manifest': manifest,
      };
}

class Body_import_contributions_api_v1_contributions_import_post {
  const Body_import_contributions_api_v1_contributions_import_post({this.file});

  factory Body_import_contributions_api_v1_contributions_import_post.fromJson(Map<String, dynamic> json) => Body_import_contributions_api_v1_contributions_import_post(
        file: json['file'] as String?,
      );

  final String? file;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (file != null) 'file': file,
      };
}

class Body_import_members_api_v1_memberships_import_post {
  const Body_import_members_api_v1_memberships_import_post({this.file});

  factory Body_import_members_api_v1_memberships_import_post.fromJson(Map<String, dynamic> json) => Body_import_members_api_v1_memberships_import_post(
        file: json['file'] as String?,
      );

  final String? file;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (file != null) 'file': file,
      };
}

class Body_upload_document_api_v1_documents_upload_post {
  const Body_upload_document_api_v1_documents_upload_post({this.access_scope, this.allowed_role_ids, this.description, this.file, this.title});

  factory Body_upload_document_api_v1_documents_upload_post.fromJson(Map<String, dynamic> json) => Body_upload_document_api_v1_documents_upload_post(
        access_scope: json['access_scope'] as String?,
        allowed_role_ids: (json['allowed_role_ids'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        description: json['description'] as String?,
        file: json['file'] as String?,
        title: json['title'] as String?,
      );

  final String? access_scope;
  final List<String>? allowed_role_ids;
  final String? description;
  final String? file;
  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_scope != null) 'access_scope': access_scope,
        if (allowed_role_ids != null) 'allowed_role_ids': allowed_role_ids,
        if (description != null) 'description': description,
        if (file != null) 'file': file,
        if (title != null) 'title': title,
      };
}

class BudgetCategoryTotal {
  const BudgetCategoryTotal({this.amount, this.category});

  factory BudgetCategoryTotal.fromJson(Map<String, dynamic> json) => BudgetCategoryTotal(
        amount: json['amount'] as String?,
        category: json['category'] as String?,
      );

  final String? amount;
  final String? category;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (category != null) 'category': category,
      };
}

class BulkUploadItemResponse {
  const BulkUploadItemResponse({this.document, this.error, this.file_name, this.index, this.status});

  factory BulkUploadItemResponse.fromJson(Map<String, dynamic> json) => BulkUploadItemResponse(
        document: json['document'] == null ? null : UploadDocumentResponse.fromJson(json['document'] as Map<String, dynamic>),
        error: json['error'] as String?,
        file_name: json['file_name'] as String?,
        index: json['index'] as int?,
        status: json['status'] as String?,
      );

  final UploadDocumentResponse? document;
  final String? error;
  final String? file_name;
  final int? index;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (document != null) 'document': document!.toJson(),
        if (error != null) 'error': error,
        if (file_name != null) 'file_name': file_name,
        if (index != null) 'index': index,
        if (status != null) 'status': status,
      };
}

class BulkUploadResponse {
  const BulkUploadResponse({this.failure_count, this.items, this.success_count});

  factory BulkUploadResponse.fromJson(Map<String, dynamic> json) => BulkUploadResponse(
        failure_count: json['failure_count'] as int?,
        items: (json['items'] as List<dynamic>?)?.map((dynamic item) => BulkUploadItemResponse.fromJson(item as Map<String, dynamic>)).toList(),
        success_count: json['success_count'] as int?,
      );

  final int? failure_count;
  final List<BulkUploadItemResponse>? items;
  final int? success_count;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (failure_count != null) 'failure_count': failure_count,
        if (items != null) 'items': items!.map((item) => item.toJson()).toList(),
        if (success_count != null) 'success_count': success_count,
      };
}

typedef CashHandoverStatus = String;

class ChangeInitialPasswordRequest {
  const ChangeInitialPasswordRequest({this.new_password});

  factory ChangeInitialPasswordRequest.fromJson(Map<String, dynamic> json) => ChangeInitialPasswordRequest(
        new_password: json['new_password'] as String?,
      );

  final String? new_password;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (new_password != null) 'new_password': new_password,
      };
}

class ChangeInitialPasswordResponse {
  const ChangeInitialPasswordResponse({this.message});

  factory ChangeInitialPasswordResponse.fromJson(Map<String, dynamic> json) => ChangeInitialPasswordResponse(
        message: json['message'] as String?,
      );

  final String? message;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (message != null) 'message': message,
      };
}

class ChangePasswordRequest {
  const ChangePasswordRequest({this.current_password, this.new_password});

  factory ChangePasswordRequest.fromJson(Map<String, dynamic> json) => ChangePasswordRequest(
        current_password: json['current_password'] as String?,
        new_password: json['new_password'] as String?,
      );

  final String? current_password;
  final String? new_password;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (current_password != null) 'current_password': current_password,
        if (new_password != null) 'new_password': new_password,
      };
}

class ChangePasswordResponse {
  const ChangePasswordResponse({this.message, this.revoked_session_count});

  factory ChangePasswordResponse.fromJson(Map<String, dynamic> json) => ChangePasswordResponse(
        message: json['message'] as String?,
        revoked_session_count: json['revoked_session_count'] as int?,
      );

  final String? message;
  final int? revoked_session_count;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (message != null) 'message': message,
        if (revoked_session_count != null) 'revoked_session_count': revoked_session_count,
      };
}

class ChatCitationResponse {
  const ChatCitationResponse({this.chunk_id, this.document_id, this.document_title, this.document_version_id, this.excerpt, this.score});

  factory ChatCitationResponse.fromJson(Map<String, dynamic> json) => ChatCitationResponse(
        chunk_id: json['chunk_id'] as String?,
        document_id: json['document_id'] as String?,
        document_title: json['document_title'] as String?,
        document_version_id: json['document_version_id'] as String?,
        excerpt: json['excerpt'] as String?,
        score: json['score'] as num?,
      );

  final String? chunk_id;
  final String? document_id;
  final String? document_title;
  final String? document_version_id;
  final String? excerpt;
  final num? score;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (chunk_id != null) 'chunk_id': chunk_id,
        if (document_id != null) 'document_id': document_id,
        if (document_title != null) 'document_title': document_title,
        if (document_version_id != null) 'document_version_id': document_version_id,
        if (excerpt != null) 'excerpt': excerpt,
        if (score != null) 'score': score,
      };
}

class ChatConversationCreate {
  const ChatConversationCreate({this.title});

  factory ChatConversationCreate.fromJson(Map<String, dynamic> json) => ChatConversationCreate(
        title: json['title'] as String?,
      );

  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (title != null) 'title': title,
      };
}

class ChatConversationDetailResponse {
  const ChatConversationDetailResponse({this.created_at, this.id, this.messages, this.tenant_id, this.title, this.updated_at, this.user_id});

  factory ChatConversationDetailResponse.fromJson(Map<String, dynamic> json) => ChatConversationDetailResponse(
        created_at: json['created_at'] as String?,
        id: json['id'] as String?,
        messages: (json['messages'] as List<dynamic>?)?.map((dynamic item) => ChatMessageResponse.fromJson(item as Map<String, dynamic>)).toList(),
        tenant_id: json['tenant_id'] as String?,
        title: json['title'] as String?,
        updated_at: json['updated_at'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? created_at;
  final String? id;
  final List<ChatMessageResponse>? messages;
  final String? tenant_id;
  final String? title;
  final String? updated_at;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (created_at != null) 'created_at': created_at,
        if (id != null) 'id': id,
        if (messages != null) 'messages': messages!.map((item) => item.toJson()).toList(),
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (title != null) 'title': title,
        if (updated_at != null) 'updated_at': updated_at,
        if (user_id != null) 'user_id': user_id,
      };
}

class ChatConversationResponse {
  const ChatConversationResponse({this.created_at, this.id, this.last_message_preview, this.message_count, this.tenant_id, this.title, this.updated_at, this.user_id});

  factory ChatConversationResponse.fromJson(Map<String, dynamic> json) => ChatConversationResponse(
        created_at: json['created_at'] as String?,
        id: json['id'] as String?,
        last_message_preview: json['last_message_preview'] as String?,
        message_count: json['message_count'] as int?,
        tenant_id: json['tenant_id'] as String?,
        title: json['title'] as String?,
        updated_at: json['updated_at'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? created_at;
  final String? id;
  final String? last_message_preview;
  final int? message_count;
  final String? tenant_id;
  final String? title;
  final String? updated_at;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (created_at != null) 'created_at': created_at,
        if (id != null) 'id': id,
        if (last_message_preview != null) 'last_message_preview': last_message_preview,
        if (message_count != null) 'message_count': message_count,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (title != null) 'title': title,
        if (updated_at != null) 'updated_at': updated_at,
        if (user_id != null) 'user_id': user_id,
      };
}

class ChatConversationUpdate {
  const ChatConversationUpdate({this.title});

  factory ChatConversationUpdate.fromJson(Map<String, dynamic> json) => ChatConversationUpdate(
        title: json['title'] as String?,
      );

  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (title != null) 'title': title,
      };
}

class ChatDomainPolicyResponse {
  const ChatDomainPolicyResponse({this.allowed_domains});

  factory ChatDomainPolicyResponse.fromJson(Map<String, dynamic> json) => ChatDomainPolicyResponse(
        allowed_domains: (json['allowed_domains'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
      );

  final List<String>? allowed_domains;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (allowed_domains != null) 'allowed_domains': allowed_domains,
      };
}

class ChatMessageResponse {
  const ChatMessageResponse({this.citations_json, this.content, this.created_at, this.id, this.role});

  factory ChatMessageResponse.fromJson(Map<String, dynamic> json) => ChatMessageResponse(
        citations_json: (json['citations_json'] as List<dynamic>?)?.map((dynamic item) => item as Map<String, dynamic>).toList(),
        content: json['content'] as String?,
        created_at: json['created_at'] as String?,
        id: json['id'] as String?,
        role: json['role'] as String?,
      );

  final List<Map<String, dynamic>>? citations_json;
  final String? content;
  final String? created_at;
  final String? id;
  final String? role;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (citations_json != null) 'citations_json': citations_json,
        if (content != null) 'content': content,
        if (created_at != null) 'created_at': created_at,
        if (id != null) 'id': id,
        if (role != null) 'role': role,
      };
}

class ChatQueryLogResponse {
  const ChatQueryLogResponse({this.answer_preview, this.citation_count, this.confidence, this.created_at, this.id, this.question_preview, this.refusal_reason_preview, this.refused, this.source_types, this.tenant_id, this.user_id});

  factory ChatQueryLogResponse.fromJson(Map<String, dynamic> json) => ChatQueryLogResponse(
        answer_preview: json['answer_preview'] as String?,
        citation_count: json['citation_count'] as int?,
        confidence: json['confidence'] as num?,
        created_at: json['created_at'] as String?,
        id: json['id'] as String?,
        question_preview: json['question_preview'] as String?,
        refusal_reason_preview: json['refusal_reason_preview'] as String?,
        refused: json['refused'] as bool?,
        source_types: (json['source_types'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        tenant_id: json['tenant_id'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? answer_preview;
  final int? citation_count;
  final num? confidence;
  final String? created_at;
  final String? id;
  final String? question_preview;
  final String? refusal_reason_preview;
  final bool? refused;
  final List<String>? source_types;
  final String? tenant_id;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (answer_preview != null) 'answer_preview': answer_preview,
        if (citation_count != null) 'citation_count': citation_count,
        if (confidence != null) 'confidence': confidence,
        if (created_at != null) 'created_at': created_at,
        if (id != null) 'id': id,
        if (question_preview != null) 'question_preview': question_preview,
        if (refusal_reason_preview != null) 'refusal_reason_preview': refusal_reason_preview,
        if (refused != null) 'refused': refused,
        if (source_types != null) 'source_types': source_types,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (user_id != null) 'user_id': user_id,
      };
}

class ChatQueryRequest {
  const ChatQueryRequest({this.conversation_id, this.question, this.response_language, this.top_k});

  factory ChatQueryRequest.fromJson(Map<String, dynamic> json) => ChatQueryRequest(
        conversation_id: json['conversation_id'] as String?,
        question: json['question'] as String?,
        response_language: json['response_language'] as String?,
        top_k: json['top_k'] as int?,
      );

  final String? conversation_id;
  final String? question;
  final String? response_language;
  final int? top_k;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (conversation_id != null) 'conversation_id': conversation_id,
        if (question != null) 'question': question,
        if (response_language != null) 'response_language': response_language,
        if (top_k != null) 'top_k': top_k,
      };
}

class ChatQueryResponse {
  const ChatQueryResponse({this.answer, this.citations, this.confidence, this.conversation_id, this.refusal_reason, this.refused, this.source_types});

  factory ChatQueryResponse.fromJson(Map<String, dynamic> json) => ChatQueryResponse(
        answer: json['answer'] as String?,
        citations: (json['citations'] as List<dynamic>?)?.map((dynamic item) => ChatCitationResponse.fromJson(item as Map<String, dynamic>)).toList(),
        confidence: json['confidence'] as num?,
        conversation_id: json['conversation_id'] as String?,
        refusal_reason: json['refusal_reason'] as String?,
        refused: json['refused'] as bool?,
        source_types: (json['source_types'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
      );

  final String? answer;
  final List<ChatCitationResponse>? citations;
  final num? confidence;
  final String? conversation_id;
  final String? refusal_reason;
  final bool? refused;
  final List<String>? source_types;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (answer != null) 'answer': answer,
        if (citations != null) 'citations': citations!.map((item) => item.toJson()).toList(),
        if (confidence != null) 'confidence': confidence,
        if (conversation_id != null) 'conversation_id': conversation_id,
        if (refusal_reason != null) 'refusal_reason': refusal_reason,
        if (refused != null) 'refused': refused,
        if (source_types != null) 'source_types': source_types,
      };
}

class ContributionReceiptDeclarationCreate {
  const ContributionReceiptDeclarationCreate({this.amount, this.currency, this.disciplinary_record_id, this.evidence_json, this.income_type, this.membership_profile_id, this.note, this.payment_method, this.received_at, this.reference, this.source_name});

  factory ContributionReceiptDeclarationCreate.fromJson(Map<String, dynamic> json) => ContributionReceiptDeclarationCreate(
        amount: json['amount'],
        currency: json['currency'] as String?,
        disciplinary_record_id: json['disciplinary_record_id'] as String?,
        evidence_json: json['evidence_json'] as String?,
        income_type: json['income_type'] as String?,
        membership_profile_id: json['membership_profile_id'] as String?,
        note: json['note'] as String?,
        payment_method: json['payment_method'] as String?,
        received_at: json['received_at'] as String?,
        reference: json['reference'] as String?,
        source_name: json['source_name'] as String?,
      );

  final dynamic amount;
  final String? currency;
  final String? disciplinary_record_id;
  final String? evidence_json;
  final FinancialIncomeType? income_type;
  final String? membership_profile_id;
  final String? note;
  final PaymentMethod? payment_method;
  final String? received_at;
  final String? reference;
  final String? source_name;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (currency != null) 'currency': currency,
        if (disciplinary_record_id != null) 'disciplinary_record_id': disciplinary_record_id,
        if (evidence_json != null) 'evidence_json': evidence_json,
        if (income_type != null) 'income_type': income_type,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (note != null) 'note': note,
        if (payment_method != null) 'payment_method': payment_method,
        if (received_at != null) 'received_at': received_at,
        if (reference != null) 'reference': reference,
        if (source_name != null) 'source_name': source_name,
      };
}

class ContributionReceiptDeclarationProcess {
  const ContributionReceiptDeclarationProcess({this.action, this.contribution_record_id, this.handover_reminder_days, this.note, this.processed_amount});

  factory ContributionReceiptDeclarationProcess.fromJson(Map<String, dynamic> json) => ContributionReceiptDeclarationProcess(
        action: json['action'] as String?,
        contribution_record_id: json['contribution_record_id'] as String?,
        handover_reminder_days: json['handover_reminder_days'] as int?,
        note: json['note'] as String?,
        processed_amount: json['processed_amount'],
      );

  final String? action;
  final String? contribution_record_id;
  final int? handover_reminder_days;
  final String? note;
  final dynamic processed_amount;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (action != null) 'action': action,
        if (contribution_record_id != null) 'contribution_record_id': contribution_record_id,
        if (handover_reminder_days != null) 'handover_reminder_days': handover_reminder_days,
        if (note != null) 'note': note,
        if (processed_amount != null) 'processed_amount': processed_amount,
      };
}

class ContributionReceiptDeclarationResponse {
  const ContributionReceiptDeclarationResponse({this.amount, this.cash_handover_status, this.contribution_record_id, this.created_at, this.currency, this.declarant_role_code, this.declarant_user_id, this.disciplinary_record_id, this.evidence_json, this.handover_due_at, this.handover_method, this.handover_reminder_days, this.handover_reminder_sent_at, this.handover_reminder_updated_at, this.handover_reported_at, this.handover_reported_by_user_id, this.id, this.income_type, this.membership_profile_id, this.note, this.payment_method, this.payment_record_id, this.processed_amount, this.processed_at, this.processed_by_user_id, this.processing_note, this.received_at, this.reference, this.source_name, this.status, this.submitted_at, this.tenant_id, this.treasury_receipt_note, this.treasury_received_at, this.treasury_received_by_user_id, this.updated_at});

  factory ContributionReceiptDeclarationResponse.fromJson(Map<String, dynamic> json) => ContributionReceiptDeclarationResponse(
        amount: json['amount'] as String?,
        cash_handover_status: json['cash_handover_status'] as String?,
        contribution_record_id: json['contribution_record_id'] as String?,
        created_at: json['created_at'] as String?,
        currency: json['currency'] as String?,
        declarant_role_code: json['declarant_role_code'] as String?,
        declarant_user_id: json['declarant_user_id'] as String?,
        disciplinary_record_id: json['disciplinary_record_id'] as String?,
        evidence_json: json['evidence_json'] as String?,
        handover_due_at: json['handover_due_at'] as String?,
        handover_method: json['handover_method'] as String?,
        handover_reminder_days: json['handover_reminder_days'] as int?,
        handover_reminder_sent_at: json['handover_reminder_sent_at'] as String?,
        handover_reminder_updated_at: json['handover_reminder_updated_at'] as String?,
        handover_reported_at: json['handover_reported_at'] as String?,
        handover_reported_by_user_id: json['handover_reported_by_user_id'] as String?,
        id: json['id'] as String?,
        income_type: json['income_type'] as String?,
        membership_profile_id: json['membership_profile_id'] as String?,
        note: json['note'] as String?,
        payment_method: json['payment_method'] as String?,
        payment_record_id: json['payment_record_id'] as String?,
        processed_amount: json['processed_amount'] as String?,
        processed_at: json['processed_at'] as String?,
        processed_by_user_id: json['processed_by_user_id'] as String?,
        processing_note: json['processing_note'] as String?,
        received_at: json['received_at'] as String?,
        reference: json['reference'] as String?,
        source_name: json['source_name'] as String?,
        status: json['status'] as String?,
        submitted_at: json['submitted_at'] as String?,
        tenant_id: json['tenant_id'] as String?,
        treasury_receipt_note: json['treasury_receipt_note'] as String?,
        treasury_received_at: json['treasury_received_at'] as String?,
        treasury_received_by_user_id: json['treasury_received_by_user_id'] as String?,
        updated_at: json['updated_at'] as String?,
      );

  final String? amount;
  final CashHandoverStatus? cash_handover_status;
  final String? contribution_record_id;
  final String? created_at;
  final String? currency;
  final String? declarant_role_code;
  final String? declarant_user_id;
  final String? disciplinary_record_id;
  final String? evidence_json;
  final String? handover_due_at;
  final String? handover_method;
  final int? handover_reminder_days;
  final String? handover_reminder_sent_at;
  final String? handover_reminder_updated_at;
  final String? handover_reported_at;
  final String? handover_reported_by_user_id;
  final String? id;
  final FinancialIncomeType? income_type;
  final String? membership_profile_id;
  final String? note;
  final String? payment_method;
  final String? payment_record_id;
  final String? processed_amount;
  final String? processed_at;
  final String? processed_by_user_id;
  final String? processing_note;
  final String? received_at;
  final String? reference;
  final String? source_name;
  final ContributionReceiptStatus? status;
  final String? submitted_at;
  final String? tenant_id;
  final String? treasury_receipt_note;
  final String? treasury_received_at;
  final String? treasury_received_by_user_id;
  final String? updated_at;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (cash_handover_status != null) 'cash_handover_status': cash_handover_status,
        if (contribution_record_id != null) 'contribution_record_id': contribution_record_id,
        if (created_at != null) 'created_at': created_at,
        if (currency != null) 'currency': currency,
        if (declarant_role_code != null) 'declarant_role_code': declarant_role_code,
        if (declarant_user_id != null) 'declarant_user_id': declarant_user_id,
        if (disciplinary_record_id != null) 'disciplinary_record_id': disciplinary_record_id,
        if (evidence_json != null) 'evidence_json': evidence_json,
        if (handover_due_at != null) 'handover_due_at': handover_due_at,
        if (handover_method != null) 'handover_method': handover_method,
        if (handover_reminder_days != null) 'handover_reminder_days': handover_reminder_days,
        if (handover_reminder_sent_at != null) 'handover_reminder_sent_at': handover_reminder_sent_at,
        if (handover_reminder_updated_at != null) 'handover_reminder_updated_at': handover_reminder_updated_at,
        if (handover_reported_at != null) 'handover_reported_at': handover_reported_at,
        if (handover_reported_by_user_id != null) 'handover_reported_by_user_id': handover_reported_by_user_id,
        if (id != null) 'id': id,
        if (income_type != null) 'income_type': income_type,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (note != null) 'note': note,
        if (payment_method != null) 'payment_method': payment_method,
        if (payment_record_id != null) 'payment_record_id': payment_record_id,
        if (processed_amount != null) 'processed_amount': processed_amount,
        if (processed_at != null) 'processed_at': processed_at,
        if (processed_by_user_id != null) 'processed_by_user_id': processed_by_user_id,
        if (processing_note != null) 'processing_note': processing_note,
        if (received_at != null) 'received_at': received_at,
        if (reference != null) 'reference': reference,
        if (source_name != null) 'source_name': source_name,
        if (status != null) 'status': status,
        if (submitted_at != null) 'submitted_at': submitted_at,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (treasury_receipt_note != null) 'treasury_receipt_note': treasury_receipt_note,
        if (treasury_received_at != null) 'treasury_received_at': treasury_received_at,
        if (treasury_received_by_user_id != null) 'treasury_received_by_user_id': treasury_received_by_user_id,
        if (updated_at != null) 'updated_at': updated_at,
      };
}

class ContributionReceiptDeclarationUpdate {
  const ContributionReceiptDeclarationUpdate({this.amount, this.currency, this.evidence_json, this.income_type, this.membership_profile_id, this.note, this.payment_method, this.received_at, this.reference, this.source_name});

  factory ContributionReceiptDeclarationUpdate.fromJson(Map<String, dynamic> json) => ContributionReceiptDeclarationUpdate(
        amount: json['amount'],
        currency: json['currency'] as String?,
        evidence_json: json['evidence_json'] as String?,
        income_type: json['income_type'] as String?,
        membership_profile_id: json['membership_profile_id'] as String?,
        note: json['note'] as String?,
        payment_method: json['payment_method'] as String?,
        received_at: json['received_at'] as String?,
        reference: json['reference'] as String?,
        source_name: json['source_name'] as String?,
      );

  final dynamic amount;
  final String? currency;
  final String? evidence_json;
  final FinancialIncomeType? income_type;
  final String? membership_profile_id;
  final String? note;
  final PaymentMethod? payment_method;
  final String? received_at;
  final String? reference;
  final String? source_name;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (currency != null) 'currency': currency,
        if (evidence_json != null) 'evidence_json': evidence_json,
        if (income_type != null) 'income_type': income_type,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (note != null) 'note': note,
        if (payment_method != null) 'payment_method': payment_method,
        if (received_at != null) 'received_at': received_at,
        if (reference != null) 'reference': reference,
        if (source_name != null) 'source_name': source_name,
      };
}

class ContributionReceiptHandoverReminderUpdate {
  const ContributionReceiptHandoverReminderUpdate({this.reminder_days});

  factory ContributionReceiptHandoverReminderUpdate.fromJson(Map<String, dynamic> json) => ContributionReceiptHandoverReminderUpdate(
        reminder_days: json['reminder_days'] as int?,
      );

  final int? reminder_days;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (reminder_days != null) 'reminder_days': reminder_days,
      };
}

class ContributionReceiptHandoverReport {
  const ContributionReceiptHandoverReport({this.method, this.note});

  factory ContributionReceiptHandoverReport.fromJson(Map<String, dynamic> json) => ContributionReceiptHandoverReport(
        method: json['method'] as String?,
        note: json['note'] as String?,
      );

  final String? method;
  final String? note;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (method != null) 'method': method,
        if (note != null) 'note': note,
      };
}

class ContributionReceiptMemberOption {
  const ContributionReceiptMemberOption({this.display_name, this.email, this.first_name, this.id, this.joined_at, this.last_name, this.member_code, this.membership_type, this.phone, this.status});

  factory ContributionReceiptMemberOption.fromJson(Map<String, dynamic> json) => ContributionReceiptMemberOption(
        display_name: json['display_name'] as String?,
        email: json['email'] as String?,
        first_name: json['first_name'] as String?,
        id: json['id'] as String?,
        joined_at: json['joined_at'] as String?,
        last_name: json['last_name'] as String?,
        member_code: json['member_code'] as String?,
        membership_type: json['membership_type'] as String?,
        phone: json['phone'] as String?,
        status: json['status'] as String?,
      );

  final String? display_name;
  final String? email;
  final String? first_name;
  final String? id;
  final String? joined_at;
  final String? last_name;
  final String? member_code;
  final String? membership_type;
  final String? phone;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (display_name != null) 'display_name': display_name,
        if (email != null) 'email': email,
        if (first_name != null) 'first_name': first_name,
        if (id != null) 'id': id,
        if (joined_at != null) 'joined_at': joined_at,
        if (last_name != null) 'last_name': last_name,
        if (member_code != null) 'member_code': member_code,
        if (membership_type != null) 'membership_type': membership_type,
        if (phone != null) 'phone': phone,
        if (status != null) 'status': status,
      };
}

typedef ContributionReceiptStatus = String;

class ContributionReceiptTreasuryConfirmation {
  const ContributionReceiptTreasuryConfirmation({this.method, this.note});

  factory ContributionReceiptTreasuryConfirmation.fromJson(Map<String, dynamic> json) => ContributionReceiptTreasuryConfirmation(
        method: json['method'] as String?,
        note: json['note'] as String?,
      );

  final String? method;
  final String? note;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (method != null) 'method': method,
        if (note != null) 'note': note,
      };
}

class ContributionRecordCreate {
  const ContributionRecordCreate({this.currency, this.due_date, this.expected_amount, this.membership_profile_id, this.paid_amount, this.status, this.year});

  factory ContributionRecordCreate.fromJson(Map<String, dynamic> json) => ContributionRecordCreate(
        currency: json['currency'] as String?,
        due_date: json['due_date'] as String?,
        expected_amount: json['expected_amount'],
        membership_profile_id: json['membership_profile_id'] as String?,
        paid_amount: json['paid_amount'],
        status: json['status'] as String?,
        year: json['year'] as int?,
      );

  final String? currency;
  final String? due_date;
  final dynamic expected_amount;
  final String? membership_profile_id;
  final dynamic paid_amount;
  final ContributionStatus? status;
  final int? year;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (currency != null) 'currency': currency,
        if (due_date != null) 'due_date': due_date,
        if (expected_amount != null) 'expected_amount': expected_amount,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (paid_amount != null) 'paid_amount': paid_amount,
        if (status != null) 'status': status,
        if (year != null) 'year': year,
      };
}

class ContributionRecordResponse {
  const ContributionRecordResponse({this.balance, this.created_at, this.currency, this.due_date, this.expected_amount, this.id, this.membership_profile_id, this.paid_amount, this.status, this.tenant_id, this.updated_at, this.year});

  factory ContributionRecordResponse.fromJson(Map<String, dynamic> json) => ContributionRecordResponse(
        balance: json['balance'] as String?,
        created_at: json['created_at'] as String?,
        currency: json['currency'] as String?,
        due_date: json['due_date'] as String?,
        expected_amount: json['expected_amount'] as String?,
        id: json['id'] as String?,
        membership_profile_id: json['membership_profile_id'] as String?,
        paid_amount: json['paid_amount'] as String?,
        status: json['status'] as String?,
        tenant_id: json['tenant_id'] as String?,
        updated_at: json['updated_at'] as String?,
        year: json['year'] as int?,
      );

  final String? balance;
  final String? created_at;
  final String? currency;
  final String? due_date;
  final String? expected_amount;
  final String? id;
  final String? membership_profile_id;
  final String? paid_amount;
  final String? status;
  final String? tenant_id;
  final String? updated_at;
  final int? year;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (balance != null) 'balance': balance,
        if (created_at != null) 'created_at': created_at,
        if (currency != null) 'currency': currency,
        if (due_date != null) 'due_date': due_date,
        if (expected_amount != null) 'expected_amount': expected_amount,
        if (id != null) 'id': id,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (paid_amount != null) 'paid_amount': paid_amount,
        if (status != null) 'status': status,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (updated_at != null) 'updated_at': updated_at,
        if (year != null) 'year': year,
      };
}

class ContributionRecordUpdate {
  const ContributionRecordUpdate({this.currency, this.due_date, this.expected_amount, this.paid_amount, this.status});

  factory ContributionRecordUpdate.fromJson(Map<String, dynamic> json) => ContributionRecordUpdate(
        currency: json['currency'] as String?,
        due_date: json['due_date'] as String?,
        expected_amount: json['expected_amount'],
        paid_amount: json['paid_amount'],
        status: json['status'] as String?,
      );

  final String? currency;
  final String? due_date;
  final dynamic expected_amount;
  final dynamic paid_amount;
  final ContributionStatus? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (currency != null) 'currency': currency,
        if (due_date != null) 'due_date': due_date,
        if (expected_amount != null) 'expected_amount': expected_amount,
        if (paid_amount != null) 'paid_amount': paid_amount,
        if (status != null) 'status': status,
      };
}

class ContributionReminderBatchRequest {
  const ContributionReminderBatchRequest({this.channel, this.due_scope, this.limit, this.status, this.year});

  factory ContributionReminderBatchRequest.fromJson(Map<String, dynamic> json) => ContributionReminderBatchRequest(
        channel: json['channel'] as String?,
        due_scope: json['due_scope'] as String?,
        limit: json['limit'] as int?,
        status: json['status'] as String?,
        year: json['year'] as int?,
      );

  final String? channel;
  final String? due_scope;
  final int? limit;
  final ContributionStatus? status;
  final int? year;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (due_scope != null) 'due_scope': due_scope,
        if (limit != null) 'limit': limit,
        if (status != null) 'status': status,
        if (year != null) 'year': year,
      };
}

class ContributionReminderBatchResponse {
  const ContributionReminderBatchResponse({this.attempted_count, this.reminder_count, this.reminders});

  factory ContributionReminderBatchResponse.fromJson(Map<String, dynamic> json) => ContributionReminderBatchResponse(
        attempted_count: json['attempted_count'] as int?,
        reminder_count: json['reminder_count'] as int?,
        reminders: (json['reminders'] as List<dynamic>?)?.map((dynamic item) => ContributionReminderResponse.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final int? attempted_count;
  final int? reminder_count;
  final List<ContributionReminderResponse>? reminders;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (attempted_count != null) 'attempted_count': attempted_count,
        if (reminder_count != null) 'reminder_count': reminder_count,
        if (reminders != null) 'reminders': reminders!.map((item) => item.toJson()).toList(),
      };
}

class ContributionReminderResponse {
  const ContributionReminderResponse({this.balance_snapshot, this.body, this.channel, this.contribution_record_id, this.created_at, this.delivery_status, this.due_date_snapshot, this.id, this.member_code, this.member_display_name, this.membership_profile_id, this.provider_message, this.recipient, this.reminded_by, this.sent_at, this.subject, this.tenant_id});

  factory ContributionReminderResponse.fromJson(Map<String, dynamic> json) => ContributionReminderResponse(
        balance_snapshot: json['balance_snapshot'] as String?,
        body: json['body'] as String?,
        channel: json['channel'] as String?,
        contribution_record_id: json['contribution_record_id'] as String?,
        created_at: json['created_at'] as String?,
        delivery_status: json['delivery_status'] as String?,
        due_date_snapshot: json['due_date_snapshot'] as String?,
        id: json['id'] as String?,
        member_code: json['member_code'] as String?,
        member_display_name: json['member_display_name'] as String?,
        membership_profile_id: json['membership_profile_id'] as String?,
        provider_message: json['provider_message'] as String?,
        recipient: json['recipient'] as String?,
        reminded_by: json['reminded_by'] as String?,
        sent_at: json['sent_at'] as String?,
        subject: json['subject'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final String? balance_snapshot;
  final String? body;
  final String? channel;
  final String? contribution_record_id;
  final String? created_at;
  final ReminderDeliveryStatus? delivery_status;
  final String? due_date_snapshot;
  final String? id;
  final String? member_code;
  final String? member_display_name;
  final String? membership_profile_id;
  final String? provider_message;
  final String? recipient;
  final String? reminded_by;
  final String? sent_at;
  final String? subject;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (balance_snapshot != null) 'balance_snapshot': balance_snapshot,
        if (body != null) 'body': body,
        if (channel != null) 'channel': channel,
        if (contribution_record_id != null) 'contribution_record_id': contribution_record_id,
        if (created_at != null) 'created_at': created_at,
        if (delivery_status != null) 'delivery_status': delivery_status,
        if (due_date_snapshot != null) 'due_date_snapshot': due_date_snapshot,
        if (id != null) 'id': id,
        if (member_code != null) 'member_code': member_code,
        if (member_display_name != null) 'member_display_name': member_display_name,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (provider_message != null) 'provider_message': provider_message,
        if (recipient != null) 'recipient': recipient,
        if (reminded_by != null) 'reminded_by': reminded_by,
        if (sent_at != null) 'sent_at': sent_at,
        if (subject != null) 'subject': subject,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class ContributionReminderSendRequest {
  const ContributionReminderSendRequest({this.channel});

  factory ContributionReminderSendRequest.fromJson(Map<String, dynamic> json) => ContributionReminderSendRequest(
        channel: json['channel'] as String?,
      );

  final String? channel;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
      };
}

typedef ContributionStatus = String;

class DeviceRegistrationRequest {
  const DeviceRegistrationRequest({this.browser, this.device_metadata, this.installation_id, this.platform});

  factory DeviceRegistrationRequest.fromJson(Map<String, dynamic> json) => DeviceRegistrationRequest(
        browser: json['browser'] as String?,
        device_metadata: json['device_metadata'] as Map<String, dynamic>?,
        installation_id: json['installation_id'] as String?,
        platform: json['platform'] as String?,
      );

  final String? browser;
  final Map<String, dynamic>? device_metadata;
  final String? installation_id;
  final String? platform;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (browser != null) 'browser': browser,
        if (device_metadata != null) 'device_metadata': device_metadata,
        if (installation_id != null) 'installation_id': installation_id,
        if (platform != null) 'platform': platform,
      };
}

class DisciplinaryRecordCreate {
  const DisciplinaryRecordCreate({this.amount, this.currency, this.description, this.membership_profile_id, this.policy_record_id, this.status, this.title});

  factory DisciplinaryRecordCreate.fromJson(Map<String, dynamic> json) => DisciplinaryRecordCreate(
        amount: json['amount'],
        currency: json['currency'] as String?,
        description: json['description'] as String?,
        membership_profile_id: json['membership_profile_id'] as String?,
        policy_record_id: json['policy_record_id'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
      );

  final dynamic amount;
  final String? currency;
  final String? description;
  final String? membership_profile_id;
  final String? policy_record_id;
  final DisciplinaryStatus? status;
  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (currency != null) 'currency': currency,
        if (description != null) 'description': description,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (policy_record_id != null) 'policy_record_id': policy_record_id,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
      };
}

class DisciplinaryRecordResponse {
  const DisciplinaryRecordResponse({this.amount, this.created_at, this.currency, this.description, this.id, this.membership_display_name, this.membership_profile_id, this.policy_record_id, this.policy_title, this.recorded_at, this.recorded_by, this.status, this.tenant_id, this.title, this.updated_at});

  factory DisciplinaryRecordResponse.fromJson(Map<String, dynamic> json) => DisciplinaryRecordResponse(
        amount: json['amount'] as String?,
        created_at: json['created_at'] as String?,
        currency: json['currency'] as String?,
        description: json['description'] as String?,
        id: json['id'] as String?,
        membership_display_name: json['membership_display_name'] as String?,
        membership_profile_id: json['membership_profile_id'] as String?,
        policy_record_id: json['policy_record_id'] as String?,
        policy_title: json['policy_title'] as String?,
        recorded_at: json['recorded_at'] as String?,
        recorded_by: json['recorded_by'] as String?,
        status: json['status'] as String?,
        tenant_id: json['tenant_id'] as String?,
        title: json['title'] as String?,
        updated_at: json['updated_at'] as String?,
      );

  final String? amount;
  final String? created_at;
  final String? currency;
  final String? description;
  final String? id;
  final String? membership_display_name;
  final String? membership_profile_id;
  final String? policy_record_id;
  final String? policy_title;
  final String? recorded_at;
  final String? recorded_by;
  final String? status;
  final String? tenant_id;
  final String? title;
  final String? updated_at;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (created_at != null) 'created_at': created_at,
        if (currency != null) 'currency': currency,
        if (description != null) 'description': description,
        if (id != null) 'id': id,
        if (membership_display_name != null) 'membership_display_name': membership_display_name,
        if (membership_profile_id != null) 'membership_profile_id': membership_profile_id,
        if (policy_record_id != null) 'policy_record_id': policy_record_id,
        if (policy_title != null) 'policy_title': policy_title,
        if (recorded_at != null) 'recorded_at': recorded_at,
        if (recorded_by != null) 'recorded_by': recorded_by,
        if (status != null) 'status': status,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (title != null) 'title': title,
        if (updated_at != null) 'updated_at': updated_at,
      };
}

class DisciplinaryRecordUpdate {
  const DisciplinaryRecordUpdate({this.amount, this.currency, this.description, this.policy_record_id, this.status, this.title});

  factory DisciplinaryRecordUpdate.fromJson(Map<String, dynamic> json) => DisciplinaryRecordUpdate(
        amount: json['amount'],
        currency: json['currency'] as String?,
        description: json['description'] as String?,
        policy_record_id: json['policy_record_id'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
      );

  final dynamic amount;
  final String? currency;
  final String? description;
  final String? policy_record_id;
  final DisciplinaryStatus? status;
  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (currency != null) 'currency': currency,
        if (description != null) 'description': description,
        if (policy_record_id != null) 'policy_record_id': policy_record_id,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
      };
}

typedef DisciplinaryStatus = String;

class DocumentAccessUpdateRequest {
  const DocumentAccessUpdateRequest({this.access_scope, this.allowed_role_ids});

  factory DocumentAccessUpdateRequest.fromJson(Map<String, dynamic> json) => DocumentAccessUpdateRequest(
        access_scope: json['access_scope'] as String?,
        allowed_role_ids: (json['allowed_role_ids'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
      );

  final String? access_scope;
  final List<String>? allowed_role_ids;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_scope != null) 'access_scope': access_scope,
        if (allowed_role_ids != null) 'allowed_role_ids': allowed_role_ids,
      };
}

class DocumentListItemResponse {
  const DocumentListItemResponse({this.access_scope, this.allowed_role_ids, this.created_at, this.current_version, this.description, this.id, this.language, this.owner_user_id, this.source_type, this.status, this.title});

  factory DocumentListItemResponse.fromJson(Map<String, dynamic> json) => DocumentListItemResponse(
        access_scope: json['access_scope'] as String?,
        allowed_role_ids: (json['allowed_role_ids'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        created_at: json['created_at'] as String?,
        current_version: json['current_version'] == null ? null : DocumentVersionResponse.fromJson(json['current_version'] as Map<String, dynamic>),
        description: json['description'] as String?,
        id: json['id'] as String?,
        language: json['language'] as String?,
        owner_user_id: json['owner_user_id'] as String?,
        source_type: json['source_type'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
      );

  final String? access_scope;
  final List<String>? allowed_role_ids;
  final String? created_at;
  final DocumentVersionResponse? current_version;
  final String? description;
  final String? id;
  final String? language;
  final String? owner_user_id;
  final String? source_type;
  final String? status;
  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_scope != null) 'access_scope': access_scope,
        if (allowed_role_ids != null) 'allowed_role_ids': allowed_role_ids,
        if (created_at != null) 'created_at': created_at,
        if (current_version != null) 'current_version': current_version!.toJson(),
        if (description != null) 'description': description,
        if (id != null) 'id': id,
        if (language != null) 'language': language,
        if (owner_user_id != null) 'owner_user_id': owner_user_id,
        if (source_type != null) 'source_type': source_type,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
      };
}

class DocumentVersionResponse {
  const DocumentVersionResponse({this.checksum, this.created_at, this.file_name, this.file_size_bytes, this.id, this.mime_type, this.storage_bucket, this.storage_key});

  factory DocumentVersionResponse.fromJson(Map<String, dynamic> json) => DocumentVersionResponse(
        checksum: json['checksum'] as String?,
        created_at: json['created_at'] as String?,
        file_name: json['file_name'] as String?,
        file_size_bytes: json['file_size_bytes'] as int?,
        id: json['id'] as String?,
        mime_type: json['mime_type'] as String?,
        storage_bucket: json['storage_bucket'] as String?,
        storage_key: json['storage_key'] as String?,
      );

  final String? checksum;
  final String? created_at;
  final String? file_name;
  final int? file_size_bytes;
  final String? id;
  final String? mime_type;
  final String? storage_bucket;
  final String? storage_key;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (checksum != null) 'checksum': checksum,
        if (created_at != null) 'created_at': created_at,
        if (file_name != null) 'file_name': file_name,
        if (file_size_bytes != null) 'file_size_bytes': file_size_bytes,
        if (id != null) 'id': id,
        if (mime_type != null) 'mime_type': mime_type,
        if (storage_bucket != null) 'storage_bucket': storage_bucket,
        if (storage_key != null) 'storage_key': storage_key,
      };
}

class EventCreate {
  const EventCreate({this.description, this.end_at, this.location, this.metadata_json, this.start_at, this.status, this.title, this.visibility_scope});

  factory EventCreate.fromJson(Map<String, dynamic> json) => EventCreate(
        description: json['description'] as String?,
        end_at: json['end_at'] as String?,
        location: json['location'] as String?,
        metadata_json: json['metadata_json'] as Map<String, dynamic>?,
        start_at: json['start_at'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
        visibility_scope: json['visibility_scope'] as String?,
      );

  final String? description;
  final String? end_at;
  final String? location;
  final Map<String, dynamic>? metadata_json;
  final String? start_at;
  final EventStatus? status;
  final String? title;
  final EventVisibility? visibility_scope;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (description != null) 'description': description,
        if (end_at != null) 'end_at': end_at,
        if (location != null) 'location': location,
        if (metadata_json != null) 'metadata_json': metadata_json,
        if (start_at != null) 'start_at': start_at,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
        if (visibility_scope != null) 'visibility_scope': visibility_scope,
      };
}

class EventResponse {
  const EventResponse({this.created_at, this.created_by, this.description, this.end_at, this.id, this.location, this.metadata_json, this.start_at, this.status, this.tenant_id, this.title, this.updated_at, this.visibility_scope});

  factory EventResponse.fromJson(Map<String, dynamic> json) => EventResponse(
        created_at: json['created_at'] as String?,
        created_by: json['created_by'] as String?,
        description: json['description'] as String?,
        end_at: json['end_at'] as String?,
        id: json['id'] as String?,
        location: json['location'] as String?,
        metadata_json: json['metadata_json'] as Map<String, dynamic>?,
        start_at: json['start_at'] as String?,
        status: json['status'] as String?,
        tenant_id: json['tenant_id'] as String?,
        title: json['title'] as String?,
        updated_at: json['updated_at'] as String?,
        visibility_scope: json['visibility_scope'] as String?,
      );

  final String? created_at;
  final String? created_by;
  final String? description;
  final String? end_at;
  final String? id;
  final String? location;
  final Map<String, dynamic>? metadata_json;
  final String? start_at;
  final String? status;
  final String? tenant_id;
  final String? title;
  final String? updated_at;
  final String? visibility_scope;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (created_at != null) 'created_at': created_at,
        if (created_by != null) 'created_by': created_by,
        if (description != null) 'description': description,
        if (end_at != null) 'end_at': end_at,
        if (id != null) 'id': id,
        if (location != null) 'location': location,
        if (metadata_json != null) 'metadata_json': metadata_json,
        if (start_at != null) 'start_at': start_at,
        if (status != null) 'status': status,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (title != null) 'title': title,
        if (updated_at != null) 'updated_at': updated_at,
        if (visibility_scope != null) 'visibility_scope': visibility_scope,
      };
}

typedef EventStatus = String;

class EventUpdate {
  const EventUpdate({this.description, this.end_at, this.location, this.metadata_json, this.start_at, this.status, this.title, this.visibility_scope});

  factory EventUpdate.fromJson(Map<String, dynamic> json) => EventUpdate(
        description: json['description'] as String?,
        end_at: json['end_at'] as String?,
        location: json['location'] as String?,
        metadata_json: json['metadata_json'] as Map<String, dynamic>?,
        start_at: json['start_at'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
        visibility_scope: json['visibility_scope'] as String?,
      );

  final String? description;
  final String? end_at;
  final String? location;
  final Map<String, dynamic>? metadata_json;
  final String? start_at;
  final EventStatus? status;
  final String? title;
  final EventVisibility? visibility_scope;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (description != null) 'description': description,
        if (end_at != null) 'end_at': end_at,
        if (location != null) 'location': location,
        if (metadata_json != null) 'metadata_json': metadata_json,
        if (start_at != null) 'start_at': start_at,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
        if (visibility_scope != null) 'visibility_scope': visibility_scope,
      };
}

typedef EventVisibility = String;

typedef ExpenseCategory = String;

class ExpenseRecordCreate {
  const ExpenseRecordCreate({this.amount, this.category, this.currency, this.description, this.payee, this.payment_method, this.reference, this.spent_at});

  factory ExpenseRecordCreate.fromJson(Map<String, dynamic> json) => ExpenseRecordCreate(
        amount: json['amount'],
        category: json['category'] as String?,
        currency: json['currency'] as String?,
        description: json['description'] as String?,
        payee: json['payee'] as String?,
        payment_method: json['payment_method'] as String?,
        reference: json['reference'] as String?,
        spent_at: json['spent_at'] as String?,
      );

  final dynamic amount;
  final ExpenseCategory? category;
  final String? currency;
  final String? description;
  final String? payee;
  final PaymentMethod? payment_method;
  final String? reference;
  final String? spent_at;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (category != null) 'category': category,
        if (currency != null) 'currency': currency,
        if (description != null) 'description': description,
        if (payee != null) 'payee': payee,
        if (payment_method != null) 'payment_method': payment_method,
        if (reference != null) 'reference': reference,
        if (spent_at != null) 'spent_at': spent_at,
      };
}

class ExpenseRecordResponse {
  const ExpenseRecordResponse({this.amount, this.category, this.created_at, this.created_by, this.currency, this.description, this.id, this.payee, this.payment_method, this.reference, this.spent_at, this.tenant_id});

  factory ExpenseRecordResponse.fromJson(Map<String, dynamic> json) => ExpenseRecordResponse(
        amount: json['amount'] as String?,
        category: json['category'] as String?,
        created_at: json['created_at'] as String?,
        created_by: json['created_by'] as String?,
        currency: json['currency'] as String?,
        description: json['description'] as String?,
        id: json['id'] as String?,
        payee: json['payee'] as String?,
        payment_method: json['payment_method'] as String?,
        reference: json['reference'] as String?,
        spent_at: json['spent_at'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final String? amount;
  final ExpenseCategory? category;
  final String? created_at;
  final String? created_by;
  final String? currency;
  final String? description;
  final String? id;
  final String? payee;
  final String? payment_method;
  final String? reference;
  final String? spent_at;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (category != null) 'category': category,
        if (created_at != null) 'created_at': created_at,
        if (created_by != null) 'created_by': created_by,
        if (currency != null) 'currency': currency,
        if (description != null) 'description': description,
        if (id != null) 'id': id,
        if (payee != null) 'payee': payee,
        if (payment_method != null) 'payment_method': payment_method,
        if (reference != null) 'reference': reference,
        if (spent_at != null) 'spent_at': spent_at,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

typedef FinancialIncomeType = String;

class ForgotPasswordRequest {
  const ForgotPasswordRequest({this.email});

  factory ForgotPasswordRequest.fromJson(Map<String, dynamic> json) => ForgotPasswordRequest(
        email: json['email'] as String?,
      );

  final String? email;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (email != null) 'email': email,
      };
}

class ForgotPasswordResponse {
  const ForgotPasswordResponse({this.message, this.reset_token});

  factory ForgotPasswordResponse.fromJson(Map<String, dynamic> json) => ForgotPasswordResponse(
        message: json['message'] as String?,
        reset_token: json['reset_token'] as String?,
      );

  final String? message;
  final String? reset_token;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (message != null) 'message': message,
        if (reset_token != null) 'reset_token': reset_token,
      };
}

class HTTPValidationError {
  const HTTPValidationError({this.detail});

  factory HTTPValidationError.fromJson(Map<String, dynamic> json) => HTTPValidationError(
        detail: (json['detail'] as List<dynamic>?)?.map((dynamic item) => ValidationError.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final List<ValidationError>? detail;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (detail != null) 'detail': detail!.map((item) => item.toJson()).toList(),
      };
}

class ImportResult {
  const ImportResult({this.dry_run, this.error_count, this.errors, this.success_count, this.total_rows});

  factory ImportResult.fromJson(Map<String, dynamic> json) => ImportResult(
        dry_run: json['dry_run'] as bool?,
        error_count: json['error_count'] as int?,
        errors: (json['errors'] as List<dynamic>?)?.map((dynamic item) => ImportRowError.fromJson(item as Map<String, dynamic>)).toList(),
        success_count: json['success_count'] as int?,
        total_rows: json['total_rows'] as int?,
      );

  final bool? dry_run;
  final int? error_count;
  final List<ImportRowError>? errors;
  final int? success_count;
  final int? total_rows;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (dry_run != null) 'dry_run': dry_run,
        if (error_count != null) 'error_count': error_count,
        if (errors != null) 'errors': errors!.map((item) => item.toJson()).toList(),
        if (success_count != null) 'success_count': success_count,
        if (total_rows != null) 'total_rows': total_rows,
      };
}

class ImportRowError {
  const ImportRowError({this.column, this.message, this.row_number, this.value});

  factory ImportRowError.fromJson(Map<String, dynamic> json) => ImportRowError(
        column: json['column'] as String?,
        message: json['message'] as String?,
        row_number: json['row_number'] as int?,
        value: json['value'] as String?,
      );

  final String? column;
  final String? message;
  final int? row_number;
  final String? value;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (column != null) 'column': column,
        if (message != null) 'message': message,
        if (row_number != null) 'row_number': row_number,
        if (value != null) 'value': value,
      };
}

class InboxNotificationResponse {
  const InboxNotificationResponse({this.category, this.correlation_id, this.created_at, this.event_id, this.event_type, this.id, this.metadata, this.priority, this.read_at, this.target_path});

  factory InboxNotificationResponse.fromJson(Map<String, dynamic> json) => InboxNotificationResponse(
        category: json['category'] as String?,
        correlation_id: json['correlation_id'] as String?,
        created_at: json['created_at'] as String?,
        event_id: json['event_id'] as String?,
        event_type: json['event_type'] as String?,
        id: json['id'] as String?,
        metadata: json['metadata'] as Map<String, dynamic>?,
        priority: json['priority'] as String?,
        read_at: json['read_at'] as String?,
        target_path: json['target_path'] as String?,
      );

  final String? category;
  final String? correlation_id;
  final String? created_at;
  final String? event_id;
  final String? event_type;
  final String? id;
  final Map<String, dynamic>? metadata;
  final String? priority;
  final String? read_at;
  final String? target_path;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (category != null) 'category': category,
        if (correlation_id != null) 'correlation_id': correlation_id,
        if (created_at != null) 'created_at': created_at,
        if (event_id != null) 'event_id': event_id,
        if (event_type != null) 'event_type': event_type,
        if (id != null) 'id': id,
        if (metadata != null) 'metadata': metadata,
        if (priority != null) 'priority': priority,
        if (read_at != null) 'read_at': read_at,
        if (target_path != null) 'target_path': target_path,
      };
}

class InboxResponse {
  const InboxResponse({this.items, this.unread_count});

  factory InboxResponse.fromJson(Map<String, dynamic> json) => InboxResponse(
        items: (json['items'] as List<dynamic>?)?.map((dynamic item) => InboxNotificationResponse.fromJson(item as Map<String, dynamic>)).toList(),
        unread_count: json['unread_count'] as int?,
      );

  final List<InboxNotificationResponse>? items;
  final int? unread_count;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (items != null) 'items': items!.map((item) => item.toJson()).toList(),
        if (unread_count != null) 'unread_count': unread_count,
      };
}

class IngestionJobHealthItemResponse {
  const IngestionJobHealthItemResponse({this.created_at, this.document_id, this.document_version_id, this.error_message, this.finished_at, this.job_id, this.started_at, this.status});

  factory IngestionJobHealthItemResponse.fromJson(Map<String, dynamic> json) => IngestionJobHealthItemResponse(
        created_at: json['created_at'] as String?,
        document_id: json['document_id'] as String?,
        document_version_id: json['document_version_id'] as String?,
        error_message: json['error_message'] as String?,
        finished_at: json['finished_at'] as String?,
        job_id: json['job_id'] as String?,
        started_at: json['started_at'] as String?,
        status: json['status'] as String?,
      );

  final String? created_at;
  final String? document_id;
  final String? document_version_id;
  final String? error_message;
  final String? finished_at;
  final String? job_id;
  final String? started_at;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (created_at != null) 'created_at': created_at,
        if (document_id != null) 'document_id': document_id,
        if (document_version_id != null) 'document_version_id': document_version_id,
        if (error_message != null) 'error_message': error_message,
        if (finished_at != null) 'finished_at': finished_at,
        if (job_id != null) 'job_id': job_id,
        if (started_at != null) 'started_at': started_at,
        if (status != null) 'status': status,
      };
}

class IngestionJobHealthResponse {
  const IngestionJobHealthResponse({this.completed_count, this.failed_count, this.processing_count, this.queued_count, this.recent_failures, this.retried_count});

  factory IngestionJobHealthResponse.fromJson(Map<String, dynamic> json) => IngestionJobHealthResponse(
        completed_count: json['completed_count'] as int?,
        failed_count: json['failed_count'] as int?,
        processing_count: json['processing_count'] as int?,
        queued_count: json['queued_count'] as int?,
        recent_failures: (json['recent_failures'] as List<dynamic>?)?.map((dynamic item) => IngestionJobHealthItemResponse.fromJson(item as Map<String, dynamic>)).toList(),
        retried_count: json['retried_count'] as int?,
      );

  final int? completed_count;
  final int? failed_count;
  final int? processing_count;
  final int? queued_count;
  final List<IngestionJobHealthItemResponse>? recent_failures;
  final int? retried_count;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (completed_count != null) 'completed_count': completed_count,
        if (failed_count != null) 'failed_count': failed_count,
        if (processing_count != null) 'processing_count': processing_count,
        if (queued_count != null) 'queued_count': queued_count,
        if (recent_failures != null) 'recent_failures': recent_failures!.map((item) => item.toJson()).toList(),
        if (retried_count != null) 'retried_count': retried_count,
      };
}

class IngestionJobResponse {
  const IngestionJobResponse({this.chunk_count, this.created_at, this.document_id, this.document_version_id, this.error_message, this.finished_at, this.id, this.indexed_chunk_count, this.started_at, this.status});

  factory IngestionJobResponse.fromJson(Map<String, dynamic> json) => IngestionJobResponse(
        chunk_count: json['chunk_count'] as int?,
        created_at: json['created_at'] as String?,
        document_id: json['document_id'] as String?,
        document_version_id: json['document_version_id'] as String?,
        error_message: json['error_message'] as String?,
        finished_at: json['finished_at'] as String?,
        id: json['id'] as String?,
        indexed_chunk_count: json['indexed_chunk_count'] as int?,
        started_at: json['started_at'] as String?,
        status: json['status'] as String?,
      );

  final int? chunk_count;
  final String? created_at;
  final String? document_id;
  final String? document_version_id;
  final String? error_message;
  final String? finished_at;
  final String? id;
  final int? indexed_chunk_count;
  final String? started_at;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (chunk_count != null) 'chunk_count': chunk_count,
        if (created_at != null) 'created_at': created_at,
        if (document_id != null) 'document_id': document_id,
        if (document_version_id != null) 'document_version_id': document_version_id,
        if (error_message != null) 'error_message': error_message,
        if (finished_at != null) 'finished_at': finished_at,
        if (id != null) 'id': id,
        if (indexed_chunk_count != null) 'indexed_chunk_count': indexed_chunk_count,
        if (started_at != null) 'started_at': started_at,
        if (status != null) 'status': status,
      };
}

class IngestionJobRetryResponse {
  const IngestionJobRetryResponse({this.job, this.retried});

  factory IngestionJobRetryResponse.fromJson(Map<String, dynamic> json) => IngestionJobRetryResponse(
        job: json['job'] == null ? null : IngestionJobResponse.fromJson(json['job'] as Map<String, dynamic>),
        retried: json['retried'] as bool?,
      );

  final IngestionJobResponse? job;
  final bool? retried;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (job != null) 'job': job!.toJson(),
        if (retried != null) 'retried': retried,
      };
}

class InvitationStatusResponse {
  const InvitationStatusResponse({this.created_at, this.email, this.expires_at, this.id, this.role_code, this.status});

  factory InvitationStatusResponse.fromJson(Map<String, dynamic> json) => InvitationStatusResponse(
        created_at: json['created_at'] as String?,
        email: json['email'] as String?,
        expires_at: json['expires_at'] as String?,
        id: json['id'] as String?,
        role_code: json['role_code'] as String?,
        status: json['status'] as String?,
      );

  final String? created_at;
  final String? email;
  final String? expires_at;
  final String? id;
  final String? role_code;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (created_at != null) 'created_at': created_at,
        if (email != null) 'email': email,
        if (expires_at != null) 'expires_at': expires_at,
        if (id != null) 'id': id,
        if (role_code != null) 'role_code': role_code,
        if (status != null) 'status': status,
      };
}

class InviteRequest {
  const InviteRequest({this.email, this.role_code, this.tenant_id});

  factory InviteRequest.fromJson(Map<String, dynamic> json) => InviteRequest(
        email: json['email'] as String?,
        role_code: json['role_code'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final String? email;
  final String? role_code;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (email != null) 'email': email,
        if (role_code != null) 'role_code': role_code,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class InviteResponse {
  const InviteResponse({this.delivery_message, this.delivery_simulation_only, this.delivery_status, this.email, this.expires_at, this.invitation_id, this.invite_token, this.role_code, this.status});

  factory InviteResponse.fromJson(Map<String, dynamic> json) => InviteResponse(
        delivery_message: json['delivery_message'] as String?,
        delivery_simulation_only: json['delivery_simulation_only'] as bool?,
        delivery_status: json['delivery_status'] as String?,
        email: json['email'] as String?,
        expires_at: json['expires_at'] as String?,
        invitation_id: json['invitation_id'] as String?,
        invite_token: json['invite_token'] as String?,
        role_code: json['role_code'] as String?,
        status: json['status'] as String?,
      );

  final String? delivery_message;
  final bool? delivery_simulation_only;
  final String? delivery_status;
  final String? email;
  final String? expires_at;
  final String? invitation_id;
  final String? invite_token;
  final String? role_code;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (delivery_message != null) 'delivery_message': delivery_message,
        if (delivery_simulation_only != null) 'delivery_simulation_only': delivery_simulation_only,
        if (delivery_status != null) 'delivery_status': delivery_status,
        if (email != null) 'email': email,
        if (expires_at != null) 'expires_at': expires_at,
        if (invitation_id != null) 'invitation_id': invitation_id,
        if (invite_token != null) 'invite_token': invite_token,
        if (role_code != null) 'role_code': role_code,
        if (status != null) 'status': status,
      };
}

class LanguagePreferenceResponse {
  const LanguagePreferenceResponse({this.preferred_language});

  factory LanguagePreferenceResponse.fromJson(Map<String, dynamic> json) => LanguagePreferenceResponse(
        preferred_language: json['preferred_language'] as String?,
      );

  final String? preferred_language;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (preferred_language != null) 'preferred_language': preferred_language,
      };
}

class LoginRequest {
  const LoginRequest({this.email, this.password, this.tenant_slug});

  factory LoginRequest.fromJson(Map<String, dynamic> json) => LoginRequest(
        email: json['email'] as String?,
        password: json['password'] as String?,
        tenant_slug: json['tenant_slug'] as String?,
      );

  final String? email;
  final String? password;
  final String? tenant_slug;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (email != null) 'email': email,
        if (password != null) 'password': password,
        if (tenant_slug != null) 'tenant_slug': tenant_slug,
      };
}

class ManagedTenantUserActionResponse {
  const ManagedTenantUserActionResponse({this.membership_status, this.message, this.revoked_session_count});

  factory ManagedTenantUserActionResponse.fromJson(Map<String, dynamic> json) => ManagedTenantUserActionResponse(
        membership_status: json['membership_status'] as String?,
        message: json['message'] as String?,
        revoked_session_count: json['revoked_session_count'] as int?,
      );

  final String? membership_status;
  final String? message;
  final int? revoked_session_count;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (membership_status != null) 'membership_status': membership_status,
        if (message != null) 'message': message,
        if (revoked_session_count != null) 'revoked_session_count': revoked_session_count,
      };
}

class ManagedTenantUserResponse {
  const ManagedTenantUserResponse({this.active_session_count, this.display_name, this.email, this.last_login_at, this.last_security_event_action, this.last_security_event_at, this.membership_status, this.profile_type, this.roles, this.user_id, this.user_status});

  factory ManagedTenantUserResponse.fromJson(Map<String, dynamic> json) => ManagedTenantUserResponse(
        active_session_count: json['active_session_count'] as int?,
        display_name: json['display_name'] as String?,
        email: json['email'] as String?,
        last_login_at: json['last_login_at'] as String?,
        last_security_event_action: json['last_security_event_action'] as String?,
        last_security_event_at: json['last_security_event_at'] as String?,
        membership_status: json['membership_status'] as String?,
        profile_type: json['profile_type'] as String?,
        roles: (json['roles'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        user_id: json['user_id'] as String?,
        user_status: json['user_status'] as String?,
      );

  final int? active_session_count;
  final String? display_name;
  final String? email;
  final String? last_login_at;
  final String? last_security_event_action;
  final String? last_security_event_at;
  final String? membership_status;
  final String? profile_type;
  final List<String>? roles;
  final String? user_id;
  final String? user_status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (active_session_count != null) 'active_session_count': active_session_count,
        if (display_name != null) 'display_name': display_name,
        if (email != null) 'email': email,
        if (last_login_at != null) 'last_login_at': last_login_at,
        if (last_security_event_action != null) 'last_security_event_action': last_security_event_action,
        if (last_security_event_at != null) 'last_security_event_at': last_security_event_at,
        if (membership_status != null) 'membership_status': membership_status,
        if (profile_type != null) 'profile_type': profile_type,
        if (roles != null) 'roles': roles,
        if (user_id != null) 'user_id': user_id,
        if (user_status != null) 'user_status': user_status,
      };
}

class ManagedTenantUserRolesUpdateRequest {
  const ManagedTenantUserRolesUpdateRequest({this.role_codes});

  factory ManagedTenantUserRolesUpdateRequest.fromJson(Map<String, dynamic> json) => ManagedTenantUserRolesUpdateRequest(
        role_codes: (json['role_codes'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
      );

  final List<String>? role_codes;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (role_codes != null) 'role_codes': role_codes,
      };
}

class ManagedTenantUserRolesUpdateResponse {
  const ManagedTenantUserRolesUpdateResponse({this.message, this.role_codes});

  factory ManagedTenantUserRolesUpdateResponse.fromJson(Map<String, dynamic> json) => ManagedTenantUserRolesUpdateResponse(
        message: json['message'] as String?,
        role_codes: (json['role_codes'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
      );

  final String? message;
  final List<String>? role_codes;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (message != null) 'message': message,
        if (role_codes != null) 'role_codes': role_codes,
      };
}

class MemberBalanceResponse {
  const MemberBalanceResponse({this.contribution_count, this.profile, this.total_balance, this.total_expected, this.total_paid});

  factory MemberBalanceResponse.fromJson(Map<String, dynamic> json) => MemberBalanceResponse(
        contribution_count: json['contribution_count'] as int?,
        profile: json['profile'] == null ? null : MembershipProfileResponse.fromJson(json['profile'] as Map<String, dynamic>),
        total_balance: json['total_balance'] as String?,
        total_expected: json['total_expected'] as String?,
        total_paid: json['total_paid'] as String?,
      );

  final int? contribution_count;
  final MembershipProfileResponse? profile;
  final String? total_balance;
  final String? total_expected;
  final String? total_paid;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (contribution_count != null) 'contribution_count': contribution_count,
        if (profile != null) 'profile': profile!.toJson(),
        if (total_balance != null) 'total_balance': total_balance,
        if (total_expected != null) 'total_expected': total_expected,
        if (total_paid != null) 'total_paid': total_paid,
      };
}

class MemberStatementResponse {
  const MemberStatementResponse({this.contributions, this.profile, this.summary});

  factory MemberStatementResponse.fromJson(Map<String, dynamic> json) => MemberStatementResponse(
        contributions: (json['contributions'] as List<dynamic>?)?.map((dynamic item) => ContributionRecordResponse.fromJson(item as Map<String, dynamic>)).toList(),
        profile: json['profile'] == null ? null : MembershipProfileResponse.fromJson(json['profile'] as Map<String, dynamic>),
        summary: json['summary'] == null ? null : MemberBalanceResponse.fromJson(json['summary'] as Map<String, dynamic>),
      );

  final List<ContributionRecordResponse>? contributions;
  final MembershipProfileResponse? profile;
  final MemberBalanceResponse? summary;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (contributions != null) 'contributions': contributions!.map((item) => item.toJson()).toList(),
        if (profile != null) 'profile': profile!.toJson(),
        if (summary != null) 'summary': summary!.toJson(),
      };
}

class MembershipProfileCreate {
  const MembershipProfileCreate({this.city, this.country_code, this.display_name, this.email, this.first_name, this.house_number, this.last_name, this.login_identifier, this.member_code, this.membership_type, this.phone, this.postal_code, this.provision_access, this.status, this.street_name, this.temporary_password});

  factory MembershipProfileCreate.fromJson(Map<String, dynamic> json) => MembershipProfileCreate(
        city: json['city'] as String?,
        country_code: json['country_code'] as String?,
        display_name: json['display_name'] as String?,
        email: json['email'] as String?,
        first_name: json['first_name'] as String?,
        house_number: json['house_number'] as String?,
        last_name: json['last_name'] as String?,
        login_identifier: json['login_identifier'] as String?,
        member_code: json['member_code'] as String?,
        membership_type: json['membership_type'] as String?,
        phone: json['phone'] as String?,
        postal_code: json['postal_code'] as String?,
        provision_access: json['provision_access'] as bool?,
        status: json['status'] as String?,
        street_name: json['street_name'] as String?,
        temporary_password: json['temporary_password'] as String?,
      );

  final String? city;
  final String? country_code;
  final String? display_name;
  final String? email;
  final String? first_name;
  final String? house_number;
  final String? last_name;
  final String? login_identifier;
  final String? member_code;
  final MembershipType? membership_type;
  final String? phone;
  final String? postal_code;
  final bool? provision_access;
  final MembershipStatus? status;
  final String? street_name;
  final String? temporary_password;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (city != null) 'city': city,
        if (country_code != null) 'country_code': country_code,
        if (display_name != null) 'display_name': display_name,
        if (email != null) 'email': email,
        if (first_name != null) 'first_name': first_name,
        if (house_number != null) 'house_number': house_number,
        if (last_name != null) 'last_name': last_name,
        if (login_identifier != null) 'login_identifier': login_identifier,
        if (member_code != null) 'member_code': member_code,
        if (membership_type != null) 'membership_type': membership_type,
        if (phone != null) 'phone': phone,
        if (postal_code != null) 'postal_code': postal_code,
        if (provision_access != null) 'provision_access': provision_access,
        if (status != null) 'status': status,
        if (street_name != null) 'street_name': street_name,
        if (temporary_password != null) 'temporary_password': temporary_password,
      };
}

class MembershipProfileResponse {
  const MembershipProfileResponse({this.city, this.country_code, this.created_at, this.display_name, this.email, this.first_name, this.house_number, this.id, this.joined_at, this.last_name, this.member_code, this.membership_type, this.phone, this.postal_code, this.status, this.street_name, this.tenant_id, this.updated_at, this.user_id});

  factory MembershipProfileResponse.fromJson(Map<String, dynamic> json) => MembershipProfileResponse(
        city: json['city'] as String?,
        country_code: json['country_code'] as String?,
        created_at: json['created_at'] as String?,
        display_name: json['display_name'] as String?,
        email: json['email'] as String?,
        first_name: json['first_name'] as String?,
        house_number: json['house_number'] as String?,
        id: json['id'] as String?,
        joined_at: json['joined_at'] as String?,
        last_name: json['last_name'] as String?,
        member_code: json['member_code'] as String?,
        membership_type: json['membership_type'] as String?,
        phone: json['phone'] as String?,
        postal_code: json['postal_code'] as String?,
        status: json['status'] as String?,
        street_name: json['street_name'] as String?,
        tenant_id: json['tenant_id'] as String?,
        updated_at: json['updated_at'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? city;
  final String? country_code;
  final String? created_at;
  final String? display_name;
  final String? email;
  final String? first_name;
  final String? house_number;
  final String? id;
  final String? joined_at;
  final String? last_name;
  final String? member_code;
  final String? membership_type;
  final String? phone;
  final String? postal_code;
  final String? status;
  final String? street_name;
  final String? tenant_id;
  final String? updated_at;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (city != null) 'city': city,
        if (country_code != null) 'country_code': country_code,
        if (created_at != null) 'created_at': created_at,
        if (display_name != null) 'display_name': display_name,
        if (email != null) 'email': email,
        if (first_name != null) 'first_name': first_name,
        if (house_number != null) 'house_number': house_number,
        if (id != null) 'id': id,
        if (joined_at != null) 'joined_at': joined_at,
        if (last_name != null) 'last_name': last_name,
        if (member_code != null) 'member_code': member_code,
        if (membership_type != null) 'membership_type': membership_type,
        if (phone != null) 'phone': phone,
        if (postal_code != null) 'postal_code': postal_code,
        if (status != null) 'status': status,
        if (street_name != null) 'street_name': street_name,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (updated_at != null) 'updated_at': updated_at,
        if (user_id != null) 'user_id': user_id,
      };
}

class MembershipProfileUpdate {
  const MembershipProfileUpdate({this.city, this.country_code, this.display_name, this.email, this.first_name, this.house_number, this.last_name, this.member_code, this.membership_type, this.phone, this.postal_code, this.status, this.street_name});

  factory MembershipProfileUpdate.fromJson(Map<String, dynamic> json) => MembershipProfileUpdate(
        city: json['city'] as String?,
        country_code: json['country_code'] as String?,
        display_name: json['display_name'] as String?,
        email: json['email'] as String?,
        first_name: json['first_name'] as String?,
        house_number: json['house_number'] as String?,
        last_name: json['last_name'] as String?,
        member_code: json['member_code'] as String?,
        membership_type: json['membership_type'] as String?,
        phone: json['phone'] as String?,
        postal_code: json['postal_code'] as String?,
        status: json['status'] as String?,
        street_name: json['street_name'] as String?,
      );

  final String? city;
  final String? country_code;
  final String? display_name;
  final String? email;
  final String? first_name;
  final String? house_number;
  final String? last_name;
  final String? member_code;
  final MembershipType? membership_type;
  final String? phone;
  final String? postal_code;
  final MembershipStatus? status;
  final String? street_name;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (city != null) 'city': city,
        if (country_code != null) 'country_code': country_code,
        if (display_name != null) 'display_name': display_name,
        if (email != null) 'email': email,
        if (first_name != null) 'first_name': first_name,
        if (house_number != null) 'house_number': house_number,
        if (last_name != null) 'last_name': last_name,
        if (member_code != null) 'member_code': member_code,
        if (membership_type != null) 'membership_type': membership_type,
        if (phone != null) 'phone': phone,
        if (postal_code != null) 'postal_code': postal_code,
        if (status != null) 'status': status,
        if (street_name != null) 'street_name': street_name,
      };
}

typedef MembershipStatus = String;

typedef MembershipType = String;

class MfaCompleteLoginRequest {
  const MfaCompleteLoginRequest({this.code, this.mfa_token});

  factory MfaCompleteLoginRequest.fromJson(Map<String, dynamic> json) => MfaCompleteLoginRequest(
        code: json['code'] as String?,
        mfa_token: json['mfa_token'] as String?,
      );

  final String? code;
  final String? mfa_token;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (code != null) 'code': code,
        if (mfa_token != null) 'mfa_token': mfa_token,
      };
}

class MfaEnrollResponse {
  const MfaEnrollResponse({this.qr_code_url, this.secret, this.uri});

  factory MfaEnrollResponse.fromJson(Map<String, dynamic> json) => MfaEnrollResponse(
        qr_code_url: json['qr_code_url'] as String?,
        secret: json['secret'] as String?,
        uri: json['uri'] as String?,
      );

  final String? qr_code_url;
  final String? secret;
  final String? uri;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (qr_code_url != null) 'qr_code_url': qr_code_url,
        if (secret != null) 'secret': secret,
        if (uri != null) 'uri': uri,
      };
}

class MfaLoginResponse {
  const MfaLoginResponse({this.access_token, this.expires_in, this.password_change_required, this.tenant_id, this.token_type, this.user_id});

  factory MfaLoginResponse.fromJson(Map<String, dynamic> json) => MfaLoginResponse(
        access_token: json['access_token'] as String?,
        expires_in: json['expires_in'] as int?,
        password_change_required: json['password_change_required'] as bool?,
        tenant_id: json['tenant_id'] as String?,
        token_type: json['token_type'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? access_token;
  final int? expires_in;
  final bool? password_change_required;
  final String? tenant_id;
  final String? token_type;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_token != null) 'access_token': access_token,
        if (expires_in != null) 'expires_in': expires_in,
        if (password_change_required != null) 'password_change_required': password_change_required,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (token_type != null) 'token_type': token_type,
        if (user_id != null) 'user_id': user_id,
      };
}

class MfaRequiredResponse {
  const MfaRequiredResponse({this.expires_in, this.mfa_required, this.mfa_token});

  factory MfaRequiredResponse.fromJson(Map<String, dynamic> json) => MfaRequiredResponse(
        expires_in: json['expires_in'] as int?,
        mfa_required: json['mfa_required'] as bool?,
        mfa_token: json['mfa_token'] as String?,
      );

  final int? expires_in;
  final bool? mfa_required;
  final String? mfa_token;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (expires_in != null) 'expires_in': expires_in,
        if (mfa_required != null) 'mfa_required': mfa_required,
        if (mfa_token != null) 'mfa_token': mfa_token,
      };
}

class MfaStatusResponse {
  const MfaStatusResponse({this.enabled, this.enrolled});

  factory MfaStatusResponse.fromJson(Map<String, dynamic> json) => MfaStatusResponse(
        enabled: json['enabled'] as bool?,
        enrolled: json['enrolled'] as bool?,
      );

  final bool? enabled;
  final bool? enrolled;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (enabled != null) 'enabled': enabled,
        if (enrolled != null) 'enrolled': enrolled,
      };
}

class MfaVerifyRequest {
  const MfaVerifyRequest({this.code});

  factory MfaVerifyRequest.fromJson(Map<String, dynamic> json) => MfaVerifyRequest(
        code: json['code'] as String?,
      );

  final String? code;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (code != null) 'code': code,
      };
}

class MfaVerifyResponse {
  const MfaVerifyResponse({this.enabled, this.message});

  factory MfaVerifyResponse.fromJson(Map<String, dynamic> json) => MfaVerifyResponse(
        enabled: json['enabled'] as bool?,
        message: json['message'] as String?,
      );

  final bool? enabled;
  final String? message;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (enabled != null) 'enabled': enabled,
        if (message != null) 'message': message,
      };
}

class MobilePushTokenRequest {
  const MobilePushTokenRequest({this.browser, this.device_metadata, this.fcm_token, this.installation_id, this.platform});

  factory MobilePushTokenRequest.fromJson(Map<String, dynamic> json) => MobilePushTokenRequest(
        browser: json['browser'] as String?,
        device_metadata: json['device_metadata'] as Map<String, dynamic>?,
        fcm_token: json['fcm_token'] as String?,
        installation_id: json['installation_id'] as String?,
        platform: json['platform'] as String?,
      );

  final String? browser;
  final Map<String, dynamic>? device_metadata;
  final String? fcm_token;
  final String? installation_id;
  final String? platform;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (browser != null) 'browser': browser,
        if (device_metadata != null) 'device_metadata': device_metadata,
        if (fcm_token != null) 'fcm_token': fcm_token,
        if (installation_id != null) 'installation_id': installation_id,
        if (platform != null) 'platform': platform,
      };
}

class ModuleNavigationEntryResponse {
  const ModuleNavigationEntryResponse({this.capabilities, this.key, this.label_key, this.order, this.path, this.section});

  factory ModuleNavigationEntryResponse.fromJson(Map<String, dynamic> json) => ModuleNavigationEntryResponse(
        capabilities: (json['capabilities'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        key: json['key'] as String?,
        label_key: json['label_key'] as String?,
        order: json['order'] as int?,
        path: json['path'] as String?,
        section: json['section'] as String?,
      );

  final List<String>? capabilities;
  final String? key;
  final String? label_key;
  final int? order;
  final String? path;
  final String? section;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (capabilities != null) 'capabilities': capabilities,
        if (key != null) 'key': key,
        if (label_key != null) 'label_key': label_key,
        if (order != null) 'order': order,
        if (path != null) 'path': path,
        if (section != null) 'section': section,
      };
}

class ModuleToggles {
  const ModuleToggles({this.announcements, this.chat, this.contributions, this.disciplinary, this.events, this.membership, this.notifications, this.policies});

  factory ModuleToggles.fromJson(Map<String, dynamic> json) => ModuleToggles(
        announcements: json['announcements'] as bool?,
        chat: json['chat'] as bool?,
        contributions: json['contributions'] as bool?,
        disciplinary: json['disciplinary'] as bool?,
        events: json['events'] as bool?,
        membership: json['membership'] as bool?,
        notifications: json['notifications'] as bool?,
        policies: json['policies'] as bool?,
      );

  final bool? announcements;
  final bool? chat;
  final bool? contributions;
  final bool? disciplinary;
  final bool? events;
  final bool? membership;
  final bool? notifications;
  final bool? policies;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (announcements != null) 'announcements': announcements,
        if (chat != null) 'chat': chat,
        if (contributions != null) 'contributions': contributions,
        if (disciplinary != null) 'disciplinary': disciplinary,
        if (events != null) 'events': events,
        if (membership != null) 'membership': membership,
        if (notifications != null) 'notifications': notifications,
        if (policies != null) 'policies': policies,
      };
}

class NotificationChannelResponse {
  const NotificationChannelResponse({this.channel, this.configured, this.description, this.display_name, this.polling_supported, this.simulation_only, this.target_hint});

  factory NotificationChannelResponse.fromJson(Map<String, dynamic> json) => NotificationChannelResponse(
        channel: json['channel'] as String?,
        configured: json['configured'] as bool?,
        description: json['description'] as String?,
        display_name: json['display_name'] as String?,
        polling_supported: json['polling_supported'] as bool?,
        simulation_only: json['simulation_only'] as bool?,
        target_hint: json['target_hint'] as String?,
      );

  final String? channel;
  final bool? configured;
  final String? description;
  final String? display_name;
  final bool? polling_supported;
  final bool? simulation_only;
  final String? target_hint;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (configured != null) 'configured': configured,
        if (description != null) 'description': description,
        if (display_name != null) 'display_name': display_name,
        if (polling_supported != null) 'polling_supported': polling_supported,
        if (simulation_only != null) 'simulation_only': simulation_only,
        if (target_hint != null) 'target_hint': target_hint,
      };
}

class NotificationDeviceRevocationResponse {
  const NotificationDeviceRevocationResponse({this.disabled_fcm_tokens, this.disabled_web_subscriptions, this.revoked_profiles});

  factory NotificationDeviceRevocationResponse.fromJson(Map<String, dynamic> json) => NotificationDeviceRevocationResponse(
        disabled_fcm_tokens: json['disabled_fcm_tokens'] as int?,
        disabled_web_subscriptions: json['disabled_web_subscriptions'] as int?,
        revoked_profiles: json['revoked_profiles'] as int?,
      );

  final int? disabled_fcm_tokens;
  final int? disabled_web_subscriptions;
  final int? revoked_profiles;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (disabled_fcm_tokens != null) 'disabled_fcm_tokens': disabled_fcm_tokens,
        if (disabled_web_subscriptions != null) 'disabled_web_subscriptions': disabled_web_subscriptions,
        if (revoked_profiles != null) 'revoked_profiles': revoked_profiles,
      };
}

class NotificationDispatchRequest {
  const NotificationDispatchRequest({this.body, this.channel, this.recipient, this.subject});

  factory NotificationDispatchRequest.fromJson(Map<String, dynamic> json) => NotificationDispatchRequest(
        body: json['body'] as String?,
        channel: json['channel'] as String?,
        recipient: json['recipient'] as String?,
        subject: json['subject'] as String?,
      );

  final String? body;
  final String? channel;
  final String? recipient;
  final String? subject;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (body != null) 'body': body,
        if (channel != null) 'channel': channel,
        if (recipient != null) 'recipient': recipient,
        if (subject != null) 'subject': subject,
      };
}

class NotificationDispatchResponse {
  const NotificationDispatchResponse({this.channel, this.delivered, this.delivery_stage, this.message, this.polling_supported, this.provider_reference, this.reconciliation_status, this.reconciliation_supported, this.simulation_only, this.status});

  factory NotificationDispatchResponse.fromJson(Map<String, dynamic> json) => NotificationDispatchResponse(
        channel: json['channel'] as String?,
        delivered: json['delivered'] as bool?,
        delivery_stage: json['delivery_stage'] as String?,
        message: json['message'] as String?,
        polling_supported: json['polling_supported'] as bool?,
        provider_reference: json['provider_reference'] as String?,
        reconciliation_status: json['reconciliation_status'] as String?,
        reconciliation_supported: json['reconciliation_supported'] as bool?,
        simulation_only: json['simulation_only'] as bool?,
        status: json['status'] as String?,
      );

  final String? channel;
  final bool? delivered;
  final String? delivery_stage;
  final String? message;
  final bool? polling_supported;
  final String? provider_reference;
  final String? reconciliation_status;
  final bool? reconciliation_supported;
  final bool? simulation_only;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (delivered != null) 'delivered': delivered,
        if (delivery_stage != null) 'delivery_stage': delivery_stage,
        if (message != null) 'message': message,
        if (polling_supported != null) 'polling_supported': polling_supported,
        if (provider_reference != null) 'provider_reference': provider_reference,
        if (reconciliation_status != null) 'reconciliation_status': reconciliation_status,
        if (reconciliation_supported != null) 'reconciliation_supported': reconciliation_supported,
        if (simulation_only != null) 'simulation_only': simulation_only,
        if (status != null) 'status': status,
      };
}

class NotificationHealthResponse {
  const NotificationHealthResponse({this.disabled_fcm_tokens, this.disabled_web_subscriptions, this.failed_outbox, this.firebase_configured, this.last_successful_dispatch_at, this.oldest_pending_seconds, this.pending_outbox, this.retrying_fcm_tokens, this.retrying_web_subscriptions, this.web_push_configured, this.worker_running});

  factory NotificationHealthResponse.fromJson(Map<String, dynamic> json) => NotificationHealthResponse(
        disabled_fcm_tokens: json['disabled_fcm_tokens'] as int?,
        disabled_web_subscriptions: json['disabled_web_subscriptions'] as int?,
        failed_outbox: json['failed_outbox'] as int?,
        firebase_configured: json['firebase_configured'] as bool?,
        last_successful_dispatch_at: json['last_successful_dispatch_at'] as String?,
        oldest_pending_seconds: json['oldest_pending_seconds'] as int?,
        pending_outbox: json['pending_outbox'] as int?,
        retrying_fcm_tokens: json['retrying_fcm_tokens'] as int?,
        retrying_web_subscriptions: json['retrying_web_subscriptions'] as int?,
        web_push_configured: json['web_push_configured'] as bool?,
        worker_running: json['worker_running'] as bool?,
      );

  final int? disabled_fcm_tokens;
  final int? disabled_web_subscriptions;
  final int? failed_outbox;
  final bool? firebase_configured;
  final String? last_successful_dispatch_at;
  final int? oldest_pending_seconds;
  final int? pending_outbox;
  final int? retrying_fcm_tokens;
  final int? retrying_web_subscriptions;
  final bool? web_push_configured;
  final bool? worker_running;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (disabled_fcm_tokens != null) 'disabled_fcm_tokens': disabled_fcm_tokens,
        if (disabled_web_subscriptions != null) 'disabled_web_subscriptions': disabled_web_subscriptions,
        if (failed_outbox != null) 'failed_outbox': failed_outbox,
        if (firebase_configured != null) 'firebase_configured': firebase_configured,
        if (last_successful_dispatch_at != null) 'last_successful_dispatch_at': last_successful_dispatch_at,
        if (oldest_pending_seconds != null) 'oldest_pending_seconds': oldest_pending_seconds,
        if (pending_outbox != null) 'pending_outbox': pending_outbox,
        if (retrying_fcm_tokens != null) 'retrying_fcm_tokens': retrying_fcm_tokens,
        if (retrying_web_subscriptions != null) 'retrying_web_subscriptions': retrying_web_subscriptions,
        if (web_push_configured != null) 'web_push_configured': web_push_configured,
        if (worker_running != null) 'worker_running': worker_running,
      };
}

class NotificationHistoryEntry {
  const NotificationHistoryEntry({this.action, this.channel, this.created_at, this.delivered, this.delivery_stage, this.id, this.message, this.polling_supported, this.provider_reference, this.recipient, this.reconciliation_status, this.reconciliation_supported, this.retry_eligible, this.retry_source_provider_reference, this.retry_supported, this.simulation_only, this.stale_minutes, this.stale_pending, this.status});

  factory NotificationHistoryEntry.fromJson(Map<String, dynamic> json) => NotificationHistoryEntry(
        action: json['action'] as String?,
        channel: json['channel'] as String?,
        created_at: json['created_at'] as String?,
        delivered: json['delivered'] as bool?,
        delivery_stage: json['delivery_stage'] as String?,
        id: json['id'] as String?,
        message: json['message'] as String?,
        polling_supported: json['polling_supported'] as bool?,
        provider_reference: json['provider_reference'] as String?,
        recipient: json['recipient'] as String?,
        reconciliation_status: json['reconciliation_status'] as String?,
        reconciliation_supported: json['reconciliation_supported'] as bool?,
        retry_eligible: json['retry_eligible'] as bool?,
        retry_source_provider_reference: json['retry_source_provider_reference'] as String?,
        retry_supported: json['retry_supported'] as bool?,
        simulation_only: json['simulation_only'] as bool?,
        stale_minutes: json['stale_minutes'] as int?,
        stale_pending: json['stale_pending'] as bool?,
        status: json['status'] as String?,
      );

  final String? action;
  final String? channel;
  final String? created_at;
  final bool? delivered;
  final String? delivery_stage;
  final String? id;
  final String? message;
  final bool? polling_supported;
  final String? provider_reference;
  final String? recipient;
  final String? reconciliation_status;
  final bool? reconciliation_supported;
  final bool? retry_eligible;
  final String? retry_source_provider_reference;
  final bool? retry_supported;
  final bool? simulation_only;
  final int? stale_minutes;
  final bool? stale_pending;
  final String? status;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (action != null) 'action': action,
        if (channel != null) 'channel': channel,
        if (created_at != null) 'created_at': created_at,
        if (delivered != null) 'delivered': delivered,
        if (delivery_stage != null) 'delivery_stage': delivery_stage,
        if (id != null) 'id': id,
        if (message != null) 'message': message,
        if (polling_supported != null) 'polling_supported': polling_supported,
        if (provider_reference != null) 'provider_reference': provider_reference,
        if (recipient != null) 'recipient': recipient,
        if (reconciliation_status != null) 'reconciliation_status': reconciliation_status,
        if (reconciliation_supported != null) 'reconciliation_supported': reconciliation_supported,
        if (retry_eligible != null) 'retry_eligible': retry_eligible,
        if (retry_source_provider_reference != null) 'retry_source_provider_reference': retry_source_provider_reference,
        if (retry_supported != null) 'retry_supported': retry_supported,
        if (simulation_only != null) 'simulation_only': simulation_only,
        if (stale_minutes != null) 'stale_minutes': stale_minutes,
        if (stale_pending != null) 'stale_pending': stale_pending,
        if (status != null) 'status': status,
      };
}

class NotificationHistoryResponse {
  const NotificationHistoryResponse({this.items, this.summary});

  factory NotificationHistoryResponse.fromJson(Map<String, dynamic> json) => NotificationHistoryResponse(
        items: (json['items'] as List<dynamic>?)?.map((dynamic item) => NotificationHistoryEntry.fromJson(item as Map<String, dynamic>)).toList(),
        summary: json['summary'] == null ? null : NotificationHistorySummary.fromJson(json['summary'] as Map<String, dynamic>),
      );

  final List<NotificationHistoryEntry>? items;
  final NotificationHistorySummary? summary;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (items != null) 'items': items!.map((item) => item.toJson()).toList(),
        if (summary != null) 'summary': summary!.toJson(),
      };
}

class NotificationHistorySummary {
  const NotificationHistorySummary({this.delivered, this.failed, this.pending, this.simulated, this.stale_pending, this.total});

  factory NotificationHistorySummary.fromJson(Map<String, dynamic> json) => NotificationHistorySummary(
        delivered: json['delivered'] as int?,
        failed: json['failed'] as int?,
        pending: json['pending'] as int?,
        simulated: json['simulated'] as int?,
        stale_pending: json['stale_pending'] as int?,
        total: json['total'] as int?,
      );

  final int? delivered;
  final int? failed;
  final int? pending;
  final int? simulated;
  final int? stale_pending;
  final int? total;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (delivered != null) 'delivered': delivered,
        if (failed != null) 'failed': failed,
        if (pending != null) 'pending': pending,
        if (simulated != null) 'simulated': simulated,
        if (stale_pending != null) 'stale_pending': stale_pending,
        if (total != null) 'total': total,
      };
}

class NotificationPreferencesResponse {
  const NotificationPreferencesResponse({this.announcements_enabled, this.discipline_enabled, this.events_enabled, this.finance_enabled, this.push_enabled});

  factory NotificationPreferencesResponse.fromJson(Map<String, dynamic> json) => NotificationPreferencesResponse(
        announcements_enabled: json['announcements_enabled'] as bool?,
        discipline_enabled: json['discipline_enabled'] as bool?,
        events_enabled: json['events_enabled'] as bool?,
        finance_enabled: json['finance_enabled'] as bool?,
        push_enabled: json['push_enabled'] as bool?,
      );

  final bool? announcements_enabled;
  final bool? discipline_enabled;
  final bool? events_enabled;
  final bool? finance_enabled;
  final bool? push_enabled;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (announcements_enabled != null) 'announcements_enabled': announcements_enabled,
        if (discipline_enabled != null) 'discipline_enabled': discipline_enabled,
        if (events_enabled != null) 'events_enabled': events_enabled,
        if (finance_enabled != null) 'finance_enabled': finance_enabled,
        if (push_enabled != null) 'push_enabled': push_enabled,
      };
}

class NotificationPreferencesUpdate {
  const NotificationPreferencesUpdate({this.announcements_enabled, this.discipline_enabled, this.events_enabled, this.finance_enabled, this.push_enabled});

  factory NotificationPreferencesUpdate.fromJson(Map<String, dynamic> json) => NotificationPreferencesUpdate(
        announcements_enabled: json['announcements_enabled'] as bool?,
        discipline_enabled: json['discipline_enabled'] as bool?,
        events_enabled: json['events_enabled'] as bool?,
        finance_enabled: json['finance_enabled'] as bool?,
        push_enabled: json['push_enabled'] as bool?,
      );

  final bool? announcements_enabled;
  final bool? discipline_enabled;
  final bool? events_enabled;
  final bool? finance_enabled;
  final bool? push_enabled;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (announcements_enabled != null) 'announcements_enabled': announcements_enabled,
        if (discipline_enabled != null) 'discipline_enabled': discipline_enabled,
        if (events_enabled != null) 'events_enabled': events_enabled,
        if (finance_enabled != null) 'finance_enabled': finance_enabled,
        if (push_enabled != null) 'push_enabled': push_enabled,
      };
}

class NotificationReconciliationCallbackRequest {
  const NotificationReconciliationCallbackRequest({this.channel, this.delivery_stage, this.external_status, this.provider_message, this.provider_reference, this.tenant_id});

  factory NotificationReconciliationCallbackRequest.fromJson(Map<String, dynamic> json) => NotificationReconciliationCallbackRequest(
        channel: json['channel'] as String?,
        delivery_stage: json['delivery_stage'] as String?,
        external_status: json['external_status'] as String?,
        provider_message: json['provider_message'] as String?,
        provider_reference: json['provider_reference'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final String? channel;
  final String? delivery_stage;
  final String? external_status;
  final String? provider_message;
  final String? provider_reference;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (delivery_stage != null) 'delivery_stage': delivery_stage,
        if (external_status != null) 'external_status': external_status,
        if (provider_message != null) 'provider_message': provider_message,
        if (provider_reference != null) 'provider_reference': provider_reference,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class NotificationReconciliationCallbackResponse {
  const NotificationReconciliationCallbackResponse({this.channel, this.delivery_stage, this.provider_reference, this.reconciliation_status, this.updated});

  factory NotificationReconciliationCallbackResponse.fromJson(Map<String, dynamic> json) => NotificationReconciliationCallbackResponse(
        channel: json['channel'] as String?,
        delivery_stage: json['delivery_stage'] as String?,
        provider_reference: json['provider_reference'] as String?,
        reconciliation_status: json['reconciliation_status'] as String?,
        updated: json['updated'] as bool?,
      );

  final String? channel;
  final String? delivery_stage;
  final String? provider_reference;
  final String? reconciliation_status;
  final bool? updated;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (delivery_stage != null) 'delivery_stage': delivery_stage,
        if (provider_reference != null) 'provider_reference': provider_reference,
        if (reconciliation_status != null) 'reconciliation_status': reconciliation_status,
        if (updated != null) 'updated': updated,
      };
}

class NotificationReconciliationPollRequest {
  const NotificationReconciliationPollRequest({this.channel, this.provider_reference});

  factory NotificationReconciliationPollRequest.fromJson(Map<String, dynamic> json) => NotificationReconciliationPollRequest(
        channel: json['channel'] as String?,
        provider_reference: json['provider_reference'] as String?,
      );

  final String? channel;
  final String? provider_reference;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (provider_reference != null) 'provider_reference': provider_reference,
      };
}

class NotificationReconciliationPollResponse {
  const NotificationReconciliationPollResponse({this.channel, this.delivery_stage, this.external_status, this.provider_message, this.provider_reference, this.reconciliation_status, this.updated});

  factory NotificationReconciliationPollResponse.fromJson(Map<String, dynamic> json) => NotificationReconciliationPollResponse(
        channel: json['channel'] as String?,
        delivery_stage: json['delivery_stage'] as String?,
        external_status: json['external_status'] as String?,
        provider_message: json['provider_message'] as String?,
        provider_reference: json['provider_reference'] as String?,
        reconciliation_status: json['reconciliation_status'] as String?,
        updated: json['updated'] as bool?,
      );

  final String? channel;
  final String? delivery_stage;
  final String? external_status;
  final String? provider_message;
  final String? provider_reference;
  final String? reconciliation_status;
  final bool? updated;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (delivery_stage != null) 'delivery_stage': delivery_stage,
        if (external_status != null) 'external_status': external_status,
        if (provider_message != null) 'provider_message': provider_message,
        if (provider_reference != null) 'provider_reference': provider_reference,
        if (reconciliation_status != null) 'reconciliation_status': reconciliation_status,
        if (updated != null) 'updated': updated,
      };
}

class NotificationRetryRequest {
  const NotificationRetryRequest({this.channel, this.provider_reference});

  factory NotificationRetryRequest.fromJson(Map<String, dynamic> json) => NotificationRetryRequest(
        channel: json['channel'] as String?,
        provider_reference: json['provider_reference'] as String?,
      );

  final String? channel;
  final String? provider_reference;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (channel != null) 'channel': channel,
        if (provider_reference != null) 'provider_reference': provider_reference,
      };
}

class NotificationRetryResponse {
  const NotificationRetryResponse({this.dispatch, this.source_provider_reference});

  factory NotificationRetryResponse.fromJson(Map<String, dynamic> json) => NotificationRetryResponse(
        dispatch: json['dispatch'] == null ? null : NotificationDispatchResponse.fromJson(json['dispatch'] as Map<String, dynamic>),
        source_provider_reference: json['source_provider_reference'] as String?,
      );

  final NotificationDispatchResponse? dispatch;
  final String? source_provider_reference;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (dispatch != null) 'dispatch': dispatch!.toJson(),
        if (source_provider_reference != null) 'source_provider_reference': source_provider_reference,
      };
}

class NotificationTestRequest {
  const NotificationTestRequest({this.body, this.channels, this.recipient, this.subject});

  factory NotificationTestRequest.fromJson(Map<String, dynamic> json) => NotificationTestRequest(
        body: json['body'] as String?,
        channels: (json['channels'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        recipient: json['recipient'] as String?,
        subject: json['subject'] as String?,
      );

  final String? body;
  final List<String>? channels;
  final String? recipient;
  final String? subject;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (body != null) 'body': body,
        if (channels != null) 'channels': channels,
        if (recipient != null) 'recipient': recipient,
        if (subject != null) 'subject': subject,
      };
}

class NotificationTestResponse {
  const NotificationTestResponse({this.results});

  factory NotificationTestResponse.fromJson(Map<String, dynamic> json) => NotificationTestResponse(
        results: (json['results'] as List<dynamic>?)?.map((dynamic item) => NotificationDispatchResponse.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final List<NotificationDispatchResponse>? results;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (results != null) 'results': results!.map((item) => item.toJson()).toList(),
      };
}

class OperationFailureCreate {
  const OperationFailureCreate({this.method, this.path, this.status_code});

  factory OperationFailureCreate.fromJson(Map<String, dynamic> json) => OperationFailureCreate(
        method: json['method'] as String?,
        path: json['path'] as String?,
        status_code: json['status_code'] as int?,
      );

  final String? method;
  final String? path;
  final int? status_code;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (method != null) 'method': method,
        if (path != null) 'path': path,
        if (status_code != null) 'status_code': status_code,
      };
}

typedef PaymentMethod = String;

class PaymentRecordCreate {
  const PaymentRecordCreate({this.amount, this.contribution_record_id, this.currency, this.paid_at, this.payment_method, this.reference});

  factory PaymentRecordCreate.fromJson(Map<String, dynamic> json) => PaymentRecordCreate(
        amount: json['amount'],
        contribution_record_id: json['contribution_record_id'] as String?,
        currency: json['currency'] as String?,
        paid_at: json['paid_at'] as String?,
        payment_method: json['payment_method'] as String?,
        reference: json['reference'] as String?,
      );

  final dynamic amount;
  final String? contribution_record_id;
  final String? currency;
  final String? paid_at;
  final PaymentMethod? payment_method;
  final String? reference;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (contribution_record_id != null) 'contribution_record_id': contribution_record_id,
        if (currency != null) 'currency': currency,
        if (paid_at != null) 'paid_at': paid_at,
        if (payment_method != null) 'payment_method': payment_method,
        if (reference != null) 'reference': reference,
      };
}

class PaymentRecordResponse {
  const PaymentRecordResponse({this.amount, this.contribution_record_id, this.created_at, this.currency, this.id, this.paid_at, this.payment_method, this.recorded_by, this.reference, this.tenant_id});

  factory PaymentRecordResponse.fromJson(Map<String, dynamic> json) => PaymentRecordResponse(
        amount: json['amount'] as String?,
        contribution_record_id: json['contribution_record_id'] as String?,
        created_at: json['created_at'] as String?,
        currency: json['currency'] as String?,
        id: json['id'] as String?,
        paid_at: json['paid_at'] as String?,
        payment_method: json['payment_method'] as String?,
        recorded_by: json['recorded_by'] as String?,
        reference: json['reference'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final String? amount;
  final String? contribution_record_id;
  final String? created_at;
  final String? currency;
  final String? id;
  final String? paid_at;
  final String? payment_method;
  final String? recorded_by;
  final String? reference;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (amount != null) 'amount': amount,
        if (contribution_record_id != null) 'contribution_record_id': contribution_record_id,
        if (created_at != null) 'created_at': created_at,
        if (currency != null) 'currency': currency,
        if (id != null) 'id': id,
        if (paid_at != null) 'paid_at': paid_at,
        if (payment_method != null) 'payment_method': payment_method,
        if (recorded_by != null) 'recorded_by': recorded_by,
        if (reference != null) 'reference': reference,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class PolicyCategoryResponse {
  const PolicyCategoryResponse({this.categories});

  factory PolicyCategoryResponse.fromJson(Map<String, dynamic> json) => PolicyCategoryResponse(
        categories: (json['categories'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
      );

  final List<String>? categories;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (categories != null) 'categories': categories,
      };
}

class PolicyRecordCreate {
  const PolicyRecordCreate({this.category, this.description, this.document_id, this.status, this.title});

  factory PolicyRecordCreate.fromJson(Map<String, dynamic> json) => PolicyRecordCreate(
        category: json['category'] as String?,
        description: json['description'] as String?,
        document_id: json['document_id'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
      );

  final String? category;
  final String? description;
  final String? document_id;
  final PolicyStatus? status;
  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (category != null) 'category': category,
        if (description != null) 'description': description,
        if (document_id != null) 'document_id': document_id,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
      };
}

class PolicyRecordResponse {
  const PolicyRecordResponse({this.category, this.created_at, this.created_by, this.description, this.document_id, this.document_title, this.id, this.status, this.tenant_id, this.title, this.updated_at});

  factory PolicyRecordResponse.fromJson(Map<String, dynamic> json) => PolicyRecordResponse(
        category: json['category'] as String?,
        created_at: json['created_at'] as String?,
        created_by: json['created_by'] as String?,
        description: json['description'] as String?,
        document_id: json['document_id'] as String?,
        document_title: json['document_title'] as String?,
        id: json['id'] as String?,
        status: json['status'] as String?,
        tenant_id: json['tenant_id'] as String?,
        title: json['title'] as String?,
        updated_at: json['updated_at'] as String?,
      );

  final String? category;
  final String? created_at;
  final String? created_by;
  final String? description;
  final String? document_id;
  final String? document_title;
  final String? id;
  final String? status;
  final String? tenant_id;
  final String? title;
  final String? updated_at;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (category != null) 'category': category,
        if (created_at != null) 'created_at': created_at,
        if (created_by != null) 'created_by': created_by,
        if (description != null) 'description': description,
        if (document_id != null) 'document_id': document_id,
        if (document_title != null) 'document_title': document_title,
        if (id != null) 'id': id,
        if (status != null) 'status': status,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (title != null) 'title': title,
        if (updated_at != null) 'updated_at': updated_at,
      };
}

class PolicyRecordUpdate {
  const PolicyRecordUpdate({this.category, this.description, this.document_id, this.status, this.title});

  factory PolicyRecordUpdate.fromJson(Map<String, dynamic> json) => PolicyRecordUpdate(
        category: json['category'] as String?,
        description: json['description'] as String?,
        document_id: json['document_id'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
      );

  final String? category;
  final String? description;
  final String? document_id;
  final PolicyStatus? status;
  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (category != null) 'category': category,
        if (description != null) 'description': description,
        if (document_id != null) 'document_id': document_id,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
      };
}

typedef PolicyStatus = String;

class PushConfigurationResponse {
  const PushConfigurationResponse({this.enabled, this.public_key, this.reason});

  factory PushConfigurationResponse.fromJson(Map<String, dynamic> json) => PushConfigurationResponse(
        enabled: json['enabled'] as bool?,
        public_key: json['public_key'] as String?,
        reason: json['reason'] as String?,
      );

  final bool? enabled;
  final String? public_key;
  final String? reason;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (enabled != null) 'enabled': enabled,
        if (public_key != null) 'public_key': public_key,
        if (reason != null) 'reason': reason,
      };
}

class PushSubscriptionRequest {
  const PushSubscriptionRequest({this.auth, this.browser, this.device_metadata, this.endpoint, this.installation_id, this.p256dh, this.platform});

  factory PushSubscriptionRequest.fromJson(Map<String, dynamic> json) => PushSubscriptionRequest(
        auth: json['auth'] as String?,
        browser: json['browser'] as String?,
        device_metadata: json['device_metadata'] as Map<String, dynamic>?,
        endpoint: json['endpoint'] as String?,
        installation_id: json['installation_id'] as String?,
        p256dh: json['p256dh'] as String?,
        platform: json['platform'] as String?,
      );

  final String? auth;
  final String? browser;
  final Map<String, dynamic>? device_metadata;
  final String? endpoint;
  final String? installation_id;
  final String? p256dh;
  final String? platform;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (auth != null) 'auth': auth,
        if (browser != null) 'browser': browser,
        if (device_metadata != null) 'device_metadata': device_metadata,
        if (endpoint != null) 'endpoint': endpoint,
        if (installation_id != null) 'installation_id': installation_id,
        if (p256dh != null) 'p256dh': p256dh,
        if (platform != null) 'platform': platform,
      };
}

class RecoveryEvidenceConfig {
  const RecoveryEvidenceConfig({this.alert_contacts_configured, this.alert_posture, this.backup_retention_days, this.last_backup_at, this.last_backup_reference, this.last_backup_status, this.last_restore_drill_at, this.last_restore_drill_status, this.notes});

  factory RecoveryEvidenceConfig.fromJson(Map<String, dynamic> json) => RecoveryEvidenceConfig(
        alert_contacts_configured: json['alert_contacts_configured'] as bool?,
        alert_posture: json['alert_posture'] as String?,
        backup_retention_days: json['backup_retention_days'] as int?,
        last_backup_at: json['last_backup_at'] as String?,
        last_backup_reference: json['last_backup_reference'] as String?,
        last_backup_status: json['last_backup_status'] as String?,
        last_restore_drill_at: json['last_restore_drill_at'] as String?,
        last_restore_drill_status: json['last_restore_drill_status'] as String?,
        notes: json['notes'] as String?,
      );

  final bool? alert_contacts_configured;
  final String? alert_posture;
  final int? backup_retention_days;
  final String? last_backup_at;
  final String? last_backup_reference;
  final String? last_backup_status;
  final String? last_restore_drill_at;
  final String? last_restore_drill_status;
  final String? notes;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (alert_contacts_configured != null) 'alert_contacts_configured': alert_contacts_configured,
        if (alert_posture != null) 'alert_posture': alert_posture,
        if (backup_retention_days != null) 'backup_retention_days': backup_retention_days,
        if (last_backup_at != null) 'last_backup_at': last_backup_at,
        if (last_backup_reference != null) 'last_backup_reference': last_backup_reference,
        if (last_backup_status != null) 'last_backup_status': last_backup_status,
        if (last_restore_drill_at != null) 'last_restore_drill_at': last_restore_drill_at,
        if (last_restore_drill_status != null) 'last_restore_drill_status': last_restore_drill_status,
        if (notes != null) 'notes': notes,
      };
}

class RecoveryEvidenceResponse {
  const RecoveryEvidenceResponse({this.alert_contacts_configured, this.alert_is_healthy, this.alert_posture, this.backup_is_stale, this.backup_retention_days, this.last_backup_at, this.last_backup_reference, this.last_backup_status, this.last_restore_drill_at, this.last_restore_drill_status, this.notes, this.overall_status, this.restore_drill_is_stale, this.status_message});

  factory RecoveryEvidenceResponse.fromJson(Map<String, dynamic> json) => RecoveryEvidenceResponse(
        alert_contacts_configured: json['alert_contacts_configured'] as bool?,
        alert_is_healthy: json['alert_is_healthy'] as bool?,
        alert_posture: json['alert_posture'] as String?,
        backup_is_stale: json['backup_is_stale'] as bool?,
        backup_retention_days: json['backup_retention_days'] as int?,
        last_backup_at: json['last_backup_at'] as String?,
        last_backup_reference: json['last_backup_reference'] as String?,
        last_backup_status: json['last_backup_status'] as String?,
        last_restore_drill_at: json['last_restore_drill_at'] as String?,
        last_restore_drill_status: json['last_restore_drill_status'] as String?,
        notes: json['notes'] as String?,
        overall_status: json['overall_status'] as String?,
        restore_drill_is_stale: json['restore_drill_is_stale'] as bool?,
        status_message: json['status_message'] as String?,
      );

  final bool? alert_contacts_configured;
  final bool? alert_is_healthy;
  final String? alert_posture;
  final bool? backup_is_stale;
  final int? backup_retention_days;
  final String? last_backup_at;
  final String? last_backup_reference;
  final String? last_backup_status;
  final String? last_restore_drill_at;
  final String? last_restore_drill_status;
  final String? notes;
  final String? overall_status;
  final bool? restore_drill_is_stale;
  final String? status_message;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (alert_contacts_configured != null) 'alert_contacts_configured': alert_contacts_configured,
        if (alert_is_healthy != null) 'alert_is_healthy': alert_is_healthy,
        if (alert_posture != null) 'alert_posture': alert_posture,
        if (backup_is_stale != null) 'backup_is_stale': backup_is_stale,
        if (backup_retention_days != null) 'backup_retention_days': backup_retention_days,
        if (last_backup_at != null) 'last_backup_at': last_backup_at,
        if (last_backup_reference != null) 'last_backup_reference': last_backup_reference,
        if (last_backup_status != null) 'last_backup_status': last_backup_status,
        if (last_restore_drill_at != null) 'last_restore_drill_at': last_restore_drill_at,
        if (last_restore_drill_status != null) 'last_restore_drill_status': last_restore_drill_status,
        if (notes != null) 'notes': notes,
        if (overall_status != null) 'overall_status': overall_status,
        if (restore_drill_is_stale != null) 'restore_drill_is_stale': restore_drill_is_stale,
        if (status_message != null) 'status_message': status_message,
      };
}

class RefreshTokenRequest {
  const RefreshTokenRequest({this.refresh_token});

  factory RefreshTokenRequest.fromJson(Map<String, dynamic> json) => RefreshTokenRequest(
        refresh_token: json['refresh_token'] as String?,
      );

  final String? refresh_token;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (refresh_token != null) 'refresh_token': refresh_token,
      };
}

class RefreshTokenResponse {
  const RefreshTokenResponse({this.access_token, this.expires_in, this.token_type});

  factory RefreshTokenResponse.fromJson(Map<String, dynamic> json) => RefreshTokenResponse(
        access_token: json['access_token'] as String?,
        expires_in: json['expires_in'] as int?,
        token_type: json['token_type'] as String?,
      );

  final String? access_token;
  final int? expires_in;
  final String? token_type;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_token != null) 'access_token': access_token,
        if (expires_in != null) 'expires_in': expires_in,
        if (token_type != null) 'token_type': token_type,
      };
}

class RegisteredModuleResponse {
  const RegisteredModuleResponse({this.capabilities, this.depends_on, this.description, this.domain_event_types, this.enabled, this.key, this.name, this.navigation});

  factory RegisteredModuleResponse.fromJson(Map<String, dynamic> json) => RegisteredModuleResponse(
        capabilities: (json['capabilities'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        depends_on: (json['depends_on'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        description: json['description'] as String?,
        domain_event_types: (json['domain_event_types'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        enabled: json['enabled'] as bool?,
        key: json['key'] as String?,
        name: json['name'] as String?,
        navigation: (json['navigation'] as List<dynamic>?)?.map((dynamic item) => ModuleNavigationEntryResponse.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final List<String>? capabilities;
  final List<String>? depends_on;
  final String? description;
  final List<String>? domain_event_types;
  final bool? enabled;
  final String? key;
  final String? name;
  final List<ModuleNavigationEntryResponse>? navigation;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (capabilities != null) 'capabilities': capabilities,
        if (depends_on != null) 'depends_on': depends_on,
        if (description != null) 'description': description,
        if (domain_event_types != null) 'domain_event_types': domain_event_types,
        if (enabled != null) 'enabled': enabled,
        if (key != null) 'key': key,
        if (name != null) 'name': name,
        if (navigation != null) 'navigation': navigation!.map((item) => item.toJson()).toList(),
      };
}

class RegisteredModulesResponse {
  const RegisteredModulesResponse({this.modules});

  factory RegisteredModulesResponse.fromJson(Map<String, dynamic> json) => RegisteredModulesResponse(
        modules: (json['modules'] as List<dynamic>?)?.map((dynamic item) => RegisteredModuleResponse.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final List<RegisteredModuleResponse>? modules;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (modules != null) 'modules': modules!.map((item) => item.toJson()).toList(),
      };
}

typedef ReminderDeliveryStatus = String;

class ResetPasswordRequest {
  const ResetPasswordRequest({this.new_password, this.token});

  factory ResetPasswordRequest.fromJson(Map<String, dynamic> json) => ResetPasswordRequest(
        new_password: json['new_password'] as String?,
        token: json['token'] as String?,
      );

  final String? new_password;
  final String? token;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (new_password != null) 'new_password': new_password,
        if (token != null) 'token': token,
      };
}

class ResetPasswordResponse {
  const ResetPasswordResponse({this.message});

  factory ResetPasswordResponse.fromJson(Map<String, dynamic> json) => ResetPasswordResponse(
        message: json['message'] as String?,
      );

  final String? message;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (message != null) 'message': message,
      };
}

class RestoreImportResponse {
  const RestoreImportResponse({this.guidance, this.run, this.verified});

  factory RestoreImportResponse.fromJson(Map<String, dynamic> json) => RestoreImportResponse(
        guidance: json['guidance'] as String?,
        run: json['run'] == null ? null : BackupRunResponse.fromJson(json['run'] as Map<String, dynamic>),
        verified: json['verified'] as bool?,
      );

  final String? guidance;
  final BackupRunResponse? run;
  final bool? verified;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (guidance != null) 'guidance': guidance,
        if (run != null) 'run': run!.toJson(),
        if (verified != null) 'verified': verified,
      };
}

class RoleBundleCreate {
  const RoleBundleCreate({this.capabilities, this.code, this.description, this.name});

  factory RoleBundleCreate.fromJson(Map<String, dynamic> json) => RoleBundleCreate(
        capabilities: (json['capabilities'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        code: json['code'] as String?,
        description: json['description'] as String?,
        name: json['name'] as String?,
      );

  final List<String>? capabilities;
  final String? code;
  final String? description;
  final String? name;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (capabilities != null) 'capabilities': capabilities,
        if (code != null) 'code': code,
        if (description != null) 'description': description,
        if (name != null) 'name': name,
      };
}

class RoleResponse {
  const RoleResponse({this.capabilities, this.code, this.description, this.id, this.is_canonical, this.is_system_role, this.name, this.tenant_id});

  factory RoleResponse.fromJson(Map<String, dynamic> json) => RoleResponse(
        capabilities: (json['capabilities'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        code: json['code'] as String?,
        description: json['description'] as String?,
        id: json['id'] as String?,
        is_canonical: json['is_canonical'] as bool?,
        is_system_role: json['is_system_role'] as bool?,
        name: json['name'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final List<String>? capabilities;
  final String? code;
  final String? description;
  final String? id;
  final bool? is_canonical;
  final bool? is_system_role;
  final String? name;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (capabilities != null) 'capabilities': capabilities,
        if (code != null) 'code': code,
        if (description != null) 'description': description,
        if (id != null) 'id': id,
        if (is_canonical != null) 'is_canonical': is_canonical,
        if (is_system_role != null) 'is_system_role': is_system_role,
        if (name != null) 'name': name,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class SearchResponse {
  const SearchResponse({this.query, this.results});

  factory SearchResponse.fromJson(Map<String, dynamic> json) => SearchResponse(
        query: json['query'] as String?,
        results: (json['results'] as List<dynamic>?)?.map((dynamic item) => SearchResult.fromJson(item as Map<String, dynamic>)).toList(),
      );

  final String? query;
  final List<SearchResult>? results;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (query != null) 'query': query,
        if (results != null) 'results': results!.map((item) => item.toJson()).toList(),
      };
}

class SearchResult {
  const SearchResult({this.id, this.score, this.subtitle, this.target_path, this.title, this.type, this.type_key});

  factory SearchResult.fromJson(Map<String, dynamic> json) => SearchResult(
        id: json['id'] as String?,
        score: json['score'] as int?,
        subtitle: json['subtitle'] as String?,
        target_path: json['target_path'] as String?,
        title: json['title'] as String?,
        type: json['type'] as String?,
        type_key: json['type_key'] as String?,
      );

  final String? id;
  final int? score;
  final String? subtitle;
  final String? target_path;
  final String? title;
  final String? type;
  final String? type_key;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (id != null) 'id': id,
        if (score != null) 'score': score,
        if (subtitle != null) 'subtitle': subtitle,
        if (target_path != null) 'target_path': target_path,
        if (title != null) 'title': title,
        if (type != null) 'type': type,
        if (type_key != null) 'type_key': type_key,
      };
}

class SecurityEventResponse {
  const SecurityEventResponse({this.action, this.actor_user_id, this.created_at, this.details, this.entity_id, this.entity_type, this.id});

  factory SecurityEventResponse.fromJson(Map<String, dynamic> json) => SecurityEventResponse(
        action: json['action'] as String?,
        actor_user_id: json['actor_user_id'] as String?,
        created_at: json['created_at'] as String?,
        details: json['details'] as Map<String, dynamic>?,
        entity_id: json['entity_id'] as String?,
        entity_type: json['entity_type'] as String?,
        id: json['id'] as String?,
      );

  final String? action;
  final String? actor_user_id;
  final String? created_at;
  final Map<String, dynamic>? details;
  final String? entity_id;
  final String? entity_type;
  final String? id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (action != null) 'action': action,
        if (actor_user_id != null) 'actor_user_id': actor_user_id,
        if (created_at != null) 'created_at': created_at,
        if (details != null) 'details': details,
        if (entity_id != null) 'entity_id': entity_id,
        if (entity_type != null) 'entity_type': entity_type,
        if (id != null) 'id': id,
      };
}

class SessionActionResponse {
  const SessionActionResponse({this.message, this.revoked_session_count});

  factory SessionActionResponse.fromJson(Map<String, dynamic> json) => SessionActionResponse(
        message: json['message'] as String?,
        revoked_session_count: json['revoked_session_count'] as int?,
      );

  final String? message;
  final int? revoked_session_count;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (message != null) 'message': message,
        if (revoked_session_count != null) 'revoked_session_count': revoked_session_count,
      };
}

class SwitchTenantRequest {
  const SwitchTenantRequest({this.tenant_id});

  factory SwitchTenantRequest.fromJson(Map<String, dynamic> json) => SwitchTenantRequest(
        tenant_id: json['tenant_id'] as String?,
      );

  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class SwitchTenantResponse {
  const SwitchTenantResponse({this.access_token, this.expires_in, this.memberships, this.tenant_id, this.token_type, this.user_id});

  factory SwitchTenantResponse.fromJson(Map<String, dynamic> json) => SwitchTenantResponse(
        access_token: json['access_token'] as String?,
        expires_in: json['expires_in'] as int?,
        memberships: (json['memberships'] as List<dynamic>?)?.map((dynamic item) => TenantMembershipResponse.fromJson(item as Map<String, dynamic>)).toList(),
        tenant_id: json['tenant_id'] as String?,
        token_type: json['token_type'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? access_token;
  final int? expires_in;
  final List<TenantMembershipResponse>? memberships;
  final String? tenant_id;
  final String? token_type;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_token != null) 'access_token': access_token,
        if (expires_in != null) 'expires_in': expires_in,
        if (memberships != null) 'memberships': memberships!.map((item) => item.toJson()).toList(),
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (token_type != null) 'token_type': token_type,
        if (user_id != null) 'user_id': user_id,
      };
}

class TenantBranding {
  const TenantBranding({this.background_color, this.custom_domain, this.display_name, this.favicon_url, this.icon_192_url, this.icon_512_url, this.legal_name, this.logo_dark_url, this.logo_url, this.maskable_icon_url, this.notification_name, this.primary_color, this.secondary_color, this.short_name, this.support_email, this.support_name, this.theme_color});

  factory TenantBranding.fromJson(Map<String, dynamic> json) => TenantBranding(
        background_color: json['background_color'] as String?,
        custom_domain: json['custom_domain'] as String?,
        display_name: json['display_name'] as String?,
        favicon_url: json['favicon_url'] as String?,
        icon_192_url: json['icon_192_url'] as String?,
        icon_512_url: json['icon_512_url'] as String?,
        legal_name: json['legal_name'] as String?,
        logo_dark_url: json['logo_dark_url'] as String?,
        logo_url: json['logo_url'] as String?,
        maskable_icon_url: json['maskable_icon_url'] as String?,
        notification_name: json['notification_name'] as String?,
        primary_color: json['primary_color'] as String?,
        secondary_color: json['secondary_color'] as String?,
        short_name: json['short_name'] as String?,
        support_email: json['support_email'] as String?,
        support_name: json['support_name'] as String?,
        theme_color: json['theme_color'] as String?,
      );

  final String? background_color;
  final String? custom_domain;
  final String? display_name;
  final String? favicon_url;
  final String? icon_192_url;
  final String? icon_512_url;
  final String? legal_name;
  final String? logo_dark_url;
  final String? logo_url;
  final String? maskable_icon_url;
  final String? notification_name;
  final String? primary_color;
  final String? secondary_color;
  final String? short_name;
  final String? support_email;
  final String? support_name;
  final String? theme_color;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (background_color != null) 'background_color': background_color,
        if (custom_domain != null) 'custom_domain': custom_domain,
        if (display_name != null) 'display_name': display_name,
        if (favicon_url != null) 'favicon_url': favicon_url,
        if (icon_192_url != null) 'icon_192_url': icon_192_url,
        if (icon_512_url != null) 'icon_512_url': icon_512_url,
        if (legal_name != null) 'legal_name': legal_name,
        if (logo_dark_url != null) 'logo_dark_url': logo_dark_url,
        if (logo_url != null) 'logo_url': logo_url,
        if (maskable_icon_url != null) 'maskable_icon_url': maskable_icon_url,
        if (notification_name != null) 'notification_name': notification_name,
        if (primary_color != null) 'primary_color': primary_color,
        if (secondary_color != null) 'secondary_color': secondary_color,
        if (short_name != null) 'short_name': short_name,
        if (support_email != null) 'support_email': support_email,
        if (support_name != null) 'support_name': support_name,
        if (theme_color != null) 'theme_color': theme_color,
      };
}

class TenantMembershipResponse {
  const TenantMembershipResponse({this.branding, this.capabilities, this.default_language, this.modules, this.name, this.profile_type, this.roles, this.slug, this.tenant_id});

  factory TenantMembershipResponse.fromJson(Map<String, dynamic> json) => TenantMembershipResponse(
        branding: json['branding'] == null ? null : TenantBranding.fromJson(json['branding'] as Map<String, dynamic>),
        capabilities: (json['capabilities'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        default_language: json['default_language'] as String?,
        modules: json['modules'] == null ? null : ModuleToggles.fromJson(json['modules'] as Map<String, dynamic>),
        name: json['name'] as String?,
        profile_type: json['profile_type'] as String?,
        roles: (json['roles'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        slug: json['slug'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final TenantBranding? branding;
  final List<String>? capabilities;
  final String? default_language;
  final ModuleToggles? modules;
  final String? name;
  final String? profile_type;
  final List<String>? roles;
  final String? slug;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (branding != null) 'branding': branding!.toJson(),
        if (capabilities != null) 'capabilities': capabilities,
        if (default_language != null) 'default_language': default_language,
        if (modules != null) 'modules': modules!.toJson(),
        if (name != null) 'name': name,
        if (profile_type != null) 'profile_type': profile_type,
        if (roles != null) 'roles': roles,
        if (slug != null) 'slug': slug,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class TenantResponse {
  const TenantResponse({this.created_at, this.default_language, this.id, this.name, this.slug, this.status, this.type});

  factory TenantResponse.fromJson(Map<String, dynamic> json) => TenantResponse(
        created_at: json['created_at'] as String?,
        default_language: json['default_language'] as String?,
        id: json['id'] as String?,
        name: json['name'] as String?,
        slug: json['slug'] as String?,
        status: json['status'] as String?,
        type: json['type'] as String?,
      );

  final String? created_at;
  final String? default_language;
  final String? id;
  final String? name;
  final String? slug;
  final String? status;
  final String? type;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (created_at != null) 'created_at': created_at,
        if (default_language != null) 'default_language': default_language,
        if (id != null) 'id': id,
        if (name != null) 'name': name,
        if (slug != null) 'slug': slug,
        if (status != null) 'status': status,
        if (type != null) 'type': type,
      };
}

class TenantSettingsResponse {
  const TenantSettingsResponse({this.branding, this.default_language, this.modules, this.name, this.operations, this.slug, this.tenant_id, this.updated_at});

  factory TenantSettingsResponse.fromJson(Map<String, dynamic> json) => TenantSettingsResponse(
        branding: json['branding'] == null ? null : TenantBranding.fromJson(json['branding'] as Map<String, dynamic>),
        default_language: json['default_language'] as String?,
        modules: json['modules'] == null ? null : ModuleToggles.fromJson(json['modules'] as Map<String, dynamic>),
        name: json['name'] as String?,
        operations: json['operations'] == null ? null : RecoveryEvidenceResponse.fromJson(json['operations'] as Map<String, dynamic>),
        slug: json['slug'] as String?,
        tenant_id: json['tenant_id'] as String?,
        updated_at: json['updated_at'] as String?,
      );

  final TenantBranding? branding;
  final String? default_language;
  final ModuleToggles? modules;
  final String? name;
  final RecoveryEvidenceResponse? operations;
  final String? slug;
  final String? tenant_id;
  final String? updated_at;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (branding != null) 'branding': branding!.toJson(),
        if (default_language != null) 'default_language': default_language,
        if (modules != null) 'modules': modules!.toJson(),
        if (name != null) 'name': name,
        if (operations != null) 'operations': operations!.toJson(),
        if (slug != null) 'slug': slug,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (updated_at != null) 'updated_at': updated_at,
      };
}

class TenantSettingsUpdate {
  const TenantSettingsUpdate({this.branding, this.default_language, this.modules, this.name, this.operations});

  factory TenantSettingsUpdate.fromJson(Map<String, dynamic> json) => TenantSettingsUpdate(
        branding: json['branding'] == null ? null : TenantBranding.fromJson(json['branding'] as Map<String, dynamic>),
        default_language: json['default_language'] as String?,
        modules: json['modules'] == null ? null : ModuleToggles.fromJson(json['modules'] as Map<String, dynamic>),
        name: json['name'] as String?,
        operations: json['operations'] == null ? null : RecoveryEvidenceConfig.fromJson(json['operations'] as Map<String, dynamic>),
      );

  final TenantBranding? branding;
  final String? default_language;
  final ModuleToggles? modules;
  final String? name;
  final RecoveryEvidenceConfig? operations;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (branding != null) 'branding': branding!.toJson(),
        if (default_language != null) 'default_language': default_language,
        if (modules != null) 'modules': modules!.toJson(),
        if (name != null) 'name': name,
        if (operations != null) 'operations': operations!.toJson(),
      };
}

class TokenResponse {
  const TokenResponse({this.access_token, this.expires_in, this.password_change_required, this.tenant_id, this.token_type, this.user_id});

  factory TokenResponse.fromJson(Map<String, dynamic> json) => TokenResponse(
        access_token: json['access_token'] as String?,
        expires_in: json['expires_in'] as int?,
        password_change_required: json['password_change_required'] as bool?,
        tenant_id: json['tenant_id'] as String?,
        token_type: json['token_type'] as String?,
        user_id: json['user_id'] as String?,
      );

  final String? access_token;
  final int? expires_in;
  final bool? password_change_required;
  final String? tenant_id;
  final String? token_type;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_token != null) 'access_token': access_token,
        if (expires_in != null) 'expires_in': expires_in,
        if (password_change_required != null) 'password_change_required': password_change_required,
        if (tenant_id != null) 'tenant_id': tenant_id,
        if (token_type != null) 'token_type': token_type,
        if (user_id != null) 'user_id': user_id,
      };
}

class UnreachableNotificationRecipient {
  const UnreachableNotificationRecipient({this.display_name, this.last_notification_at, this.pending_notifications, this.user_id});

  factory UnreachableNotificationRecipient.fromJson(Map<String, dynamic> json) => UnreachableNotificationRecipient(
        display_name: json['display_name'] as String?,
        last_notification_at: json['last_notification_at'] as String?,
        pending_notifications: json['pending_notifications'] as int?,
        user_id: json['user_id'] as String?,
      );

  final String? display_name;
  final String? last_notification_at;
  final int? pending_notifications;
  final String? user_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (display_name != null) 'display_name': display_name,
        if (last_notification_at != null) 'last_notification_at': last_notification_at,
        if (pending_notifications != null) 'pending_notifications': pending_notifications,
        if (user_id != null) 'user_id': user_id,
      };
}

class UpdateLanguagePreferenceRequest {
  const UpdateLanguagePreferenceRequest({this.preferred_language});

  factory UpdateLanguagePreferenceRequest.fromJson(Map<String, dynamic> json) => UpdateLanguagePreferenceRequest(
        preferred_language: json['preferred_language'] as String?,
      );

  final String? preferred_language;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (preferred_language != null) 'preferred_language': preferred_language,
      };
}

class UploadDocumentResponse {
  const UploadDocumentResponse({this.access_scope, this.allowed_role_ids, this.created_at, this.current_version, this.description, this.duplicate_of_document_id, this.id, this.ingestion_job_id, this.language, this.owner_user_id, this.source_type, this.status, this.title});

  factory UploadDocumentResponse.fromJson(Map<String, dynamic> json) => UploadDocumentResponse(
        access_scope: json['access_scope'] as String?,
        allowed_role_ids: (json['allowed_role_ids'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        created_at: json['created_at'] as String?,
        current_version: json['current_version'] == null ? null : DocumentVersionResponse.fromJson(json['current_version'] as Map<String, dynamic>),
        description: json['description'] as String?,
        duplicate_of_document_id: json['duplicate_of_document_id'] as String?,
        id: json['id'] as String?,
        ingestion_job_id: json['ingestion_job_id'] as String?,
        language: json['language'] as String?,
        owner_user_id: json['owner_user_id'] as String?,
        source_type: json['source_type'] as String?,
        status: json['status'] as String?,
        title: json['title'] as String?,
      );

  final String? access_scope;
  final List<String>? allowed_role_ids;
  final String? created_at;
  final DocumentVersionResponse? current_version;
  final String? description;
  final String? duplicate_of_document_id;
  final String? id;
  final String? ingestion_job_id;
  final String? language;
  final String? owner_user_id;
  final String? source_type;
  final String? status;
  final String? title;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (access_scope != null) 'access_scope': access_scope,
        if (allowed_role_ids != null) 'allowed_role_ids': allowed_role_ids,
        if (created_at != null) 'created_at': created_at,
        if (current_version != null) 'current_version': current_version!.toJson(),
        if (description != null) 'description': description,
        if (duplicate_of_document_id != null) 'duplicate_of_document_id': duplicate_of_document_id,
        if (id != null) 'id': id,
        if (ingestion_job_id != null) 'ingestion_job_id': ingestion_job_id,
        if (language != null) 'language': language,
        if (owner_user_id != null) 'owner_user_id': owner_user_id,
        if (source_type != null) 'source_type': source_type,
        if (status != null) 'status': status,
        if (title != null) 'title': title,
      };
}

class UserWithMembershipsResponse {
  const UserWithMembershipsResponse({this.capabilities, this.display_name, this.email, this.id, this.last_login_at, this.memberships, this.password_change_required, this.preferred_language, this.roles, this.status, this.tenant_id});

  factory UserWithMembershipsResponse.fromJson(Map<String, dynamic> json) => UserWithMembershipsResponse(
        capabilities: (json['capabilities'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        display_name: json['display_name'] as String?,
        email: json['email'] as String?,
        id: json['id'] as String?,
        last_login_at: json['last_login_at'] as String?,
        memberships: (json['memberships'] as List<dynamic>?)?.map((dynamic item) => TenantMembershipResponse.fromJson(item as Map<String, dynamic>)).toList(),
        password_change_required: json['password_change_required'] as bool?,
        preferred_language: json['preferred_language'] as String?,
        roles: (json['roles'] as List<dynamic>?)?.map((dynamic item) => item as String).toList(),
        status: json['status'] as String?,
        tenant_id: json['tenant_id'] as String?,
      );

  final List<String>? capabilities;
  final String? display_name;
  final String? email;
  final String? id;
  final String? last_login_at;
  final List<TenantMembershipResponse>? memberships;
  final bool? password_change_required;
  final String? preferred_language;
  final List<String>? roles;
  final String? status;
  final String? tenant_id;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (capabilities != null) 'capabilities': capabilities,
        if (display_name != null) 'display_name': display_name,
        if (email != null) 'email': email,
        if (id != null) 'id': id,
        if (last_login_at != null) 'last_login_at': last_login_at,
        if (memberships != null) 'memberships': memberships!.map((item) => item.toJson()).toList(),
        if (password_change_required != null) 'password_change_required': password_change_required,
        if (preferred_language != null) 'preferred_language': preferred_language,
        if (roles != null) 'roles': roles,
        if (status != null) 'status': status,
        if (tenant_id != null) 'tenant_id': tenant_id,
      };
}

class ValidationError {
  const ValidationError({this.ctx, this.input, this.loc, this.msg, this.type});

  factory ValidationError.fromJson(Map<String, dynamic> json) => ValidationError(
        ctx: json['ctx'] as Map<String, dynamic>?,
        input: json['input'],
        loc: (json['loc'] as List<dynamic>?)?.map((dynamic item) => item).toList(),
        msg: json['msg'] as String?,
        type: json['type'] as String?,
      );

  final Map<String, dynamic>? ctx;
  final dynamic input;
  final List<dynamic>? loc;
  final String? msg;
  final String? type;

  Map<String, dynamic> toJson() => <String, dynamic>{
        if (ctx != null) 'ctx': ctx,
        if (input != null) 'input': input,
        if (loc != null) 'loc': loc,
        if (msg != null) 'msg': msg,
        if (type != null) 'type': type,
      };
}

const Map<String, String> apiOperationIds = <String, String>{
  'GET /api/v1/admin/audit/events': 'list_audit_events_api_v1_admin_audit_events_get',
  'GET /api/v1/admin/audit/events/export': 'export_audit_events_api_v1_admin_audit_events_export_get',
  'GET /api/v1/admin/audit/operation-journal': 'list_operation_journal_api_v1_admin_audit_operation_journal_get',
  'POST /api/v1/admin/audit/operation-journal/failures': 'record_operation_failure_api_v1_admin_audit_operation_journal_failures_post',
  'GET /api/v1/admin/chat-queries': 'list_chat_queries_api_v1_admin_chat_queries_get',
  'GET /api/v1/admin/ingestion-jobs/health': 'ingestion_jobs_health_api_v1_admin_ingestion_jobs_health_get',
  'GET /api/v1/admin/module-has-data': 'check_module_has_data_api_v1_admin_module_has_data_get',
  'GET /api/v1/announcements/': 'list_all_announcements_api_v1_announcements__get',
  'POST /api/v1/announcements/': 'create_announcement_api_v1_announcements__post',
  'GET /api/v1/announcements/active': 'list_active_announcements_api_v1_announcements_active_get',
  'GET /api/v1/announcements/export': 'export_announcements_api_v1_announcements_export_get',
  'GET /api/v1/announcements/{announcement_id}': 'get_announcement_api_v1_announcements__announcement_id__get',
  'PATCH /api/v1/announcements/{announcement_id}': 'update_announcement_api_v1_announcements__announcement_id__patch',
  'DELETE /api/v1/announcements/{announcement_id}': 'delete_announcement_api_v1_announcements__announcement_id__delete',
  'GET /api/v1/attention': 'get_attention_overview_api_v1_attention_get',
  'POST /api/v1/auth/accept-invite': 'accept_invite_api_v1_auth_accept_invite_post',
  'POST /api/v1/auth/access-recovery/{user_id}': 'recover_member_access_api_v1_auth_access_recovery__user_id__post',
  'GET /api/v1/auth/admin/managed-users/{tenant_id}': 'list_managed_users_api_v1_auth_admin_managed_users__tenant_id__get',
  'POST /api/v1/auth/admin/managed-users/{user_id}/reactivate': 'reactivate_managed_user_api_v1_auth_admin_managed_users__user_id__reactivate_post',
  'POST /api/v1/auth/admin/managed-users/{user_id}/revoke-sessions': 'revoke_managed_user_sessions_api_v1_auth_admin_managed_users__user_id__revoke_sessions_post',
  'PUT /api/v1/auth/admin/managed-users/{user_id}/roles': 'update_managed_user_roles_api_v1_auth_admin_managed_users__user_id__roles_put',
  'POST /api/v1/auth/admin/managed-users/{user_id}/suspend': 'suspend_managed_user_api_v1_auth_admin_managed_users__user_id__suspend_post',
  'POST /api/v1/auth/change-initial-password': 'change_initial_password_api_v1_auth_change_initial_password_post',
  'POST /api/v1/auth/change-password': 'change_password_api_v1_auth_change_password_post',
  'POST /api/v1/auth/forgot-password': 'forgot_password_api_v1_auth_forgot_password_post',
  'DELETE /api/v1/auth/invitations/{invitation_id}': 'cancel_invitation_api_v1_auth_invitations__invitation_id__delete',
  'GET /api/v1/auth/invitations/{tenant_id}': 'list_invitations_api_v1_auth_invitations__tenant_id__get',
  'POST /api/v1/auth/invite': 'invite_user_api_v1_auth_invite_post',
  'POST /api/v1/auth/login': 'login_api_v1_auth_login_post',
  'GET /api/v1/auth/me': 'get_me_api_v1_auth_me_get',
  'PATCH /api/v1/auth/me/preferences/language': 'update_language_preference_api_v1_auth_me_preferences_language_patch',
  'DELETE /api/v1/auth/mfa': 'disable_mfa_api_v1_auth_mfa_delete',
  'POST /api/v1/auth/mfa/complete': 'mfa_complete_login_api_v1_auth_mfa_complete_post',
  'POST /api/v1/auth/mfa/enroll': 'enroll_mfa_api_v1_auth_mfa_enroll_post',
  'GET /api/v1/auth/mfa/status': 'get_mfa_status_api_v1_auth_mfa_status_get',
  'POST /api/v1/auth/mfa/verify': 'verify_mfa_api_v1_auth_mfa_verify_post',
  'GET /api/v1/auth/protected': 'protected_test_api_v1_auth_protected_get',
  'POST /api/v1/auth/refresh': 'refresh_token_api_v1_auth_refresh_post',
  'POST /api/v1/auth/reset-password': 'reset_password_api_v1_auth_reset_password_post',
  'GET /api/v1/auth/security-events': 'list_security_events_api_v1_auth_security_events_get',
  'GET /api/v1/auth/sessions': 'list_active_sessions_api_v1_auth_sessions_get',
  'POST /api/v1/auth/sessions/revoke-all': 'revoke_all_sessions_api_v1_auth_sessions_revoke_all_post',
  'POST /api/v1/auth/sessions/revoke-others': 'revoke_other_sessions_api_v1_auth_sessions_revoke_others_post',
  'DELETE /api/v1/auth/sessions/{session_id}': 'revoke_session_api_v1_auth_sessions__session_id__delete',
  'POST /api/v1/auth/switch-tenant': 'switch_tenant_api_v1_auth_switch_tenant_post',
  'GET /api/v1/chat/conversations': 'list_conversations_api_v1_chat_conversations_get',
  'POST /api/v1/chat/conversations': 'create_conversation_api_v1_chat_conversations_post',
  'GET /api/v1/chat/conversations/{conversation_id}': 'get_conversation_api_v1_chat_conversations__conversation_id__get',
  'PATCH /api/v1/chat/conversations/{conversation_id}': 'update_conversation_api_v1_chat_conversations__conversation_id__patch',
  'DELETE /api/v1/chat/conversations/{conversation_id}': 'delete_conversation_api_v1_chat_conversations__conversation_id__delete',
  'GET /api/v1/chat/domain-policy': 'get_chat_domain_policy_api_v1_chat_domain_policy_get',
  'POST /api/v1/chat/query': 'query_chat_api_v1_chat_query_post',
  'POST /api/v1/chat/query-stream': 'query_chat_stream_api_v1_chat_query_stream_post',
  'GET /api/v1/contributions/': 'list_contributions_api_v1_contributions__get',
  'POST /api/v1/contributions/': 'create_contribution_api_v1_contributions__post',
  'GET /api/v1/contributions/annual-budget': 'get_annual_budget_api_v1_contributions_annual_budget_get',
  'GET /api/v1/contributions/by-member/{profile_id}': 'list_member_contributions_api_v1_contributions_by_member__profile_id__get',
  'POST /api/v1/contributions/expenses': 'create_expense_api_v1_contributions_expenses_post',
  'GET /api/v1/contributions/export': 'export_contributions_api_v1_contributions_export_get',
  'POST /api/v1/contributions/import': 'import_contributions_api_v1_contributions_import_post',
  'GET /api/v1/contributions/payments': 'list_tenant_payments_api_v1_contributions_payments_get',
  'POST /api/v1/contributions/payments': 'record_payment_api_v1_contributions_payments_post',
  'GET /api/v1/contributions/receipt-declarations': 'list_receipt_declarations_api_v1_contributions_receipt_declarations_get',
  'POST /api/v1/contributions/receipt-declarations': 'create_receipt_declaration_api_v1_contributions_receipt_declarations_post',
  'GET /api/v1/contributions/receipt-declarations/me': 'list_member_receipt_declarations_api_v1_contributions_receipt_declarations_me_get',
  'GET /api/v1/contributions/receipt-declarations/member-options': 'list_receipt_declaration_member_options_api_v1_contributions_receipt_declarations_member_options_get',
  'GET /api/v1/contributions/receipt-declarations/mine': 'list_my_receipt_declarations_api_v1_contributions_receipt_declarations_mine_get',
  'PATCH /api/v1/contributions/receipt-declarations/{declaration_id}': 'update_receipt_declaration_api_v1_contributions_receipt_declarations__declaration_id__patch',
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/confirm-treasury-receipt': 'confirm_receipt_in_treasury_api_v1_contributions_receipt_declarations__declaration_id__confirm_treasury_receipt_post',
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/handover': 'report_receipt_handover_api_v1_contributions_receipt_declarations__declaration_id__handover_post',
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/handover-reminder': 'update_receipt_handover_reminder_api_v1_contributions_receipt_declarations__declaration_id__handover_reminder_post',
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/process': 'process_receipt_declaration_api_v1_contributions_receipt_declarations__declaration_id__process_post',
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/submit': 'submit_receipt_declaration_api_v1_contributions_receipt_declarations__declaration_id__submit_post',
  'GET /api/v1/contributions/reminders': 'list_contribution_reminders_api_v1_contributions_reminders_get',
  'POST /api/v1/contributions/reminders/send': 'send_batch_contribution_reminders_api_v1_contributions_reminders_send_post',
  'GET /api/v1/contributions/report/export': 'export_finance_report_api_v1_contributions_report_export_get',
  'GET /api/v1/contributions/report/export/{export_format}': 'export_member_finance_report_api_v1_contributions_report_export__export_format__get',
  'GET /api/v1/contributions/summary': 'get_contribution_summary_api_v1_contributions_summary_get',
  'GET /api/v1/contributions/{contribution_id}': 'get_contribution_api_v1_contributions__contribution_id__get',
  'PATCH /api/v1/contributions/{contribution_id}': 'update_contribution_api_v1_contributions__contribution_id__patch',
  'DELETE /api/v1/contributions/{contribution_id}': 'delete_contribution_api_v1_contributions__contribution_id__delete',
  'GET /api/v1/contributions/{contribution_id}/payments': 'list_payments_api_v1_contributions__contribution_id__payments_get',
  'POST /api/v1/contributions/{contribution_id}/reminders/send': 'send_contribution_reminder_api_v1_contributions__contribution_id__reminders_send_post',
  'GET /api/v1/disciplinary/': 'list_records_api_v1_disciplinary__get',
  'POST /api/v1/disciplinary/': 'create_record_api_v1_disciplinary__post',
  'GET /api/v1/disciplinary/me': 'list_my_records_api_v1_disciplinary_me_get',
  'GET /api/v1/disciplinary/{record_id}': 'get_record_api_v1_disciplinary__record_id__get',
  'PATCH /api/v1/disciplinary/{record_id}': 'update_record_api_v1_disciplinary__record_id__patch',
  'DELETE /api/v1/disciplinary/{record_id}': 'delete_record_api_v1_disciplinary__record_id__delete',
  'GET /api/v1/documents/': 'list_documents_api_v1_documents__get',
  'POST /api/v1/documents/bulk-upload': 'bulk_upload_documents_api_v1_documents_bulk_upload_post',
  'GET /api/v1/documents/ingestion-jobs/{job_id}': 'get_ingestion_job_api_v1_documents_ingestion_jobs__job_id__get',
  'POST /api/v1/documents/ingestion-jobs/{job_id}/retry': 'retry_ingestion_job_api_v1_documents_ingestion_jobs__job_id__retry_post',
  'POST /api/v1/documents/upload': 'upload_document_api_v1_documents_upload_post',
  'PATCH /api/v1/documents/{document_id}/access': 'update_document_access_api_v1_documents__document_id__access_patch',
  'PATCH /api/v1/documents/{document_id}/archive': 'archive_document_api_v1_documents__document_id__archive_patch',
  'POST /api/v1/documents/{document_id}/reindex': 'reindex_document_api_v1_documents__document_id__reindex_post',
  'PATCH /api/v1/documents/{document_id}/unarchive': 'unarchive_document_api_v1_documents__document_id__unarchive_patch',
  'GET /api/v1/events/': 'list_all_events_api_v1_events__get',
  'POST /api/v1/events/': 'create_event_api_v1_events__post',
  'GET /api/v1/events/export': 'export_events_api_v1_events_export_get',
  'GET /api/v1/events/public': 'list_public_events_api_v1_events_public_get',
  'GET /api/v1/events/{event_id}': 'get_event_api_v1_events__event_id__get',
  'PATCH /api/v1/events/{event_id}': 'update_event_api_v1_events__event_id__patch',
  'DELETE /api/v1/events/{event_id}': 'delete_event_api_v1_events__event_id__delete',
  'GET /api/v1/memberships/': 'list_profiles_api_v1_memberships__get',
  'POST /api/v1/memberships/': 'create_profile_api_v1_memberships__post',
  'GET /api/v1/memberships/export': 'export_members_api_v1_memberships_export_get',
  'POST /api/v1/memberships/import': 'import_members_api_v1_memberships_import_post',
  'GET /api/v1/memberships/me': 'get_my_profile_api_v1_memberships_me_get',
  'GET /api/v1/memberships/me/balance': 'get_my_balance_api_v1_memberships_me_balance_get',
  'GET /api/v1/memberships/me/contributions': 'get_my_contributions_api_v1_memberships_me_contributions_get',
  'GET /api/v1/memberships/me/statement': 'get_my_statement_api_v1_memberships_me_statement_get',
  'GET /api/v1/memberships/me/statement.pdf': 'download_my_statement_pdf_api_v1_memberships_me_statement_pdf_get',
  'GET /api/v1/memberships/{profile_id}': 'get_profile_api_v1_memberships__profile_id__get',
  'PATCH /api/v1/memberships/{profile_id}': 'update_profile_api_v1_memberships__profile_id__patch',
  'DELETE /api/v1/memberships/{profile_id}': 'delete_profile_api_v1_memberships__profile_id__delete',
  'GET /api/v1/memberships/{profile_id}/balance': 'get_member_balance_api_v1_memberships__profile_id__balance_get',
  'GET /api/v1/memberships/{profile_id}/statement': 'get_member_statement_api_v1_memberships__profile_id__statement_get',
  'GET /api/v1/modules': 'list_registered_modules_api_v1_modules_get',
  'GET /api/v1/modules/{module_key}': 'get_registered_module_api_v1_modules__module_key__get',
  'GET /api/v1/notifications/channels': 'list_notification_channels_api_v1_notifications_channels_get',
  'POST /api/v1/notifications/devices': 'register_notification_device_api_v1_notifications_devices_post',
  'POST /api/v1/notifications/devices/{installation_id}/revoke': 'revoke_notification_device_api_v1_notifications_devices__installation_id__revoke_post',
  'POST /api/v1/notifications/dispatch': 'send_live_notification_api_v1_notifications_dispatch_post',
  'GET /api/v1/notifications/health': 'get_notification_health_api_v1_notifications_health_get',
  'GET /api/v1/notifications/history': 'list_notification_history_api_v1_notifications_history_get',
  'GET /api/v1/notifications/inbox': 'get_user_notification_inbox_api_v1_notifications_inbox_get',
  'POST /api/v1/notifications/inbox/read-all': 'mark_all_user_notifications_read_api_v1_notifications_inbox_read_all_post',
  'POST /api/v1/notifications/inbox/{notification_id}/read': 'mark_user_notification_read_api_v1_notifications_inbox__notification_id__read_post',
  'POST /api/v1/notifications/mobile-push-tokens': 'subscribe_to_mobile_push_api_v1_notifications_mobile_push_tokens_post',
  'GET /api/v1/notifications/preferences': 'get_user_notification_preferences_api_v1_notifications_preferences_get',
  'PUT /api/v1/notifications/preferences': 'update_user_notification_preferences_api_v1_notifications_preferences_put',
  'POST /api/v1/notifications/push-subscriptions': 'subscribe_to_web_push_api_v1_notifications_push_subscriptions_post',
  'GET /api/v1/notifications/push/configuration': 'get_web_push_configuration_api_v1_notifications_push_configuration_get',
  'POST /api/v1/notifications/reconciliation/callback': 'receive_notification_reconciliation_callback_api_v1_notifications_reconciliation_callback_post',
  'POST /api/v1/notifications/reconciliation/poll': 'poll_notification_reconciliation_api_v1_notifications_reconciliation_poll_post',
  'POST /api/v1/notifications/retry': 'retry_notification_dispatch_api_v1_notifications_retry_post',
  'POST /api/v1/notifications/test': 'send_test_notification_api_v1_notifications_test_post',
  'GET /api/v1/notifications/unreachable': 'get_unreachable_notification_recipients_api_v1_notifications_unreachable_get',
  'GET /api/v1/policies/': 'list_policies_api_v1_policies__get',
  'POST /api/v1/policies/': 'create_policy_api_v1_policies__post',
  'GET /api/v1/policies/categories': 'list_policy_categories_api_v1_policies_categories_get',
  'GET /api/v1/policies/public': 'list_public_policies_api_v1_policies_public_get',
  'GET /api/v1/policies/{policy_id}': 'get_policy_api_v1_policies__policy_id__get',
  'PATCH /api/v1/policies/{policy_id}': 'update_policy_api_v1_policies__policy_id__patch',
  'DELETE /api/v1/policies/{policy_id}': 'delete_policy_api_v1_policies__policy_id__delete',
  'GET /api/v1/recovery/backups': 'backup_overview_api_v1_recovery_backups_get',
  'POST /api/v1/recovery/backups': 'request_backup_api_v1_recovery_backups_post',
  'POST /api/v1/recovery/backups/import': 'import_backup_api_v1_recovery_backups_import_post',
  'GET /api/v1/recovery/backups/{run_id}': 'get_backup_api_v1_recovery_backups__run_id__get',
  'GET /api/v1/sample/status': 'sample_status_api_v1_sample_status_get',
  'GET /api/v1/search': 'global_search_api_v1_search_get',
  'GET /api/v1/sports/events': 'list_sports_events_api_v1_sports_events_get',
  'POST /api/v1/sports/events': 'create_sports_event_api_v1_sports_events_post',
  'GET /api/v1/sports/events/{event_id}': 'get_sports_event_api_v1_sports_events__event_id__get',
  'PATCH /api/v1/sports/events/{event_id}': 'update_sports_event_api_v1_sports_events__event_id__patch',
  'DELETE /api/v1/sports/events/{event_id}': 'delete_sports_event_api_v1_sports_events__event_id__delete',
  'GET /api/v1/tenants/': 'list_my_tenants_api_v1_tenants__get',
  'GET /api/v1/tenants/{tenant_id}': 'get_tenant_api_v1_tenants__tenant_id__get',
  'GET /api/v1/tenants/{tenant_id}/roles': 'list_tenant_roles_api_v1_tenants__tenant_id__roles_get',
  'POST /api/v1/tenants/{tenant_id}/roles': 'create_tenant_role_bundle_api_v1_tenants__tenant_id__roles_post',
  'GET /api/v1/tenants/{tenant_id}/settings': 'get_tenant_settings_api_v1_tenants__tenant_id__settings_get',
  'PUT /api/v1/tenants/{tenant_id}/settings': 'update_tenant_settings_api_v1_tenants__tenant_id__settings_put',
  'GET /health': 'health_check_health_get',
  'GET /health/live': 'liveness_check_health_live_get',
  'GET /health/ready': 'readiness_check_health_ready_get',
  'GET /metrics': 'metrics_metrics_get',
};
