// AUTO-GENERATED from docs/api/openapi.json — do not edit by hand.
// Regenerate with: node scripts/generate-client-contracts.mjs

export interface AcceptInviteRequest {
  display_name: string;
  password: string;
  token: string;
}

export interface AcceptInviteResponse {
  access_token: string;
  expires_in: number;
  tenant_id: string;
  token_type?: string;
  user_id: string;
}

export interface ActiveSessionResponse {
  created_at: string;
  created_ip?: string | null;
  created_user_agent?: string | null;
  current: boolean;
  current_tenant_id: string;
  id: string;
  last_seen_at: string;
  last_seen_ip?: string | null;
  last_seen_user_agent?: string | null;
}

export interface AnnouncementCreate {
  body: string;
  expires_at?: string | null;
  published_at?: string | null;
  title: string;
  visibility_scope?: AnnouncementVisibility;
}

export interface AnnouncementResponse {
  body: string;
  created_at: string;
  created_by: string | null;
  expires_at: string | null;
  id: string;
  published_at: string | null;
  tenant_id: string;
  title: string;
  updated_at: string;
  visibility_scope: string;
}

export interface AnnouncementUpdate {
  body?: string | null;
  expires_at?: string | null;
  published_at?: string | null;
  title?: string | null;
  visibility_scope?: AnnouncementVisibility | null;
}

export type AnnouncementVisibility = "tenant_public" | "members_only" | "role_restricted" | "admin_only";

export interface AnnualBudgetResponse {
  available_balance: string;
  currency?: string;
  expense_total: string;
  expenses_by_category: Array<BudgetCategoryTotal>;
  income_by_category: Array<BudgetCategoryTotal>;
  income_total: string;
  recent_expenses: Array<ExpenseRecordResponse>;
  year: number;
}

export interface AssistedAccessRecoveryRequest {
  reason?: string;
}

export interface AssistedAccessRecoveryResponse {
  expires_at: string;
  message?: string;
  revoked_session_count?: number;
  target_display_name: string;
  target_user_id: string;
  temporary_password: string;
}

export interface AttentionItem {
  category: "finance" | "governance" | "community" | "account" | "knowledge";
  count: number;
  id: string;
  priority: "urgent" | "attention" | "normal" | "informational";
  target_path: string;
  title_key: string;
}

export interface AttentionOverview {
  items: Array<AttentionItem>;
}

export interface AuditActorSummary {
  display_name: string;
  email: string;
  roles?: Array<string>;
}

export interface AuditEventResponse {
  action: string;
  actor?: AuditActorSummary | null;
  actor_user_id: string | null;
  created_at: string;
  details?: Record<string, unknown>;
  entity_id: string | null;
  entity_type: string;
  id: string;
  module_key: string | null;
  tenant_id: string;
}

export interface BackupOverviewResponse {
  automatic_enabled: boolean;
  external_storage_configured: boolean;
  last_restore_drill_at: string | null;
  last_successful_backup_at: string | null;
  point_in_time_recovery_enabled: boolean;
  retention_days: number;
  runs: Array<BackupRunResponse>;
}

export interface BackupRequest {
  reason?: string | null;
}

export interface BackupRunResponse {
  archive_sha256: string | null;
  archive_size_bytes: number | null;
  completed_at: string | null;
  components: Record<string, unknown>;
  error_code: string | null;
  id: string;
  manifest_sha256: string | null;
  requested_at: string;
  started_at: string | null;
  status: string;
  storage_reference: string | null;
  tenant_id: string;
  trigger: string;
  verified_at: string | null;
}

export interface Body_bulk_upload_documents_api_v1_documents_bulk_upload_post {
  access_scope?: string;
  allowed_role_ids?: Array<string> | null;
  description?: string | null;
  files: Array<string>;
  title_prefix?: string;
}

export interface Body_import_backup_api_v1_recovery_backups_import_post {
  archive: string;
  manifest: string;
}

export interface Body_import_contributions_api_v1_contributions_import_post {
  file: string;
}

export interface Body_import_members_api_v1_memberships_import_post {
  file: string;
}

export interface Body_upload_document_api_v1_documents_upload_post {
  access_scope?: string;
  allowed_role_ids?: Array<string> | null;
  description?: string | null;
  file: string;
  title?: string;
}

export interface BrandingConfig {
  logo_url?: string;
  primary_color?: string;
}

export interface BudgetCategoryTotal {
  amount: string;
  category: string;
}

export interface BulkUploadItemResponse {
  document?: UploadDocumentResponse | null;
  error?: string | null;
  file_name: string;
  index: number;
  status: string;
}

export interface BulkUploadResponse {
  failure_count?: number;
  items?: Array<BulkUploadItemResponse>;
  success_count?: number;
}

export type CashHandoverStatus = "pending_handover" | "handover_reported" | "received_in_treasury";

export interface ChangeInitialPasswordRequest {
  new_password: string;
}

export interface ChangeInitialPasswordResponse {
  message?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  message?: string;
  revoked_session_count?: number;
}

export interface ChatCitationResponse {
  chunk_id: string;
  document_id: string;
  document_title: string;
  document_version_id: string;
  excerpt: string;
  score: number;
}

export interface ChatConversationCreate {
  title?: string;
}

export interface ChatConversationDetailResponse {
  created_at: string;
  id: string;
  messages?: Array<ChatMessageResponse>;
  tenant_id: string;
  title: string;
  updated_at: string;
  user_id: string;
}

export interface ChatConversationResponse {
  created_at: string;
  id: string;
  last_message_preview?: string | null;
  message_count?: number;
  tenant_id: string;
  title: string;
  updated_at: string;
  user_id: string;
}

export interface ChatConversationUpdate {
  title: string;
}

export interface ChatDomainPolicyResponse {
  allowed_domains?: Array<string>;
}

export interface ChatMessageResponse {
  citations_json?: Array<Record<string, unknown>>;
  content: string;
  created_at: string;
  id: string;
  role: string;
}

export interface ChatQueryLogResponse {
  answer_preview: string;
  citation_count: number;
  confidence: number;
  created_at: string;
  id: string;
  question_preview: string;
  refusal_reason_preview: string | null;
  refused: boolean;
  source_types?: Array<string>;
  tenant_id: string;
  user_id: string;
}

export interface ChatQueryRequest {
  conversation_id?: string | null;
  question: string;
  response_language?: string;
  top_k?: number;
}

export interface ChatQueryResponse {
  answer: string;
  citations?: Array<ChatCitationResponse>;
  confidence: number;
  conversation_id?: string | null;
  refusal_reason?: string | null;
  refused?: boolean;
  source_types?: Array<string>;
}

export interface ContributionReceiptDeclarationCreate {
  amount: number | string;
  currency?: string;
  disciplinary_record_id?: string | null;
  evidence_json?: string;
  income_type?: FinancialIncomeType;
  membership_profile_id?: string | null;
  note?: string | null;
  payment_method?: PaymentMethod;
  received_at?: string | null;
  reference?: string | null;
  source_name?: string | null;
}

export interface ContributionReceiptDeclarationProcess {
  action: "validated" | "partially_validated" | "rejected" | "clarification_requested" | "cancelled";
  contribution_record_id?: string | null;
  handover_reminder_days?: number;
  note?: string | null;
  processed_amount?: number | string | null;
}

export interface ContributionReceiptDeclarationResponse {
  amount: string | null;
  cash_handover_status: CashHandoverStatus | null;
  contribution_record_id: string | null;
  created_at: string;
  currency: string;
  declarant_role_code: string;
  declarant_user_id: string;
  disciplinary_record_id: string | null;
  evidence_json: string;
  handover_due_at: string | null;
  handover_method: string | null;
  handover_reminder_days: number | null;
  handover_reminder_sent_at: string | null;
  handover_reminder_updated_at: string | null;
  handover_reported_at: string | null;
  handover_reported_by_user_id: string | null;
  id: string;
  income_type: FinancialIncomeType;
  membership_profile_id: string | null;
  note: string | null;
  payment_method: string;
  payment_record_id: string | null;
  processed_amount: string | null;
  processed_at: string | null;
  processed_by_user_id: string | null;
  processing_note: string | null;
  received_at: string;
  reference: string | null;
  source_name: string | null;
  status: ContributionReceiptStatus;
  submitted_at: string | null;
  tenant_id: string;
  treasury_receipt_note: string | null;
  treasury_received_at: string | null;
  treasury_received_by_user_id: string | null;
  updated_at: string;
}

export interface ContributionReceiptDeclarationUpdate {
  amount?: number | string | null;
  currency?: string | null;
  evidence_json?: string | null;
  income_type?: FinancialIncomeType | null;
  membership_profile_id?: string | null;
  note?: string | null;
  payment_method?: PaymentMethod | null;
  received_at?: string | null;
  reference?: string | null;
  source_name?: string | null;
}

export interface ContributionReceiptHandoverReminderUpdate {
  reminder_days: number;
}

export interface ContributionReceiptHandoverReport {
  method: "cash" | "bank_transfer";
  note?: string | null;
}

export interface ContributionReceiptMemberOption {
  display_name: string;
  email: string | null;
  first_name: string;
  id: string;
  joined_at: string;
  last_name: string;
  member_code: string;
  membership_type: string;
  phone: string | null;
  status: string;
}

export type ContributionReceiptStatus = "draft" | "submitted" | "clarification_requested" | "validated" | "partially_validated" | "rejected" | "cancelled";

export interface ContributionReceiptTreasuryConfirmation {
  method?: "cash" | "bank_transfer";
  note?: string | null;
}

export interface ContributionRecordCreate {
  currency?: string;
  due_date?: string | null;
  expected_amount?: number | string;
  membership_profile_id: string;
  paid_amount?: number | string;
  status?: ContributionStatus;
  year: number;
}

export interface ContributionRecordResponse {
  balance: string;
  created_at: string;
  currency: string;
  due_date: string | null;
  expected_amount: string;
  id: string;
  membership_profile_id: string;
  paid_amount: string;
  status: string;
  tenant_id: string;
  updated_at: string;
  year: number;
}

export interface ContributionRecordUpdate {
  currency?: string | null;
  due_date?: string | null;
  expected_amount?: number | string | null;
  paid_amount?: number | string | null;
  status?: ContributionStatus | null;
}

export interface ContributionReminderBatchRequest {
  channel?: string;
  due_scope?: "all_outstanding" | "overdue" | "due_soon";
  limit?: number;
  status?: ContributionStatus | null;
  year?: number | null;
}

export interface ContributionReminderBatchResponse {
  attempted_count: number;
  reminder_count: number;
  reminders: Array<ContributionReminderResponse>;
}

export interface ContributionReminderResponse {
  balance_snapshot: string;
  body: string;
  channel: string;
  contribution_record_id: string;
  created_at: string;
  delivery_status: ReminderDeliveryStatus;
  due_date_snapshot: string | null;
  id: string;
  member_code: string;
  member_display_name: string;
  membership_profile_id: string;
  provider_message: string | null;
  recipient: string;
  reminded_by: string | null;
  sent_at: string;
  subject: string;
  tenant_id: string;
}

export interface ContributionReminderSendRequest {
  channel?: string;
}

export type ContributionStatus = "pending" | "partial" | "paid" | "overdue" | "waived";

export interface DeviceRegistrationRequest {
  browser?: string | null;
  device_metadata?: Record<string, string | number | boolean | null>;
  installation_id: string;
  platform?: string | null;
}

export interface DisciplinaryRecordCreate {
  amount?: number | string;
  currency?: string;
  description?: string | null;
  membership_profile_id: string;
  policy_record_id?: string | null;
  status?: DisciplinaryStatus;
  title: string;
}

export interface DisciplinaryRecordResponse {
  amount: string;
  created_at: string;
  currency: string;
  description: string | null;
  id: string;
  membership_display_name?: string | null;
  membership_profile_id: string;
  policy_record_id: string | null;
  policy_title?: string | null;
  recorded_at: string;
  recorded_by: string | null;
  status: string;
  tenant_id: string;
  title: string;
  updated_at: string;
}

export interface DisciplinaryRecordUpdate {
  amount?: number | string | null;
  currency?: string | null;
  description?: string | null;
  policy_record_id?: string | null;
  status?: DisciplinaryStatus | null;
  title?: string | null;
}

export type DisciplinaryStatus = "open" | "under_review" | "resolved" | "waived";

export interface DocumentAccessUpdateRequest {
  access_scope: string;
  allowed_role_ids?: Array<string> | null;
}

export interface DocumentListItemResponse {
  access_scope: string;
  allowed_role_ids?: Array<string> | null;
  created_at: string;
  current_version?: DocumentVersionResponse | null;
  description: string | null;
  id: string;
  language: string;
  owner_user_id: string | null;
  source_type: string;
  status: string;
  title: string;
}

export interface DocumentVersionResponse {
  checksum: string;
  created_at: string;
  file_name: string;
  file_size_bytes: number;
  id: string;
  mime_type: string;
  storage_bucket: string;
  storage_key: string;
}

export interface EventCreate {
  description?: string | null;
  end_at?: string | null;
  location?: string | null;
  metadata_json?: Record<string, unknown>;
  start_at: string;
  status?: EventStatus;
  title: string;
  visibility_scope?: EventVisibility;
}

export interface EventResponse {
  created_at: string;
  created_by: string | null;
  description: string | null;
  end_at: string | null;
  id: string;
  location: string | null;
  metadata_json?: Record<string, unknown>;
  start_at: string;
  status: string;
  tenant_id: string;
  title: string;
  updated_at: string;
  visibility_scope: string;
}

export type EventStatus = "draft" | "published" | "cancelled" | "completed";

export interface EventUpdate {
  description?: string | null;
  end_at?: string | null;
  location?: string | null;
  metadata_json?: Record<string, unknown> | null;
  start_at?: string | null;
  status?: EventStatus | null;
  title?: string | null;
  visibility_scope?: EventVisibility | null;
}

export type EventVisibility = "tenant_public" | "members_only" | "role_restricted" | "admin_only";

export type ExpenseCategory = "sport_equipment" | "fuel_transport" | "tournament" | "cultural_event" | "administration" | "other";

export interface ExpenseRecordCreate {
  amount: number | string;
  category: ExpenseCategory;
  currency?: string;
  description: string;
  payee?: string | null;
  payment_method?: PaymentMethod;
  reference?: string | null;
  spent_at?: string | null;
}

export interface ExpenseRecordResponse {
  amount: string;
  category: ExpenseCategory;
  created_at: string;
  created_by: string | null;
  currency: string;
  description: string;
  id: string;
  payee: string | null;
  payment_method: string;
  reference: string | null;
  spent_at: string;
  tenant_id: string;
}

export type FinancialIncomeType = "membership_contribution" | "donation" | "sponsorship" | "tournament_proceeds" | "other_income" | "disciplinary_payment";

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  message?: string;
  reset_token?: string | null;
}

export interface HTTPValidationError {
  detail?: Array<ValidationError>;
}

export interface ImportResult {
  dry_run: boolean;
  error_count: number;
  errors: Array<ImportRowError>;
  success_count: number;
  total_rows: number;
}

export interface ImportRowError {
  column?: string | null;
  message: string;
  row_number: number;
  value?: string | null;
}

export interface InboxNotificationResponse {
  category: string;
  correlation_id?: string | null;
  created_at: string;
  event_id?: string | null;
  event_type: string;
  id: string;
  metadata: Record<string, unknown>;
  priority: string;
  read_at: string | null;
  target_path: string;
}

export interface InboxResponse {
  items: Array<InboxNotificationResponse>;
  unread_count: number;
}

export interface IngestionJobHealthItemResponse {
  created_at: string;
  document_id: string;
  document_version_id: string;
  error_message: string | null;
  finished_at: string | null;
  job_id: string;
  started_at: string | null;
  status: string;
}

export interface IngestionJobHealthResponse {
  completed_count: number;
  failed_count: number;
  processing_count: number;
  queued_count: number;
  recent_failures: Array<IngestionJobHealthItemResponse>;
  retried_count: number;
}

export interface IngestionJobResponse {
  chunk_count: number;
  created_at: string;
  document_id: string;
  document_version_id: string;
  error_message: string | null;
  finished_at: string | null;
  id: string;
  indexed_chunk_count: number;
  started_at: string | null;
  status: string;
}

export interface IngestionJobRetryResponse {
  job: IngestionJobResponse;
  retried?: boolean;
}

export interface InvitationStatusResponse {
  created_at: string;
  email: string;
  expires_at: string;
  id: string;
  role_code: string;
  status: string;
}

export interface InviteRequest {
  email: string;
  role_code?: string;
  tenant_id: string;
}

export interface InviteResponse {
  delivery_message?: string | null;
  delivery_simulation_only?: boolean;
  delivery_status?: string;
  email: string;
  expires_at: string;
  invitation_id: string;
  invite_token?: string | null;
  role_code: string;
  status: string;
}

export interface LanguagePreferenceResponse {
  preferred_language: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  tenant_slug?: string | null;
}

export interface ManagedTenantUserActionResponse {
  membership_status: string;
  message: string;
  revoked_session_count?: number;
}

export interface ManagedTenantUserResponse {
  active_session_count?: number;
  display_name: string;
  email: string;
  last_login_at?: string | null;
  last_security_event_action?: string | null;
  last_security_event_at?: string | null;
  membership_status: string;
  profile_type: string;
  roles: Array<string>;
  user_id: string;
  user_status: string;
}

export interface ManagedTenantUserRolesUpdateRequest {
  role_codes: Array<string>;
}

export interface ManagedTenantUserRolesUpdateResponse {
  message: string;
  role_codes: Array<string>;
}

export interface MemberBalanceResponse {
  contribution_count?: number;
  profile: MembershipProfileResponse;
  total_balance?: string;
  total_expected?: string;
  total_paid?: string;
}

export interface MemberStatementResponse {
  contributions: Array<ContributionRecordResponse>;
  profile: MembershipProfileResponse;
  summary: MemberBalanceResponse;
}

export interface MembershipProfileCreate {
  city?: string | null;
  country_code?: string | null;
  display_name: string;
  email?: string | null;
  first_name: string;
  house_number?: string | null;
  last_name: string;
  login_identifier?: string | null;
  member_code?: string | null;
  membership_type?: MembershipType | null;
  phone?: string | null;
  postal_code?: string | null;
  provision_access?: boolean;
  status?: MembershipStatus;
  street_name?: string | null;
  temporary_password?: string | null;
}

export interface MembershipProfileResponse {
  city: string | null;
  country_code: string | null;
  created_at: string;
  display_name: string;
  email: string | null;
  first_name: string;
  house_number: string | null;
  id: string;
  joined_at: string;
  last_name: string;
  member_code: string;
  membership_type: string;
  phone: string | null;
  postal_code: string | null;
  status: string;
  street_name: string | null;
  tenant_id: string;
  updated_at: string;
  user_id: string | null;
}

export interface MembershipProfileUpdate {
  city?: string | null;
  country_code?: string | null;
  display_name?: string | null;
  email?: string | null;
  first_name?: string | null;
  house_number?: string | null;
  last_name?: string | null;
  member_code?: string | null;
  membership_type?: MembershipType | null;
  phone?: string | null;
  postal_code?: string | null;
  status?: MembershipStatus | null;
  street_name?: string | null;
}

export type MembershipStatus = "active" | "inactive" | "suspended" | "resigned";

export type MembershipType = "individual" | "family";

export interface MfaCompleteLoginRequest {
  code: string;
  mfa_token: string;
}

export interface MfaEnrollResponse {
  qr_code_url?: string;
  secret: string;
  uri: string;
}

export interface MfaLoginResponse {
  access_token: string;
  expires_in: number;
  password_change_required?: boolean;
  tenant_id: string;
  token_type?: string;
  user_id: string;
}

export interface MfaRequiredResponse {
  expires_in: number;
  mfa_required?: boolean;
  mfa_token: string;
}

export interface MfaStatusResponse {
  enabled: boolean;
  enrolled: boolean;
}

export interface MfaVerifyRequest {
  code: string;
}

export interface MfaVerifyResponse {
  enabled?: boolean;
  message?: string;
}

export interface MobilePushTokenRequest {
  browser?: string | null;
  device_metadata?: Record<string, string | number | boolean | null>;
  fcm_token: string;
  installation_id: string;
  platform?: string | null;
}

export interface ModuleNavigationEntryResponse {
  capabilities: Array<string>;
  key: string;
  label_key: string;
  order: number;
  path: string;
  section: string;
}

export interface ModuleToggles {
  announcements?: boolean;
  chat?: boolean;
  contributions?: boolean;
  disciplinary?: boolean;
  events?: boolean;
  membership?: boolean;
  notifications?: boolean;
  policies?: boolean;
}

export interface NotificationChannelResponse {
  channel: string;
  configured: boolean;
  description: string;
  display_name: string;
  polling_supported?: boolean;
  simulation_only: boolean;
  target_hint: string;
}

export interface NotificationDeviceRevocationResponse {
  disabled_fcm_tokens: number;
  disabled_web_subscriptions: number;
  revoked_profiles: number;
}

export interface NotificationDispatchRequest {
  body: string;
  channel: string;
  recipient: string;
  subject?: string | null;
}

export interface NotificationDispatchResponse {
  channel: string;
  delivered: boolean;
  delivery_stage: string;
  message: string;
  polling_supported?: boolean;
  provider_reference?: string | null;
  reconciliation_status: string;
  reconciliation_supported: boolean;
  simulation_only: boolean;
  status: string;
}

export interface NotificationHealthResponse {
  disabled_fcm_tokens: number;
  disabled_web_subscriptions: number;
  failed_outbox: number;
  firebase_configured: boolean;
  last_successful_dispatch_at?: string | null;
  oldest_pending_seconds?: number | null;
  pending_outbox: number;
  retrying_fcm_tokens?: number;
  retrying_web_subscriptions?: number;
  web_push_configured: boolean;
  worker_running: boolean;
}

export interface NotificationHistoryEntry {
  action: string;
  channel: string;
  created_at: string;
  delivered: boolean;
  delivery_stage: string;
  id: string;
  message: string;
  polling_supported?: boolean;
  provider_reference?: string | null;
  recipient: string;
  reconciliation_status: string;
  reconciliation_supported: boolean;
  retry_eligible?: boolean;
  retry_source_provider_reference?: string | null;
  retry_supported?: boolean;
  simulation_only: boolean;
  stale_minutes?: number | null;
  stale_pending?: boolean;
  status: string;
}

export interface NotificationHistoryResponse {
  items: Array<NotificationHistoryEntry>;
  summary: NotificationHistorySummary;
}

export interface NotificationHistorySummary {
  delivered: number;
  failed: number;
  pending: number;
  simulated: number;
  stale_pending: number;
  total: number;
}

export interface NotificationPreferencesResponse {
  announcements_enabled?: boolean;
  discipline_enabled?: boolean;
  events_enabled?: boolean;
  finance_enabled?: boolean;
  push_enabled?: boolean;
}

export interface NotificationPreferencesUpdate {
  announcements_enabled?: boolean;
  discipline_enabled?: boolean;
  events_enabled?: boolean;
  finance_enabled?: boolean;
  push_enabled?: boolean;
}

export interface NotificationReconciliationCallbackRequest {
  channel: string;
  delivery_stage: "delivered" | "failed";
  external_status?: string | null;
  provider_message?: string | null;
  provider_reference: string;
  tenant_id: string;
}

export interface NotificationReconciliationCallbackResponse {
  channel: string;
  delivery_stage: string;
  provider_reference: string;
  reconciliation_status: string;
  updated: boolean;
}

export interface NotificationReconciliationPollRequest {
  channel: string;
  provider_reference: string;
}

export interface NotificationReconciliationPollResponse {
  channel: string;
  delivery_stage: string;
  external_status?: string | null;
  provider_message: string;
  provider_reference: string;
  reconciliation_status: string;
  updated: boolean;
}

export interface NotificationRetryRequest {
  channel: string;
  provider_reference: string;
}

export interface NotificationRetryResponse {
  dispatch: NotificationDispatchResponse;
  source_provider_reference: string;
}

export interface NotificationTestRequest {
  body: string;
  channels: Array<string>;
  recipient: string;
  subject?: string | null;
}

export interface NotificationTestResponse {
  results: Array<NotificationDispatchResponse>;
}

export interface OperationFailureCreate {
  method: string;
  path: string;
  status_code?: number | null;
}

export type PaymentMethod = "cash" | "bank_transfer" | "card" | "check" | "other";

export interface PaymentRecordCreate {
  amount: number | string;
  contribution_record_id: string;
  currency?: string;
  paid_at?: string | null;
  payment_method?: PaymentMethod;
  reference?: string | null;
}

export interface PaymentRecordResponse {
  amount: string;
  contribution_record_id: string;
  created_at: string;
  currency: string;
  id: string;
  paid_at: string;
  payment_method: string;
  recorded_by: string | null;
  reference: string | null;
  tenant_id: string;
}

export interface PolicyCategoryResponse {
  categories?: Array<string>;
}

export interface PolicyRecordCreate {
  category: string;
  description?: string | null;
  document_id?: string | null;
  status?: PolicyStatus;
  title: string;
}

export interface PolicyRecordResponse {
  category: string;
  created_at: string;
  created_by: string | null;
  description: string | null;
  document_id: string | null;
  document_title?: string | null;
  id: string;
  status: string;
  tenant_id: string;
  title: string;
  updated_at: string;
}

export interface PolicyRecordUpdate {
  category?: string | null;
  description?: string | null;
  document_id?: string | null;
  status?: PolicyStatus | null;
  title?: string | null;
}

export type PolicyStatus = "draft" | "published" | "archived";

export interface PushConfigurationResponse {
  enabled: boolean;
  public_key?: string | null;
  reason?: string | null;
}

export interface PushSubscriptionRequest {
  auth: string;
  browser?: string | null;
  device_metadata?: Record<string, string | number | boolean | null>;
  endpoint: string;
  installation_id: string;
  p256dh: string;
  platform?: string | null;
}

export interface RecoveryEvidenceConfig {
  alert_contacts_configured?: boolean;
  alert_posture?: string;
  backup_retention_days?: number | null;
  last_backup_at?: string | null;
  last_backup_reference?: string;
  last_backup_status?: string;
  last_restore_drill_at?: string | null;
  last_restore_drill_status?: string;
  notes?: string;
}

export interface RecoveryEvidenceResponse {
  alert_contacts_configured?: boolean;
  alert_is_healthy: boolean;
  alert_posture?: string;
  backup_is_stale: boolean;
  backup_retention_days?: number | null;
  last_backup_at?: string | null;
  last_backup_reference?: string;
  last_backup_status?: string;
  last_restore_drill_at?: string | null;
  last_restore_drill_status?: string;
  notes?: string;
  overall_status: string;
  restore_drill_is_stale: boolean;
  status_message: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
  token_type?: string;
}

export interface RegisteredModuleResponse {
  capabilities: Array<string>;
  depends_on: Array<string>;
  description: string;
  domain_event_types: Array<string>;
  enabled: boolean;
  key: string;
  name: string;
  navigation: Array<ModuleNavigationEntryResponse>;
}

export interface RegisteredModulesResponse {
  modules: Array<RegisteredModuleResponse>;
}

export type ReminderDeliveryStatus = "sent" | "simulated" | "failed" | "skipped";

export interface ResetPasswordRequest {
  new_password: string;
  token: string;
}

export interface ResetPasswordResponse {
  message?: string;
}

export interface RestoreImportResponse {
  guidance: string;
  run: BackupRunResponse;
  verified: boolean;
}

export interface RoleBundleCreate {
  capabilities: Array<string>;
  code: string;
  description?: string | null;
  name: string;
}

export interface RoleResponse {
  capabilities?: Array<string>;
  code: string;
  description: string | null;
  id: string;
  is_canonical?: boolean;
  is_system_role: boolean;
  name: string;
  tenant_id: string;
}

export interface SearchResponse {
  query: string;
  results: Array<SearchResult>;
}

export interface SearchResult {
  id: string;
  score: number;
  subtitle?: string | null;
  target_path: string;
  title: string;
  type: "members" | "documents" | "events" | "announcements" | "payments" | "receipts" | "audit" | "discipline";
  type_key: string;
}

export interface SecurityEventResponse {
  action: string;
  actor_user_id?: string | null;
  created_at: string;
  details: Record<string, unknown>;
  entity_id?: string | null;
  entity_type: string;
  id: string;
}

export interface SessionActionResponse {
  message: string;
  revoked_session_count?: number;
}

export interface SwitchTenantRequest {
  tenant_id: string;
}

export interface SwitchTenantResponse {
  access_token: string;
  expires_in: number;
  memberships: Array<TenantMembershipResponse>;
  tenant_id: string;
  token_type?: string;
  user_id: string;
}

export interface TenantMembershipResponse {
  branding: BrandingConfig;
  capabilities?: Array<string>;
  default_language: string;
  modules: ModuleToggles;
  name: string;
  profile_type: string;
  roles: Array<string>;
  slug: string;
  tenant_id: string;
}

export interface TenantResponse {
  created_at: string;
  default_language: string;
  id: string;
  name: string;
  slug: string;
  status: string;
  type: string;
}

export interface TenantSettingsResponse {
  branding: BrandingConfig;
  default_language: string;
  modules: ModuleToggles;
  name: string;
  operations?: RecoveryEvidenceResponse;
  slug: string;
  tenant_id: string;
  updated_at: string;
}

export interface TenantSettingsUpdate {
  branding?: BrandingConfig | null;
  default_language?: string | null;
  modules?: ModuleToggles | null;
  name?: string | null;
  operations?: RecoveryEvidenceConfig | null;
}

export interface TokenResponse {
  access_token: string;
  expires_in: number;
  password_change_required?: boolean;
  tenant_id: string;
  token_type?: string;
  user_id: string;
}

export interface UnreachableNotificationRecipient {
  display_name: string;
  last_notification_at: string;
  pending_notifications: number;
  user_id: string;
}

export interface UpdateLanguagePreferenceRequest {
  preferred_language: string;
}

export interface UploadDocumentResponse {
  access_scope: string;
  allowed_role_ids?: Array<string> | null;
  created_at: string;
  current_version?: DocumentVersionResponse | null;
  description: string | null;
  duplicate_of_document_id?: string | null;
  id: string;
  ingestion_job_id: string;
  language: string;
  owner_user_id: string | null;
  source_type: string;
  status: string;
  title: string;
}

export interface UserWithMembershipsResponse {
  capabilities?: Array<string>;
  display_name: string;
  email: string;
  id: string;
  last_login_at?: string | null;
  memberships: Array<TenantMembershipResponse>;
  password_change_required?: boolean;
  preferred_language?: string | null;
  roles: Array<string>;
  status: string;
  tenant_id: string;
}

export interface ValidationError {
  ctx?: Record<string, unknown>;
  input?: unknown;
  loc: Array<string | number>;
  msg: string;
  type: string;
}

export interface ApiOperations {
  'GET /api/v1/admin/audit/events': { request: undefined; response: Array<AuditEventResponse> };
  'GET /api/v1/admin/audit/events/export': { request: undefined; response: unknown };
  'GET /api/v1/admin/audit/operation-journal': { request: undefined; response: Array<AuditEventResponse> };
  'POST /api/v1/admin/audit/operation-journal/failures': { request: OperationFailureCreate; response: undefined };
  'GET /api/v1/admin/chat-queries': { request: undefined; response: Array<ChatQueryLogResponse> };
  'GET /api/v1/admin/ingestion-jobs/health': { request: undefined; response: IngestionJobHealthResponse };
  'GET /api/v1/admin/module-has-data': { request: undefined; response: Record<string, unknown> };
  'GET /api/v1/announcements/': { request: undefined; response: Array<AnnouncementResponse> };
  'POST /api/v1/announcements/': { request: AnnouncementCreate; response: AnnouncementResponse };
  'GET /api/v1/announcements/active': { request: undefined; response: Array<AnnouncementResponse> };
  'GET /api/v1/announcements/export': { request: undefined; response: unknown };
  'GET /api/v1/announcements/{announcement_id}': { request: undefined; response: AnnouncementResponse };
  'PATCH /api/v1/announcements/{announcement_id}': { request: AnnouncementUpdate; response: AnnouncementResponse };
  'DELETE /api/v1/announcements/{announcement_id}': { request: undefined; response: undefined };
  'GET /api/v1/attention': { request: undefined; response: AttentionOverview };
  'POST /api/v1/auth/accept-invite': { request: AcceptInviteRequest; response: AcceptInviteResponse };
  'POST /api/v1/auth/access-recovery/{user_id}': { request: AssistedAccessRecoveryRequest; response: AssistedAccessRecoveryResponse };
  'GET /api/v1/auth/admin/managed-users/{tenant_id}': { request: undefined; response: Array<ManagedTenantUserResponse> };
  'POST /api/v1/auth/admin/managed-users/{user_id}/reactivate': { request: undefined; response: ManagedTenantUserActionResponse };
  'POST /api/v1/auth/admin/managed-users/{user_id}/revoke-sessions': { request: undefined; response: ManagedTenantUserActionResponse };
  'PUT /api/v1/auth/admin/managed-users/{user_id}/roles': { request: ManagedTenantUserRolesUpdateRequest; response: ManagedTenantUserRolesUpdateResponse };
  'POST /api/v1/auth/admin/managed-users/{user_id}/suspend': { request: undefined; response: ManagedTenantUserActionResponse };
  'POST /api/v1/auth/change-initial-password': { request: ChangeInitialPasswordRequest; response: ChangeInitialPasswordResponse };
  'POST /api/v1/auth/change-password': { request: ChangePasswordRequest; response: ChangePasswordResponse };
  'POST /api/v1/auth/forgot-password': { request: ForgotPasswordRequest; response: ForgotPasswordResponse };
  'DELETE /api/v1/auth/invitations/{invitation_id}': { request: undefined; response: undefined };
  'GET /api/v1/auth/invitations/{tenant_id}': { request: undefined; response: Array<InvitationStatusResponse> };
  'POST /api/v1/auth/invite': { request: InviteRequest; response: InviteResponse };
  'POST /api/v1/auth/login': { request: LoginRequest; response: TokenResponse | MfaRequiredResponse };
  'GET /api/v1/auth/me': { request: undefined; response: UserWithMembershipsResponse };
  'PATCH /api/v1/auth/me/preferences/language': { request: UpdateLanguagePreferenceRequest; response: LanguagePreferenceResponse };
  'DELETE /api/v1/auth/mfa': { request: undefined; response: undefined };
  'POST /api/v1/auth/mfa/complete': { request: MfaCompleteLoginRequest; response: MfaLoginResponse };
  'POST /api/v1/auth/mfa/enroll': { request: undefined; response: MfaEnrollResponse };
  'GET /api/v1/auth/mfa/status': { request: undefined; response: MfaStatusResponse };
  'POST /api/v1/auth/mfa/verify': { request: MfaVerifyRequest; response: MfaVerifyResponse };
  'GET /api/v1/auth/protected': { request: undefined; response: Record<string, unknown> };
  'POST /api/v1/auth/refresh': { request: RefreshTokenRequest; response: RefreshTokenResponse };
  'POST /api/v1/auth/reset-password': { request: ResetPasswordRequest; response: ResetPasswordResponse };
  'GET /api/v1/auth/security-events': { request: undefined; response: Array<SecurityEventResponse> };
  'GET /api/v1/auth/sessions': { request: undefined; response: Array<ActiveSessionResponse> };
  'POST /api/v1/auth/sessions/revoke-all': { request: undefined; response: SessionActionResponse };
  'POST /api/v1/auth/sessions/revoke-others': { request: undefined; response: SessionActionResponse };
  'DELETE /api/v1/auth/sessions/{session_id}': { request: undefined; response: SessionActionResponse };
  'POST /api/v1/auth/switch-tenant': { request: SwitchTenantRequest; response: SwitchTenantResponse };
  'GET /api/v1/chat/conversations': { request: undefined; response: Array<ChatConversationResponse> };
  'POST /api/v1/chat/conversations': { request: ChatConversationCreate; response: ChatConversationResponse };
  'GET /api/v1/chat/conversations/{conversation_id}': { request: undefined; response: ChatConversationDetailResponse };
  'PATCH /api/v1/chat/conversations/{conversation_id}': { request: ChatConversationUpdate; response: ChatConversationResponse };
  'DELETE /api/v1/chat/conversations/{conversation_id}': { request: undefined; response: undefined };
  'GET /api/v1/chat/domain-policy': { request: undefined; response: ChatDomainPolicyResponse };
  'POST /api/v1/chat/query': { request: ChatQueryRequest; response: ChatQueryResponse };
  'POST /api/v1/chat/query-stream': { request: ChatQueryRequest; response: unknown };
  'GET /api/v1/contributions/': { request: undefined; response: Array<ContributionRecordResponse> };
  'POST /api/v1/contributions/': { request: ContributionRecordCreate; response: ContributionRecordResponse };
  'GET /api/v1/contributions/annual-budget': { request: undefined; response: AnnualBudgetResponse };
  'GET /api/v1/contributions/by-member/{profile_id}': { request: undefined; response: Array<ContributionRecordResponse> };
  'POST /api/v1/contributions/expenses': { request: ExpenseRecordCreate; response: ExpenseRecordResponse };
  'GET /api/v1/contributions/export': { request: undefined; response: unknown };
  'POST /api/v1/contributions/import': { request: undefined; response: ImportResult };
  'GET /api/v1/contributions/payments': { request: undefined; response: Array<PaymentRecordResponse> };
  'POST /api/v1/contributions/payments': { request: PaymentRecordCreate; response: PaymentRecordResponse };
  'GET /api/v1/contributions/receipt-declarations': { request: undefined; response: Array<ContributionReceiptDeclarationResponse> };
  'POST /api/v1/contributions/receipt-declarations': { request: ContributionReceiptDeclarationCreate; response: ContributionReceiptDeclarationResponse };
  'GET /api/v1/contributions/receipt-declarations/me': { request: undefined; response: Array<ContributionReceiptDeclarationResponse> };
  'GET /api/v1/contributions/receipt-declarations/member-options': { request: undefined; response: Array<ContributionReceiptMemberOption> };
  'GET /api/v1/contributions/receipt-declarations/mine': { request: undefined; response: Array<ContributionReceiptDeclarationResponse> };
  'PATCH /api/v1/contributions/receipt-declarations/{declaration_id}': { request: ContributionReceiptDeclarationUpdate; response: ContributionReceiptDeclarationResponse };
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/confirm-treasury-receipt': { request: ContributionReceiptTreasuryConfirmation; response: ContributionReceiptDeclarationResponse };
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/handover': { request: ContributionReceiptHandoverReport; response: ContributionReceiptDeclarationResponse };
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/handover-reminder': { request: ContributionReceiptHandoverReminderUpdate; response: ContributionReceiptDeclarationResponse };
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/process': { request: ContributionReceiptDeclarationProcess; response: ContributionReceiptDeclarationResponse };
  'POST /api/v1/contributions/receipt-declarations/{declaration_id}/submit': { request: undefined; response: ContributionReceiptDeclarationResponse };
  'GET /api/v1/contributions/reminders': { request: undefined; response: Array<ContributionReminderResponse> };
  'POST /api/v1/contributions/reminders/send': { request: ContributionReminderBatchRequest; response: ContributionReminderBatchResponse };
  'GET /api/v1/contributions/report/export': { request: undefined; response: unknown };
  'GET /api/v1/contributions/report/export/{export_format}': { request: undefined; response: unknown };
  'GET /api/v1/contributions/summary': { request: undefined; response: Record<string, unknown> };
  'GET /api/v1/contributions/{contribution_id}': { request: undefined; response: ContributionRecordResponse };
  'PATCH /api/v1/contributions/{contribution_id}': { request: ContributionRecordUpdate; response: ContributionRecordResponse };
  'DELETE /api/v1/contributions/{contribution_id}': { request: undefined; response: undefined };
  'GET /api/v1/contributions/{contribution_id}/payments': { request: undefined; response: Array<PaymentRecordResponse> };
  'POST /api/v1/contributions/{contribution_id}/reminders/send': { request: ContributionReminderSendRequest; response: ContributionReminderResponse };
  'GET /api/v1/disciplinary/': { request: undefined; response: Array<DisciplinaryRecordResponse> };
  'POST /api/v1/disciplinary/': { request: DisciplinaryRecordCreate; response: DisciplinaryRecordResponse };
  'GET /api/v1/disciplinary/me': { request: undefined; response: Array<DisciplinaryRecordResponse> };
  'GET /api/v1/disciplinary/{record_id}': { request: undefined; response: DisciplinaryRecordResponse };
  'PATCH /api/v1/disciplinary/{record_id}': { request: DisciplinaryRecordUpdate; response: DisciplinaryRecordResponse };
  'DELETE /api/v1/disciplinary/{record_id}': { request: undefined; response: undefined };
  'GET /api/v1/documents/': { request: undefined; response: Array<DocumentListItemResponse> };
  'POST /api/v1/documents/bulk-upload': { request: undefined; response: BulkUploadResponse };
  'GET /api/v1/documents/ingestion-jobs/{job_id}': { request: undefined; response: IngestionJobResponse };
  'POST /api/v1/documents/ingestion-jobs/{job_id}/retry': { request: undefined; response: IngestionJobRetryResponse };
  'POST /api/v1/documents/upload': { request: undefined; response: UploadDocumentResponse };
  'PATCH /api/v1/documents/{document_id}/access': { request: DocumentAccessUpdateRequest; response: DocumentListItemResponse };
  'PATCH /api/v1/documents/{document_id}/archive': { request: undefined; response: DocumentListItemResponse };
  'POST /api/v1/documents/{document_id}/reindex': { request: undefined; response: IngestionJobResponse };
  'PATCH /api/v1/documents/{document_id}/unarchive': { request: undefined; response: DocumentListItemResponse };
  'GET /api/v1/events/': { request: undefined; response: Array<EventResponse> };
  'POST /api/v1/events/': { request: EventCreate; response: EventResponse };
  'GET /api/v1/events/export': { request: undefined; response: unknown };
  'GET /api/v1/events/public': { request: undefined; response: Array<EventResponse> };
  'GET /api/v1/events/{event_id}': { request: undefined; response: EventResponse };
  'PATCH /api/v1/events/{event_id}': { request: EventUpdate; response: EventResponse };
  'DELETE /api/v1/events/{event_id}': { request: undefined; response: undefined };
  'GET /api/v1/memberships/': { request: undefined; response: Array<MembershipProfileResponse> };
  'POST /api/v1/memberships/': { request: MembershipProfileCreate; response: MembershipProfileResponse };
  'GET /api/v1/memberships/export': { request: undefined; response: unknown };
  'POST /api/v1/memberships/import': { request: undefined; response: ImportResult };
  'GET /api/v1/memberships/me': { request: undefined; response: MembershipProfileResponse };
  'GET /api/v1/memberships/me/balance': { request: undefined; response: MemberBalanceResponse };
  'GET /api/v1/memberships/me/contributions': { request: undefined; response: Array<ContributionRecordResponse> };
  'GET /api/v1/memberships/me/statement': { request: undefined; response: MemberStatementResponse };
  'GET /api/v1/memberships/me/statement.pdf': { request: undefined; response: unknown };
  'GET /api/v1/memberships/{profile_id}': { request: undefined; response: MembershipProfileResponse };
  'PATCH /api/v1/memberships/{profile_id}': { request: MembershipProfileUpdate; response: MembershipProfileResponse };
  'DELETE /api/v1/memberships/{profile_id}': { request: undefined; response: undefined };
  'GET /api/v1/memberships/{profile_id}/balance': { request: undefined; response: MemberBalanceResponse };
  'GET /api/v1/memberships/{profile_id}/statement': { request: undefined; response: MemberStatementResponse };
  'GET /api/v1/modules': { request: undefined; response: RegisteredModulesResponse };
  'GET /api/v1/modules/{module_key}': { request: undefined; response: RegisteredModuleResponse };
  'GET /api/v1/notifications/channels': { request: undefined; response: Array<NotificationChannelResponse> };
  'POST /api/v1/notifications/devices': { request: DeviceRegistrationRequest; response: undefined };
  'POST /api/v1/notifications/devices/{installation_id}/revoke': { request: undefined; response: NotificationDeviceRevocationResponse };
  'POST /api/v1/notifications/dispatch': { request: NotificationDispatchRequest; response: NotificationDispatchResponse };
  'GET /api/v1/notifications/health': { request: undefined; response: NotificationHealthResponse };
  'GET /api/v1/notifications/history': { request: undefined; response: NotificationHistoryResponse };
  'GET /api/v1/notifications/inbox': { request: undefined; response: InboxResponse };
  'POST /api/v1/notifications/inbox/read-all': { request: undefined; response: undefined };
  'POST /api/v1/notifications/inbox/{notification_id}/read': { request: undefined; response: undefined };
  'POST /api/v1/notifications/mobile-push-tokens': { request: MobilePushTokenRequest; response: undefined };
  'GET /api/v1/notifications/preferences': { request: undefined; response: NotificationPreferencesResponse };
  'PUT /api/v1/notifications/preferences': { request: NotificationPreferencesUpdate; response: NotificationPreferencesResponse };
  'POST /api/v1/notifications/push-subscriptions': { request: PushSubscriptionRequest; response: undefined };
  'GET /api/v1/notifications/push/configuration': { request: undefined; response: PushConfigurationResponse };
  'POST /api/v1/notifications/reconciliation/callback': { request: NotificationReconciliationCallbackRequest; response: NotificationReconciliationCallbackResponse };
  'POST /api/v1/notifications/reconciliation/poll': { request: NotificationReconciliationPollRequest; response: NotificationReconciliationPollResponse };
  'POST /api/v1/notifications/retry': { request: NotificationRetryRequest; response: NotificationRetryResponse };
  'POST /api/v1/notifications/test': { request: NotificationTestRequest; response: NotificationTestResponse };
  'GET /api/v1/notifications/unreachable': { request: undefined; response: Array<UnreachableNotificationRecipient> };
  'GET /api/v1/policies/': { request: undefined; response: Array<PolicyRecordResponse> };
  'POST /api/v1/policies/': { request: PolicyRecordCreate; response: PolicyRecordResponse };
  'GET /api/v1/policies/categories': { request: undefined; response: PolicyCategoryResponse };
  'GET /api/v1/policies/public': { request: undefined; response: Array<PolicyRecordResponse> };
  'GET /api/v1/policies/{policy_id}': { request: undefined; response: PolicyRecordResponse };
  'PATCH /api/v1/policies/{policy_id}': { request: PolicyRecordUpdate; response: PolicyRecordResponse };
  'DELETE /api/v1/policies/{policy_id}': { request: undefined; response: undefined };
  'GET /api/v1/recovery/backups': { request: undefined; response: BackupOverviewResponse };
  'POST /api/v1/recovery/backups': { request: BackupRequest; response: undefined };
  'POST /api/v1/recovery/backups/import': { request: undefined; response: RestoreImportResponse };
  'GET /api/v1/recovery/backups/{run_id}': { request: undefined; response: BackupRunResponse };
  'GET /api/v1/sample/status': { request: undefined; response: Record<string, string> };
  'GET /api/v1/search': { request: undefined; response: SearchResponse };
  'GET /api/v1/sports/events': { request: undefined; response: Array<EventResponse> };
  'POST /api/v1/sports/events': { request: EventCreate; response: EventResponse };
  'GET /api/v1/sports/events/{event_id}': { request: undefined; response: EventResponse };
  'PATCH /api/v1/sports/events/{event_id}': { request: EventUpdate; response: EventResponse };
  'DELETE /api/v1/sports/events/{event_id}': { request: undefined; response: undefined };
  'GET /api/v1/tenants/': { request: undefined; response: Array<TenantResponse> };
  'GET /api/v1/tenants/{tenant_id}': { request: undefined; response: TenantResponse };
  'GET /api/v1/tenants/{tenant_id}/roles': { request: undefined; response: Array<RoleResponse> };
  'POST /api/v1/tenants/{tenant_id}/roles': { request: RoleBundleCreate; response: RoleResponse };
  'GET /api/v1/tenants/{tenant_id}/settings': { request: undefined; response: TenantSettingsResponse };
  'PUT /api/v1/tenants/{tenant_id}/settings': { request: TenantSettingsUpdate; response: TenantSettingsResponse };
  'GET /health': { request: undefined; response: Record<string, unknown> };
  'GET /health/live': { request: undefined; response: Record<string, unknown> };
  'GET /health/ready': { request: undefined; response: unknown };
  'GET /metrics': { request: undefined; response: unknown };
}
