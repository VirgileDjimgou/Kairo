<template>
  <div class="p-4 members-view">
    <div class="d-flex flex-column flex-md-row align-items-md-start align-items-center justify-content-between gap-3 mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">{{ t('members.title') }}</h1>
        <p class="text-muted small mb-0">{{ t('members.subtitle') }}</p>
      </div>
      <div class="d-flex flex-wrap gap-2 justify-content-end w-100 w-md-auto">
        <button v-if="canUseBulkMemberTools" class="btn btn-outline-secondary btn-sm" @click="exportMembers" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>{{ t('common.exportCsv') }}
        </button>
        <button v-if="canUseBulkMemberTools" class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#importMemberModal">
          <i class="bi bi-upload me-1"></i>{{ t('common.importCsv') }}
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createMemberModal">
          <i class="bi bi-person-plus me-1"></i>{{ t('members.addMember') }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-3" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <div class="input-group mb-3">
      <span class="input-group-text"><i class="bi bi-search"></i></span>
      <input v-model.trim="searchQuery" class="form-control" :placeholder="t('members.searchPlaceholder')" @input="scheduleSearch" />
      <button v-if="searchQuery" class="btn btn-outline-secondary" type="button" @click="clearSearch">{{ t('common.reset') }}</button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('common.loading') }}</span>
      </div>
    </div>

    <div v-else-if="members.length === 0" class="empty-state">
      <i class="bi bi-people display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">{{ t('members.noMembers') }}</p>
      <p class="text-muted mb-3">
        {{ t('members.addFirst') }}
      </p>
      <div class="d-flex flex-wrap justify-content-center gap-2">
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createMemberModal">
          {{ t('members.addFirstMember') }}
        </button>
        <button class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#importMemberModal">
          {{ t('common.importCsv') }}
        </button>
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary btn-sm">
          {{ t('members.reviewSettings') }}
        </RouterLink>
      </div>
    </div>

    <div v-else class="row g-4 align-items-start">
    <div :class="selectedMember ? 'col-xl-8' : 'col-12'">
    <ResponsiveDataView
      class="card shadow-sm border-0"
      :items="members"
      :item-key="(member) => member.id"
      :mobile-aria-label="t('members.title')"
    >
      <template #thead>
        <tr>
          <th class="ps-4" scope="col">{{ t('members.code') }}</th>
          <th scope="col">{{ t('common.name') }}</th>
          <th scope="col">{{ t('common.email') }}</th>
          <th scope="col">{{ t('common.status') }}</th>
          <th scope="col">{{ t('members.joined') }}</th>
          <th class="text-end pe-4" scope="col">{{ t('common.actions') }}</th>
        </tr>
      </template>
      <template #rows>
        <tr v-for="member in members" :key="member.id" class="member-row" tabindex="0" @click="selectMember(member)" @keydown.enter="selectMember(member)">
          <td class="ps-4 font-monospace small">{{ member.member_code }}</td>
          <td class="fw-medium">{{ member.display_name }}</td>
          <td class="small text-muted">{{ member.email || '—' }}</td>
          <td><span class="badge" :class="member.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">{{ member.status }}</span></td>
          <td class="small">{{ formatDate(member.joined_at) }}</td>
          <td class="text-end pe-4">
            <button class="btn btn-sm btn-outline-secondary me-1" :aria-label="t('members.editMember')" @click.stop="editMember(member)"><i class="bi bi-pencil"></i></button>
            <button v-if="canRecoverMemberAccess && member.user_id" class="btn btn-sm btn-outline-primary me-1" :aria-label="t('members.recoverAccess')" @click.stop="openAccessRecovery(member)"><i class="bi bi-key"></i></button>
            <button class="btn btn-sm btn-outline-warning me-1" :aria-label="member.status === 'active' ? t('members.pauseMember') : t('members.reactivateMember')" @click.stop="toggleMemberPause(member)"><i :class="member.status === 'active' ? 'bi bi-pause-circle' : 'bi bi-play-circle'"></i></button>
            <button v-if="canDeleteMembers" class="btn btn-sm btn-outline-danger" :aria-label="t('members.deleteMember')" @click.stop="confirmDelete(member)"><i class="bi bi-trash"></i></button>
          </td>
        </tr>
      </template>
      <template #mobile-title="{ item: member }">
        <div>{{ member.display_name }}</div>
        <div class="small text-muted font-monospace">{{ member.member_code }}</div>
      </template>
      <template #mobile-status="{ item: member }">
        <span class="badge" :class="member.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">{{ member.status }}</span>
      </template>
      <template #mobile-fields="{ item: member }">
        <div class="om-data-card-row"><span class="om-data-card-label">{{ t('common.email') }}</span><span class="om-data-card-value om-technical-value">{{ member.email || '—' }}</span></div>
        <div class="om-data-card-row"><span class="om-data-card-label">{{ t('members.joined') }}</span><span class="om-data-card-value">{{ formatDate(member.joined_at) }}</span></div>
      </template>
      <template #mobile-actions="{ item: member }">
        <button class="btn btn-outline-primary" type="button" @click="selectMember(member)"><i class="bi bi-person-vcard me-2"></i>{{ t('members.viewDetails') }}</button>
        <button class="btn btn-outline-secondary" type="button" @click="editMember(member)"><i class="bi bi-pencil me-2"></i>{{ t('members.editMember') }}</button>
        <button v-if="canRecoverMemberAccess && member.user_id" class="btn btn-outline-primary" type="button" @click="openAccessRecovery(member)"><i class="bi bi-key me-2"></i>{{ t('members.recoverAccess') }}</button>
        <button class="btn btn-outline-warning" type="button" @click="toggleMemberPause(member)"><i :class="member.status === 'active' ? 'bi bi-pause-circle me-2' : 'bi bi-play-circle me-2'"></i>{{ member.status === 'active' ? t('members.pauseMember') : t('members.reactivateMember') }}</button>
        <button v-if="canDeleteMembers" class="btn btn-outline-danger" type="button" @click="confirmDelete(member)"><i class="bi bi-trash me-2"></i>{{ t('members.deleteMember') }}</button>
      </template>
    </ResponsiveDataView>
    </div>
    <div v-if="selectedMember" class="col-xl-4">
      <MemberInsightsPanel
        :member="selectedMember"
        :can-read-finance="canReadMemberFinance"
        :can-read-disciplinary="canReadMemberDiscipline"
        @close="selectedMember = null"
      />
    </div>
    <AssistedAccessRecoveryModal :member="accessRecoveryMember" @close="accessRecoveryMember = null" />
    </div>
    <!--
      Desktop markup now lives in ResponsiveDataView; the mobile representation is
      rendered from the same member collection and permission-aware actions.
    -->
    <div v-if="false" class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle" aria-label="Members list">
          <thead class="table-light">
            <tr>
              <th class="ps-4" scope="col">{{ t('members.code') }}</th>
              <th scope="col">{{ t('common.name') }}</th>
              <th scope="col">{{ t('common.email') }}</th>
              <th scope="col">{{ t('common.status') }}</th>
              <th scope="col">{{ t('members.joined') }}</th>
              <th class="text-end pe-4" scope="col">{{ t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in members" :key="member.id">
              <td class="ps-4 font-monospace small">{{ member.member_code }}</td>
              <td class="fw-medium">{{ member.display_name }}</td>
              <td class="small text-muted">{{ member.email || '—' }}</td>
              <td>
                <span class="badge"
                  :class="member.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">
                  {{ member.status }}
                </span>
              </td>
              <td class="small">{{ formatDate(member.joined_at) }}</td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-secondary me-1" :aria-label="t('members.editMember')"
                  @click="editMember(member)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" :aria-label="t('members.deleteMember')"
                  @click="confirmDelete(member)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>

          </tbody>
        </table>
      </div>
    </div>

    <!-- Import Members Modal -->
    <div class="modal fade" id="importMemberModal" tabindex="-1" aria-labelledby="importMemberModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="importMemberModalLabel">{{ t('members.importTitle') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetImport"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.csvFile') }}</label>
              <input ref="importFileInput" class="form-control form-control-sm" type="file" accept=".csv" @change="onImportFileChange" />
              <div class="form-text small">{{ t('members.requiredColumns') }}</div>
            </div>
            <div class="form-check mb-3">
              <input id="importDryRun" v-model="importDryRun" type="checkbox" class="form-check-input" />
              <label for="importDryRun" class="form-check-label small">{{ t('common.dryRun') }}</label>
            </div>
            <div v-if="importResult" class="mt-3">
              <hr />
              <div class="d-flex gap-3 mb-3">
                <span class="badge bg-secondary">{{ t('common.total') }}: {{ importResult.total }}</span>
                <span class="badge bg-success">{{ t('common.successCount') }}: {{ importResult.success_count }}</span>
                <span class="badge" :class="importResult.error_count > 0 ? 'bg-danger' : 'bg-success'">{{ t('common.errorCount') }}: {{ importResult.error_count }}</span>
              </div>
              <div v-if="importResult.errors.length > 0" class="mb-3">
                <h6 class="small fw-bold text-danger">{{ t('common.validationErrors') }}</h6>
                <div class="table-responsive">
                  <table class="table table-sm small mb-0">
                    <thead><tr><th>{{ t('common.row') }}</th><th>{{ t('common.errorColumn') }}</th></tr></thead>
                    <tbody>
                      <tr v-for="err in importResult.errors" :key="err.row">
                        <td>{{ err.row }}</td>
                        <td><div class="text-break">{{ err.message }}</div></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-if="importResult.error_count === 0 && !importDryRun" class="alert alert-success small py-2 mb-0">
                {{ t('members.successfullyImported').replace('{count}', String(importResult.success_count)) }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal" @click="resetImport">{{ t('common.cancel') }}</button>
            <button v-if="importDryRun && importResult && importResult.error_count === 0" type="button" class="btn btn-sm btn-primary" @click="confirmImport" :disabled="importing">
              {{ importing ? t('common.importing') : t('common.confirmImport') }}
            </button>
            <button v-else type="button" class="btn btn-sm btn-primary" @click="handleImport" :disabled="importing || !importSelectedFile">
              {{ importing ? t('common.importing') : importDryRun ? t('common.validate') : t('common.import') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Member Modal -->
    <div class="modal fade" id="createMemberModal" tabindex="-1" aria-labelledby="createMemberModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="createMemberModalLabel">{{ t('members.addMember') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <template v-if="!reviewMode">
            <div class="alert alert-light border small mb-3">
              <i class="bi bi-magic me-1" aria-hidden="true"></i>{{ t('members.memberCodeAuto') }}
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium" for="member-first-name">{{ t('members.firstName') }}</label>
                <input id="member-first-name" v-model="form.first_name" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.first_name }" required @input="clearMemberFieldError('first_name')" />
                <div v-if="memberFieldErrors.first_name" class="invalid-feedback">{{ memberFieldErrors.first_name }}</div>
              </div>
              <div class="col">
                <label class="form-label small fw-medium" for="member-last-name">{{ t('members.lastName') }}</label>
                <input id="member-last-name" v-model="form.last_name" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.last_name }" required @input="clearMemberFieldError('last_name')" />
                <div v-if="memberFieldErrors.last_name" class="invalid-feedback">{{ memberFieldErrors.last_name }}</div>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium" for="member-display-name">{{ t('members.displayName') }}</label>
              <input id="member-display-name" v-model="form.display_name" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.display_name }" required @input="clearMemberFieldError('display_name')" />
              <div v-if="memberFieldErrors.display_name" class="invalid-feedback">{{ memberFieldErrors.display_name }}</div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-8">
                <label class="form-label small fw-medium" for="member-street-name">{{ t('members.streetName') }}</label>
                <input id="member-street-name" v-model.trim="form.street_name" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.street_name }" required @input="clearMemberFieldError('street_name')" />
                <div v-if="memberFieldErrors.street_name" class="invalid-feedback">{{ memberFieldErrors.street_name }}</div>
              </div>
              <div class="col-4">
                <label class="form-label small fw-medium" for="member-house-number">{{ t('members.houseNumber') }}</label>
                <input id="member-house-number" v-model.trim="form.house_number" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.house_number }" required @input="clearMemberFieldError('house_number')" />
                <div v-if="memberFieldErrors.house_number" class="invalid-feedback">{{ memberFieldErrors.house_number }}</div>
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-4">
                <label class="form-label small fw-medium" for="member-postal-code">{{ t('members.postalCode') }}</label>
                <input id="member-postal-code" v-model.trim="form.postal_code" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.postal_code }" inputmode="numeric" maxlength="5" required @input="clearMemberFieldError('postal_code')" />
                <div v-if="memberFieldErrors.postal_code" class="invalid-feedback">{{ memberFieldErrors.postal_code }}</div>
              </div>
              <div class="col-8">
                <label class="form-label small fw-medium" for="member-city">{{ t('members.city') }}</label>
                <input id="member-city" v-model.trim="form.city" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.city }" required @input="clearMemberFieldError('city')" />
                <div v-if="memberFieldErrors.city" class="invalid-feedback">{{ memberFieldErrors.city }}</div>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium" for="member-country">{{ t('members.country') }}</label>
              <select id="member-country" v-model="form.country_code" class="form-select form-select-sm" :class="{ 'is-invalid': memberFieldErrors.country_code }" required @change="clearMemberFieldError('country_code')">
                <option v-for="country in phoneCountries" :key="country.code" :value="country.code">{{ country.flag }} {{ country.name }}</option>
              </select>
              <div v-if="memberFieldErrors.country_code" class="invalid-feedback">{{ memberFieldErrors.country_code }}</div>
              <div class="form-text">{{ t('members.germanAddressHelp') }}</div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium" for="member-generated-email">{{ t('members.generatedEmail') }}</label>
              <input id="member-generated-email" :value="generatedMemberEmailPreview" class="form-control form-control-sm" type="email" readonly aria-readonly="true" />
              <div class="form-text">{{ t('members.generatedEmailHelp') }}</div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.phone') }}</label>
              <div class="row g-2">
                <div class="col-7">
                  <label class="visually-hidden" for="member-phone-country">{{ t('members.phoneCountry') }}</label>
                  <select id="member-phone-country" v-model="selectedPhoneCountry" class="form-select form-select-sm" data-testid="member-phone-country">
                    <option v-for="country in phoneCountries" :key="country.code" :value="country.code">{{ country.flag }} {{ country.name }} (+{{ country.callingCode }})</option>
                  </select>
                </div>
                <div class="col-5">
                  <label class="visually-hidden" for="member-phone-number">{{ t('members.phoneNumber') }}</label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">+{{ selectedPhoneCallingCode }}</span>
                    <input id="member-phone-number" v-model="phoneNationalNumber" class="form-control" :class="{ 'is-invalid': memberFieldErrors.phone }" type="tel" inputmode="tel" :placeholder="t('members.phonePlaceholder')" @input="clearMemberFieldError('phone')" />
                  </div>
                </div>
              </div>
              <div v-if="memberFieldErrors.phone" class="invalid-feedback d-block">{{ memberFieldErrors.phone }}</div>
              <div class="form-text">{{ t('members.phoneHelp') }}</div>
            </div>
            <fieldset class="mb-1">
              <legend class="form-label small fw-medium mb-2">{{ t('members.membershipType') }}</legend>
              <div class="vstack gap-2">
                <label class="border rounded-3 p-2 d-flex gap-2 align-items-start">
                  <input v-model="form.membership_type" class="form-check-input mt-1" type="radio" value="individual" />
                  <span><strong>{{ t('members.individualContribution') }}</strong><br /><small class="text-muted">{{ t('members.individualContributionDescription') }}</small></span>
                </label>
                <label class="border rounded-3 p-2 d-flex gap-2 align-items-start">
                  <input v-model="form.membership_type" class="form-check-input mt-1" type="radio" value="family" />
                  <span><strong>{{ t('members.familyContribution') }}</strong><br /><small class="text-muted">{{ t('members.familyContributionDescription') }}</small></span>
                </label>
              </div>
            </fieldset>
            <hr class="my-4" />
            <div class="form-check form-switch mb-3">
              <input id="provision-access" v-model="form.provision_access" class="form-check-input" type="checkbox" />
              <label for="provision-access" class="form-check-label fw-medium">{{ t('members.directAccess') }}</label>
              <div class="form-text">{{ t('members.directAccessHelp') }}</div>
            </div>
            <template v-if="form.provision_access">
              <div class="mb-3">
                <label class="form-label small fw-medium">{{ t('members.loginIdentifier') }}</label>
                <input v-model.trim="form.login_identifier" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.login_identifier }" autocomplete="username" @input="clearMemberFieldError('login_identifier')" />
                <div v-if="memberFieldErrors.login_identifier" class="invalid-feedback">{{ memberFieldErrors.login_identifier }}</div>
                <div class="form-text">{{ t('members.loginIdentifierHelp') }}</div>
              </div>
              <div class="mb-3">
                <label class="form-label small fw-medium">{{ t('members.temporaryPassword') }}</label>
                <div class="input-group input-group-sm">
                  <input v-model="form.temporary_password" data-testid="direct-temporary-password" class="form-control" :class="{ 'is-invalid': memberFieldErrors.temporary_password }" :type="showTemporaryPassword ? 'text' : 'password'" autocomplete="new-password" minlength="8" @input="clearMemberFieldError('temporary_password')" />
                  <button data-testid="direct-temporary-password-visibility" class="btn btn-outline-secondary" type="button" @click="showTemporaryPassword = !showTemporaryPassword">
                    <i :class="showTemporaryPassword ? 'bi bi-eye-slash' : 'bi bi-eye'" class="me-1"></i>{{ showTemporaryPassword ? t('members.hidePassword') : t('members.showPassword') }}
                  </button>
                </div>
                <div v-if="memberFieldErrors.temporary_password" class="invalid-feedback d-block">{{ memberFieldErrors.temporary_password }}</div>
                <div data-testid="direct-temporary-password-help" class="form-text">{{ t('members.defaultTemporaryPasswordHelp') }}</div>
              </div>
              <div class="mb-3">
                <label class="form-label small fw-medium">{{ t('members.confirmTemporaryPassword') }}</label>
                <input v-model="temporaryPasswordConfirmation" class="form-control form-control-sm" :class="{ 'is-invalid': memberFieldErrors.temporary_password_confirmation }" type="password" autocomplete="new-password" minlength="8" @input="clearMemberFieldError('temporary_password_confirmation')" />
                <div v-if="memberFieldErrors.temporary_password_confirmation" class="invalid-feedback">{{ memberFieldErrors.temporary_password_confirmation }}</div>
              </div>
            </template>
            </template>
            <template v-else>
              <div class="alert alert-primary small mb-3" role="status">{{ t('members.reviewSubmissionHelp') }}</div>
              <dl class="row small mb-0">
                <dt class="col-5">{{ t('members.memberCode') }}</dt><dd class="col-7">{{ t('members.memberCodeAutoReview') }}</dd>
                <dt class="col-5">{{ t('common.name') }}</dt><dd class="col-7">{{ form.display_name }}</dd>
                <dt class="col-5">{{ t('members.address') }}</dt><dd class="col-7">{{ formattedAddress }}</dd>
                <dt class="col-5">{{ t('common.email') }}</dt><dd class="col-7 text-break">{{ generatedMemberEmailPreview }}</dd>
                <dt class="col-5">{{ t('members.phone') }}</dt><dd class="col-7">{{ completePhoneNumber || '—' }}</dd>
                <dt class="col-5">{{ t('members.membershipType') }}</dt><dd class="col-7">{{ form.membership_type === 'family' ? t('members.familyContribution') : t('members.individualContribution') }}</dd>
                <dt class="col-5">{{ t('members.initialBalance') }}</dt><dd class="col-7">{{ expectedContributionAmount }} €</dd>
                <dt class="col-5">{{ t('members.directAccess') }}</dt><dd class="col-7">{{ form.provision_access ? t('members.accessEnabled') : t('members.accessDisabled') }}</dd>
                <template v-if="form.provision_access">
                  <dt class="col-5">{{ t('members.loginIdentifier') }}</dt><dd class="col-7">{{ form.login_identifier || '—' }}</dd>
                  <dt class="col-5">{{ t('members.temporaryPassword') }}</dt><dd class="col-7">{{ t('members.temporaryPasswordSet') }}</dd>
                </template>
              </dl>
            </template>
          </div>
          <div class="modal-footer">
            <button v-if="reviewMode" type="button" class="btn btn-sm btn-outline-secondary" @click="reviewMode = false">{{ t('common.edit') }}</button>
            <button v-else type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-primary" @click="reviewMode ? confirmCreate() : reviewCreate()" :disabled="saving">
              {{ saving ? t('common.saving') : reviewMode ? t('members.confirmCreateMember') : t('members.reviewSubmission') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Member Modal -->
    <div class="modal fade" id="editMemberModal" tabindex="-1" aria-labelledby="editMemberModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editMemberModalLabel">{{ t('members.editMember') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.memberCode') }}</label>
              <input v-model="editForm.member_code" class="form-control form-control-sm" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">{{ t('members.firstName') }}</label>
                <input v-model="editForm.first_name" class="form-control form-control-sm" />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">{{ t('members.lastName') }}</label>
                <input v-model="editForm.last_name" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.displayName') }}</label>
              <input v-model="editForm.display_name" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.email') }}</label>
              <input v-model="editForm.email" type="email" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.phone') }}</label>
              <input v-model="editForm.phone" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.status') }}</label>
              <select v-model="editForm.status" class="form-select form-select-sm">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
                <option value="resigned">Resigned</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleUpdate" :disabled="saving">
              {{ saving ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteMemberModal" tabindex="-1" aria-labelledby="deleteMemberModalLabel">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteMemberModalLabel">{{ t('common.confirm') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0 small">{{ t('members.deleteMember') }}: <strong>{{ deletingMember?.display_name }}</strong>?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-danger" @click="handleDelete" :disabled="saving">
              {{ saving ? t('common.loading') : t('common.delete') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import * as bootstrap from 'bootstrap'
import { getCountries, getCountryCallingCode, type CountryCode } from 'libphonenumber-js'
import { listMembers, createMember, updateMember, deleteMember, importMembersCsv, exportMembersCsv } from '@/api/membership.api'
import type { MembershipProfileResponse, CreateMemberPayload, UpdateMemberPayload, ImportResult } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'
import { useLocaleStore } from '@/stores/locale.store'
import { useAuthStore } from '@/stores/auth.store'
import ResponsiveDataView from '@/components/ui/ResponsiveDataView.vue'
import MemberInsightsPanel from '@/components/members/MemberInsightsPanel.vue'
import AssistedAccessRecoveryModal from '@/components/members/AssistedAccessRecoveryModal.vue'
import { notifyOperation } from '@/services/operation-notifications'

const localeStore = useLocaleStore()
const authStore = useAuthStore()
const canUseBulkMemberTools = computed(() => authStore.user?.roles.some((role) => ['admin', 'principal_admin'].includes(role)) ?? false)
const canDeleteMembers = computed(() => authStore.user?.roles.some((role) => ['president', 'secretary_general'].includes(role)) ?? false)
const canRecoverMemberAccess = computed(() => authStore.user?.roles.some((role) => ['admin', 'principal_admin', 'president', 'vice_president', 'secretary_general'].includes(role)) ?? false)
const canReadMemberFinance = computed(() => authStore.user?.roles.some((role) => ['admin', 'principal_admin', 'president', 'vice_president', 'treasurer', 'auditor'].includes(role)) ?? false)
const canReadMemberDiscipline = computed(() => authStore.user?.roles.some((role) => ['admin', 'principal_admin', 'president', 'secretary_general', 'censor'].includes(role)) ?? false)
const t = (key: string) => localeStore.t(key)

const loading = ref(true)
const error = ref('')
const members = ref<MembershipProfileResponse[]>([])
const selectedMember = ref<MembershipProfileResponse | null>(null)
const accessRecoveryMember = ref<MembershipProfileResponse | null>(null)
const saving = ref(false)
const searchQuery = ref('')
let searchTimer: ReturnType<typeof setTimeout> | undefined
const deletingMember = ref<MembershipProfileResponse | null>(null)
const memberFieldErrors = ref<Record<string, string>>({})

function setError(err: unknown) {
  error.value = (err as any)?.response?.data?.detail || (err as any)?.message || 'An unexpected error occurred'
}

function selectMember(member: MembershipProfileResponse) {
  selectedMember.value = member
}

function openAccessRecovery(member: MembershipProfileResponse) {
  accessRecoveryMember.value = member
}

const form = ref<CreateMemberPayload>({
  first_name: '',
  last_name: '',
  display_name: '',
  phone: '',
  street_name: '',
  house_number: '',
  postal_code: '',
  city: '',
  country_code: 'DE',
  membership_type: 'individual',
  provision_access: false,
  login_identifier: '',
  temporary_password: 'CombisPass#',
})
const temporaryPasswordConfirmation = ref('CombisPass#')
const showTemporaryPassword = ref(false)
const reviewMode = ref(false)
const selectedPhoneCountry = ref<CountryCode>('DE')
const phoneNationalNumber = ref('')
const selectedPhoneCallingCode = computed(() => getCountryCallingCode(selectedPhoneCountry.value))
const completePhoneNumber = computed(() => {
  const nationalNumber = phoneNationalNumber.value.replace(/[\s()-]/g, '').replace(/^0+/, '')
  return nationalNumber ? `+${selectedPhoneCallingCode.value}${nationalNumber}` : ''
})
const expectedContributionAmount = computed(() => form.value.membership_type === 'family' ? '100' : '60')
const generatedEmailPreviewSuffix = ref(Math.floor(Math.random() * 10_001))
const phoneCountries = computed(() => {
  const displayNames = new Intl.DisplayNames([localeStore.currentLocale], { type: 'region' })
  return getCountries()
    .map((code) => ({
      code,
      callingCode: getCountryCallingCode(code),
      flag: String.fromCodePoint(...code.split('').map((character) => 127397 + character.charCodeAt(0))),
      name: displayNames.of(code) ?? code,
    }))
    .sort((left, right) => left.name.localeCompare(right.name, localeStore.currentLocale))
})
const generatedMemberEmailPreview = computed(() => {
  const source = form.value.login_identifier?.trim() || form.value.display_name.trim()
  const normalized = source.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
  const localPart = normalized.replace(/[^a-z0-9]/g, '').slice(0, 48) || 'member'
  return `${localPart}${generatedEmailPreviewSuffix.value}@combis.org`
})
const formattedAddress = computed(() => `${form.value.street_name} ${form.value.house_number}, ${form.value.postal_code} ${form.value.city}`)

const editForm = ref<UpdateMemberPayload>({})
const editingId = ref<string | null>(null)

const importSelectedFile = ref<File | null>(null)
const importDryRun = ref(true)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)
const importFileInput = ref<HTMLInputElement | null>(null)

const { exportCsv, exporting } = useCsvExport()

function resetImport() {
  importSelectedFile.value = null
  importDryRun.value = true
  importing.value = false
  importResult.value = null
  if (importFileInput.value) importFileInput.value.value = ''
}

function onImportFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  importSelectedFile.value = input.files?.[0] ?? null
  importResult.value = null
}

async function handleImport() {
  if (!importSelectedFile.value) return
  importing.value = true
  try {
    importResult.value = await importMembersCsv(importSelectedFile.value, importDryRun.value)
  } finally { importing.value = false }
}

async function confirmImport() {
  importDryRun.value = false
  await handleImport()
  if (importResult.value && importResult.value.error_count > 0) {
    importDryRun.value = true
  } else {
    await loadMembers()
  }
}

async function exportMembers() {
  try {
    await exportCsv(exportMembersCsv, 'members.csv')
  } catch (err) { setError(err) }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadMembers(query = searchQuery.value) {
  try {
    members.value = await listMembers(query)
  } catch (err) { setError(err) }
  finally { loading.value = false }
}

function scheduleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadMembers(), 250)
}

function clearSearch() {
  searchQuery.value = ''
  void loadMembers('')
}

function resetForm() {
  form.value = { first_name: '', last_name: '', display_name: '', phone: '', street_name: '', house_number: '', postal_code: '', city: '', country_code: 'DE', membership_type: 'individual', provision_access: false, login_identifier: '', temporary_password: 'CombisPass#' }
  generatedEmailPreviewSuffix.value = Math.floor(Math.random() * 10_001)
  temporaryPasswordConfirmation.value = 'CombisPass#'
  showTemporaryPassword.value = false
  reviewMode.value = false
  selectedPhoneCountry.value = 'DE'
  phoneNationalNumber.value = ''
  memberFieldErrors.value = {}
}

function clearMemberFieldError(field: string) {
  if (!memberFieldErrors.value[field]) return
  const next = { ...memberFieldErrors.value }
  delete next[field]
  memberFieldErrors.value = next
}

function validateMemberForm(): boolean {
  const errors: Record<string, string> = {}
  if (!form.value.first_name.trim()) errors.first_name = t('validation.firstNameRequired')
  if (!form.value.last_name.trim()) errors.last_name = t('validation.lastNameRequired')
  if (!form.value.display_name.trim()) errors.display_name = t('validation.displayNameRequired')
  if (!form.value.street_name?.trim()) errors.street_name = t('validation.streetNameRequired')
  if (!form.value.house_number?.trim()) errors.house_number = t('validation.houseNumberRequired')
  if (!form.value.postal_code?.trim()) errors.postal_code = t('validation.postalCodeRequired')
  else if (!/^\d{5}$/.test(form.value.postal_code.trim())) errors.postal_code = t('validation.germanPostalCodeInvalid')
  if (!form.value.city?.trim()) errors.city = t('validation.cityRequired')
  if (!form.value.country_code?.trim()) errors.country_code = t('validation.countryRequired')
  if (phoneNationalNumber.value.trim() && !/^\+[1-9]\d{7,14}$/.test(completePhoneNumber.value)) errors.phone = t('validation.phoneInvalid')
  if (form.value.provision_access) {
    if (!form.value.temporary_password || form.value.temporary_password.length < 8) errors.temporary_password = t('validation.passwordTooShort')
    if (form.value.temporary_password !== temporaryPasswordConfirmation.value) errors.temporary_password_confirmation = t('members.passwordMismatch')
  }
  memberFieldErrors.value = errors
  if (Object.keys(errors).length === 0) return true
  notifyOperation({ level: 'warning', messageKey: 'validation.correctHighlightedFields' })
  return false
}

function reviewCreate() {
  if (!validateMemberForm()) return
  reviewMode.value = true
}

async function confirmCreate() {
  saving.value = true
  try {
    const payload: CreateMemberPayload = {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      display_name: form.value.display_name,
      street_name: form.value.street_name ?? '',
      house_number: form.value.house_number ?? '',
      postal_code: form.value.postal_code ?? '',
      city: form.value.city ?? '',
      country_code: form.value.country_code ?? '',
      membership_type: form.value.membership_type,
      provision_access: Boolean(form.value.provision_access),
    }
    if (completePhoneNumber.value) payload.phone = completePhoneNumber.value
    if (form.value.login_identifier?.trim()) payload.login_identifier = form.value.login_identifier.trim()
    if (form.value.temporary_password) payload.temporary_password = form.value.temporary_password
    await createMember(payload)
    resetForm()
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('createMemberModal')!)
    modal?.hide()
  } catch (err) { setError(err) }
  finally { saving.value = false }
}

function editMember(member: MembershipProfileResponse) {
  editingId.value = member.id
  editForm.value = {
    member_code: member.member_code,
    first_name: member.first_name,
    last_name: member.last_name,
    display_name: member.display_name,
    email: member.email || '',
    phone: member.phone || '',
    status: member.status,
  }
  nextTick(() => {
    const modal = new bootstrap.Modal(document.getElementById('editMemberModal')!)
    modal.show()
  })
}

async function handleUpdate() {
  if (!editingId.value) return
  saving.value = true
  try {
    await updateMember(editingId.value, editForm.value)
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('editMemberModal')!)
    modal?.hide()
  } catch (err) { setError(err) }
  finally { saving.value = false }
}

async function toggleMemberPause(member: MembershipProfileResponse) {
  saving.value = true
  try {
    const isActive = member.status === 'active'
    await updateMember(member.id, { status: isActive ? 'suspended' : 'active' })
    notifyOperation({ level: 'success', messageKey: isActive ? 'members.pauseSuccess' : 'members.reactivateSuccess' })
    await loadMembers()
  } catch (err) {
    setError(err)
    notifyOperation({ level: 'error', messageKey: 'common.error' })
  } finally {
    saving.value = false
  }
}

function confirmDelete(member: MembershipProfileResponse) {
  deletingMember.value = member
  notifyOperation({ level: 'warning', messageKey: 'toast.deleteWarning' })
  nextTick(() => {
    const modal = new bootstrap.Modal(document.getElementById('deleteMemberModal')!)
    modal.show()
  })
}

async function handleDelete() {
  if (!deletingMember.value) return
  saving.value = true
  try {
    await deleteMember(deletingMember.value.id)
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteMemberModal')!)
    modal?.hide()
  } catch (err) { setError(err) }
  finally { saving.value = false; deletingMember.value = null }
}

onMounted(loadMembers)
</script>

<style scoped>
@media (max-width: 767.98px) {
  .members-view :deep(.mobile-data-card__actions) {
    grid-template-columns: 1fr;
  }
}
</style>
