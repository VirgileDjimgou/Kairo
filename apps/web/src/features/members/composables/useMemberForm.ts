import { computed, ref } from 'vue'
import { getCountries, getCountryCallingCode, type CountryCode } from 'libphonenumber-js'
import type { CreateMemberPayload } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { notifyOperation } from '@/services/operation-notifications'

const DEFAULT_TEMPORARY_PASSWORD = 'CombisPass#'

function defaultForm(): CreateMemberPayload {
  return {
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
    temporary_password: DEFAULT_TEMPORARY_PASSWORD,
  }
}

/**
 * Create-member form state, validation and payload assembly.
 *
 * Presentation and client-side validation only; the backend remains the
 * authority for uniqueness, access provisioning and member codes.
 */
export function useMemberForm() {
  const localeStore = useLocaleStore()
  const t = (key: string) => localeStore.t(key)

  const form = ref<CreateMemberPayload>(defaultForm())
  const temporaryPasswordConfirmation = ref(DEFAULT_TEMPORARY_PASSWORD)
  const showTemporaryPassword = ref(false)
  const selectedPhoneCountry = ref<CountryCode>('DE')
  const phoneNationalNumber = ref('')
  const memberFieldErrors = ref<Record<string, string>>({})
  const generatedEmailPreviewSuffix = ref(Math.floor(Math.random() * 10_001))

  const selectedPhoneCallingCode = computed(() => getCountryCallingCode(selectedPhoneCountry.value))
  const completePhoneNumber = computed(() => {
    const nationalNumber = phoneNationalNumber.value.replace(/[\s()-]/g, '').replace(/^0+/, '')
    return nationalNumber ? `+${selectedPhoneCallingCode.value}${nationalNumber}` : ''
  })
  const expectedContributionAmount = computed(() => form.value.membership_type === 'family' ? '100' : '60')
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

  function resetForm() {
    form.value = defaultForm()
    generatedEmailPreviewSuffix.value = Math.floor(Math.random() * 10_001)
    temporaryPasswordConfirmation.value = DEFAULT_TEMPORARY_PASSWORD
    showTemporaryPassword.value = false
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

  function buildPayload(): CreateMemberPayload {
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
    return payload
  }

  return {
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
  }
}
