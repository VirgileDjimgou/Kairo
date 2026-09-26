<template>
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
</template>

<script setup lang="ts">
import { ref } from 'vue'
import * as bootstrap from 'bootstrap'
import { createMember } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useMemberForm } from '../composables/useMemberForm'
import { memberErrorMessage } from '../memberErrors'

const emit = defineEmits<{
  created: []
  error: [message: string]
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const {
  form,
  temporaryPasswordConfirmation,
  showTemporaryPassword,
  selectedPhoneCountry,
  phoneNationalNumber,
  memberFieldErrors,
  selectedPhoneCallingCode,
  completePhoneNumber,
  expectedContributionAmount,
  phoneCountries,
  generatedMemberEmailPreview,
  formattedAddress,
  resetForm,
  clearMemberFieldError,
  validateMemberForm,
  buildPayload,
} = useMemberForm()

const reviewMode = ref(false)
const saving = ref(false)

function reviewCreate() {
  if (!validateMemberForm()) return
  reviewMode.value = true
}

async function confirmCreate() {
  saving.value = true
  try {
    await createMember(buildPayload())
    resetForm()
    reviewMode.value = false
    const modal = bootstrap.Modal.getInstance(document.getElementById('createMemberModal')!)
    modal?.hide()
    emit('created')
  } catch (err) {
    emit('error', memberErrorMessage(err))
  } finally {
    saving.value = false
  }
}
</script>
