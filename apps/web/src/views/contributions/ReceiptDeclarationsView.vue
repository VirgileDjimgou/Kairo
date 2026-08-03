<template>
  <div class="p-4 p-lg-5 receipt-declarations">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ copy.kicker }}</div>
        <h1 class="h4 fw-bold mb-1">{{ copy.title }}</h1>
        <p class="text-muted mb-0">{{ copy.lead }}</p>
      </div>
      <button class="btn btn-outline-secondary align-self-start" type="button" @click="load" :disabled="loading">
        <i class="bi bi-arrow-clockwise me-1"></i>{{ copy.refresh }}
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="notice" class="alert alert-success">{{ notice }}</div>

    <div class="row g-4">
      <div class="col-xl-4">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold">{{ copy.declareTitle }}</h2>
            <p class="small text-muted">{{ copy.declareLead }}</p>
            <form class="vstack gap-3" @submit.prevent="createAndSubmit">
              <div>
                <label class="form-label small fw-semibold" for="receipt-income-type">{{ t('receipt.incomeType') }}</label>
                <select id="receipt-income-type" v-model="form.income_type" class="form-select" @change="handleIncomeTypeChange">
                  <option value="membership_contribution">{{ t('receipt.incomeType.membershipContribution') }}</option>
                  <option value="donation">{{ t('receipt.incomeType.donation') }}</option>
                  <option value="sponsorship">{{ t('receipt.incomeType.sponsorship') }}</option>
                  <option value="tournament_proceeds">{{ t('receipt.incomeType.tournamentProceeds') }}</option>
                  <option value="other_income">{{ t('receipt.incomeType.otherIncome') }}</option>
                  <option value="disciplinary_payment">{{ t('receipt.incomeType.disciplinaryPayment') }}</option>
                </select>
              </div>
              <template v-if="requiresMember">
              <div class="position-relative">
                <input v-model.trim="memberSearch" class="form-control" :class="{ 'is-invalid': declarationFieldErrors.membership_profile_id }" :placeholder="copy.searchMember" @focus="showMemberResults = true" @input="clearDeclarationFieldError('membership_profile_id')" />
                <div v-if="showMemberResults && memberSearch" class="list-group position-absolute w-100 shadow-sm receipt-member-results">
                  <div v-for="member in filteredMembers.slice(0, 8)" :key="member.id" class="list-group-item d-flex align-items-center gap-2">
                    <button class="btn btn-link text-start text-decoration-none flex-grow-1 p-0" type="button" @click="selectMember(member)">
                      <span class="fw-semibold text-body">{{ member.display_name }}</span><span class="small text-muted ms-2">{{ member.member_code }}</span>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" type="button" :aria-label="copy.viewMemberDetails" @click="openMemberDetails(member)">
                      <i class="bi bi-info-circle" aria-hidden="true"></i><span class="visually-hidden">{{ copy.viewMemberDetails }}</span>
                    </button>
                  </div>
                  <div v-if="filteredMembers.length === 0" class="list-group-item small text-muted">{{ copy.noMemberFound }}</div>
                </div>
              </div>
              <select v-model="form.membership_profile_id" class="form-select" :class="{ 'is-invalid': declarationFieldErrors.membership_profile_id }" :aria-label="copy.chooseMemberFromList" @change="selectMemberById">
                <option value="">{{ copy.chooseMemberFromList }}</option>
                <option v-for="member in members" :key="member.id" :value="member.id">{{ member.display_name }} · {{ member.member_code }}</option>
              </select>
              <div v-if="declarationFieldErrors.membership_profile_id" class="invalid-feedback d-block">{{ declarationFieldErrors.membership_profile_id }}</div>
              <div v-if="selectedMember" class="alert alert-primary small py-2 mb-0 d-flex justify-content-between align-items-center">
                <span>{{ selectedMember.display_name }} ({{ selectedMember.member_code }})</span>
                <button class="btn btn-sm btn-link p-0" type="button" @click="clearMember">{{ copy.changeMember }}</button>
              </div>
              <div v-if="form.income_type === 'disciplinary_payment'">
                <label class="form-label small fw-semibold" for="receipt-disciplinary-record">{{ t('receipt.incomeType.disciplinaryPayment') }}</label>
                <select id="receipt-disciplinary-record" v-model="form.disciplinary_record_id" class="form-select" :class="{ 'is-invalid': declarationFieldErrors.disciplinary_record_id }">
                  <option value="">{{ t('common.select') }}</option><option v-for="record in memberDisciplinaryRecords" :key="record.id" :value="record.id">{{ record.title }} · {{ record.amount }} {{ record.currency }}</option>
                </select>
                <div v-if="declarationFieldErrors.disciplinary_record_id" class="invalid-feedback d-block">{{ declarationFieldErrors.disciplinary_record_id }}</div>
              </div>
              </template>
              <div v-else>
                <label class="form-label small fw-semibold" for="receipt-source-name">{{ t('receipt.sourceName') }}</label>
                <input id="receipt-source-name" v-model.trim="form.source_name" class="form-control" :class="{ 'is-invalid': declarationFieldErrors.source_name }" :placeholder="t('receipt.sourceName')" @input="clearDeclarationFieldError('source_name')" />
                <div v-if="declarationFieldErrors.source_name" class="invalid-feedback d-block">{{ declarationFieldErrors.source_name }}</div>
                <div class="form-text">{{ t('receipt.sourceNameHelp') }}</div>
              </div>
              <div class="row g-2">
                <div class="col-7"><input v-model="form.amount" class="form-control" :class="{ 'is-invalid': declarationFieldErrors.amount }" type="number" min="0.01" step="0.01" :placeholder="copy.amount" @input="clearDeclarationFieldError('amount')" /><div v-if="declarationFieldErrors.amount" class="invalid-feedback">{{ declarationFieldErrors.amount }}</div></div>
                <div class="col-5"><select v-model="form.payment_method" class="form-select"><option value="cash">{{ copy.cash }}</option><option value="check">{{ copy.check }}</option><option value="bank_transfer">{{ copy.transfer }}</option></select></div>
              </div>
              <input v-model="form.reference" class="form-control" :placeholder="copy.reference" />
              <textarea v-model="form.note" class="form-control" rows="3" :placeholder="copy.note"></textarea>
              <button class="btn btn-primary" type="submit" :disabled="saving">{{ saving ? copy.saving : copy.submit }}</button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-8">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold">{{ copy.myTitle }}</h2>
            <div v-if="ownDeclarations.length === 0" class="text-muted small">{{ copy.emptyMine }}</div>
            <div v-else class="vstack gap-2">
              <div v-for="item in ownDeclarations" :key="item.id" class="border rounded-3 p-3 d-flex justify-content-between gap-3">
                <div><div class="fw-semibold">{{ declarationLabel(item) }}</div><div class="small text-muted">{{ incomeTypeLabel(item.income_type) }} · {{ item.amount }} {{ item.currency }} · {{ formatDate(item.received_at) }}</div><div v-if="item.cash_handover_status" class="small mt-2 text-warning-emphasis">{{ handoverStatusLabel(item.cash_handover_status) }}</div></div>
                <div class="vstack gap-2 align-self-start"><span class="badge" :class="badgeClass(item.status)">{{ statusLabel(item.status) }}</span><button v-if="item.cash_handover_status === 'pending_handover'" class="btn btn-sm btn-outline-primary" type="button" @click="reportHandover(item, 'cash')">{{ t('receipt.reportHandover') }}</button></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="detailMember" class="modal d-block receipt-member-modal" tabindex="-1" role="dialog" aria-modal="true" :aria-label="copy.memberDetails" @keydown.esc="closeMemberDetails">
      <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content shadow">
          <div class="modal-header">
            <div>
              <h2 class="modal-title fs-5">{{ copy.memberDetails }}</h2>
              <div class="small text-muted">{{ detailMember.display_name }} · {{ detailMember.member_code }}</div>
            </div>
            <button class="btn-close" type="button" :aria-label="copy.close" @click="closeMemberDetails"></button>
          </div>
          <div class="modal-body">
            <p class="small text-muted">{{ copy.memberDetailsLead }}</p>
            <dl class="row mb-0 receipt-member-details">
              <dt class="col-sm-5">{{ copy.fullName }}</dt><dd class="col-sm-7">{{ detailMember.first_name }} {{ detailMember.last_name }}</dd>
              <dt class="col-sm-5">{{ copy.memberCode }}</dt><dd class="col-sm-7">{{ detailMember.member_code }}</dd>
              <dt class="col-sm-5">{{ copy.email }}</dt><dd class="col-sm-7 text-break">{{ detailMember.email || copy.notProvided }}</dd>
              <dt class="col-sm-5">{{ copy.phone }}</dt><dd class="col-sm-7">{{ detailMember.phone || copy.notProvided }}</dd>
              <dt class="col-sm-5">{{ copy.membershipType }}</dt><dd class="col-sm-7">{{ membershipTypeLabel(detailMember.membership_type) }}</dd>
              <dt class="col-sm-5">{{ copy.status }}</dt><dd class="col-sm-7">{{ membershipStatusLabel(detailMember.status) }}</dd>
              <dt class="col-sm-5">{{ copy.joinedAt }}</dt><dd class="col-sm-7">{{ formatDate(detailMember.joined_at) }}</dd>
            </dl>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" type="button" @click="closeMemberDetails">{{ copy.close }}</button>
            <button class="btn btn-primary" type="button" @click="selectMemberFromDetails">{{ copy.selectMember }}</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="detailMember" class="modal-backdrop show"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  createContributionReceiptDeclaration, listContributionReceiptDeclarationMemberOptions,
  listMyContributionReceiptDeclarations, submitContributionReceiptDeclaration,
  reportContributionReceiptHandover,
  type ContributionReceiptDeclarationResponse, type ContributionReceiptMemberOption, type FinancialIncomeType,
} from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import { notifyOperation } from '@/services/operation-notifications'
import { listDisciplinaryRecords, type DisciplinaryRecordResponse } from '@/api/disciplinary.api'

const locale = useLocaleStore()
const t = locale.t
const members = ref<ContributionReceiptMemberOption[]>([])
const ownDeclarations = ref<ContributionReceiptDeclarationResponse[]>([])
const disciplinaryRecords = ref<DisciplinaryRecordResponse[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const notice = ref('')
const declarationFieldErrors = ref<Record<string, string>>({})
const form = ref<{ membership_profile_id: string; income_type: FinancialIncomeType; source_name: string; disciplinary_record_id: string; amount: string; payment_method: string; reference: string; note: string }>({ membership_profile_id: '', income_type: 'membership_contribution', source_name: '', disciplinary_record_id: '', amount: '', payment_method: 'cash', reference: '', note: '' })
const memberSearch = ref('')
const showMemberResults = ref(false)
const detailMember = ref<ContributionReceiptMemberOption | null>(null)
const memberById = computed(() => Object.fromEntries(members.value.map((member) => [member.id, member])))
const filteredMembers = computed(() => {
  const query = memberSearch.value.toLocaleLowerCase()
  if (!query) return members.value
  return members.value.filter((member) => `${member.display_name} ${member.member_code}`.toLocaleLowerCase().includes(query))
})
const selectedMember = computed(() => members.value.find((member) => member.id === form.value.membership_profile_id) ?? null)
const requiresMember = computed(() => ['membership_contribution', 'disciplinary_payment'].includes(form.value.income_type))
const memberDisciplinaryRecords = computed(() => disciplinaryRecords.value.filter((record) => record.membership_profile_id === form.value.membership_profile_id && ['open', 'under_review'].includes(record.status)))
const copy = computed(() => {
  const fr = locale.currentLocale === 'fr'
  const de = locale.currentLocale === 'de'
  return {
    kicker: de ? 'Finanzmeldung' : fr ? 'Déclaration financière' : 'Financial declaration',
    title: de ? 'Erhaltene Zahlung melden' : fr ? 'Déclarer un encaissement reçu' : 'Declare a received payment',
    lead: de ? 'Die Buchhaltung wird erst nach der Bestätigung durch die Schatzmeisterei aktualisiert.' : fr ? 'La comptabilité officielle ne sera modifiée qu’après validation par le trésorier.' : 'Official records change only after treasurer validation.',
    refresh: de ? 'Aktualisieren' : fr ? 'Actualiser' : 'Refresh', declareTitle: de ? 'Neue Meldung' : fr ? 'Nouvelle déclaration' : 'New declaration',
    declareLead: de ? 'Melden Sie eine persönlich erhaltene Zahlung.' : fr ? 'Signalez un paiement reçu en main propre.' : 'Report a payment received in person.',
    chooseMember: de ? 'Mitglied auswählen' : fr ? 'Choisir le membre' : 'Choose member', chooseMemberFromList: de ? 'Aus vollständiger Liste auswählen' : fr ? 'Choisir dans la liste complète' : 'Choose from the full list', searchMember: de ? 'Mitglied suchen…' : fr ? 'Rechercher un membre…' : 'Search a member…', noMemberFound: de ? 'Kein Mitglied gefunden.' : fr ? 'Aucun membre trouvé.' : 'No member found.', changeMember: de ? 'Ändern' : fr ? 'Modifier' : 'Change', viewMemberDetails: de ? 'Mitgliedsinformationen anzeigen' : fr ? 'Voir les informations du membre' : 'View member information', memberDetails: de ? 'Mitgliedsinformationen' : fr ? 'Informations du membre' : 'Member information', memberDetailsLead: de ? 'Diese Informationen sind schreibgeschützt.' : fr ? 'Ces informations sont consultables en lecture seule.' : 'This information is read-only.', fullName: de ? 'Vollständiger Name' : fr ? 'Nom complet' : 'Full name', memberCode: de ? 'Mitgliedsnummer' : fr ? 'Matricule' : 'Member code', email: 'E-mail', phone: de ? 'Telefon' : fr ? 'Téléphone' : 'Phone', membershipType: de ? 'Mitgliedschaft' : fr ? 'Type de membre' : 'Membership type', status: de ? 'Status' : fr ? 'Statut' : 'Status', joinedAt: de ? 'Beitrittsdatum' : fr ? 'Inscrit le' : 'Joined on', notProvided: de ? 'Nicht angegeben' : fr ? 'Non renseigné' : 'Not provided', close: de ? 'Schließen' : fr ? 'Fermer' : 'Close', selectMember: de ? 'Dieses Mitglied auswählen' : fr ? 'Sélectionner ce membre' : 'Select this member', amount: de ? 'Betrag' : fr ? 'Montant' : 'Amount', cash: de ? 'Bar' : fr ? 'Espèces' : 'Cash', check: de ? 'Scheck' : fr ? 'Chèque' : 'Check', transfer: de ? 'Überweisung' : fr ? 'Virement' : 'Transfer', reference: de ? 'Referenz (optional)' : fr ? 'Référence (facultative)' : 'Reference (optional)', note: de ? 'Notiz (optional)' : fr ? 'Note (facultative)' : 'Note (optional)', saving: de ? 'Speichern…' : fr ? 'Envoi…' : 'Saving…', submit: de ? 'Meldung einreichen' : fr ? 'Soumettre la déclaration' : 'Submit declaration',
    queueTitle: de ? 'Zu bestätigende Meldungen' : fr ? 'Encaissements à valider' : 'Receipts awaiting validation', queueLead: de ? 'Nur die Schatzmeisterei kann offizielle Zahlungen erstellen.' : fr ? 'Seul le trésorier crée le paiement officiel.' : 'Only the treasurer creates the official payment.', emptyQueue: de ? 'Keine ausstehende Meldung.' : fr ? 'Aucune déclaration en attente.' : 'No pending declarations.', validate: de ? 'Bestätigen' : fr ? 'Valider' : 'Validate', reject: de ? 'Ablehnen' : fr ? 'Rejeter' : 'Reject', myTitle: de ? 'Meine Meldungen' : fr ? 'Mes déclarations' : 'My declarations', emptyMine: de ? 'Noch keine Meldung.' : fr ? 'Aucune déclaration pour le moment.' : 'No declarations yet.',
    loadFailed: de ? 'Die Meldungen konnten nicht geladen werden.' : fr ? 'Impossible de charger les déclarations.' : 'Unable to load receipt declarations.', submitFailed: de ? 'Die Meldung konnte nicht eingereicht werden.' : fr ? 'Impossible de soumettre la déclaration.' : 'Unable to submit receipt declaration.', processFailed: de ? 'Die Meldung konnte nicht traitée werden.' : fr ? 'Impossible de traiter la déclaration.' : 'Unable to process declaration.', submitted: de ? 'Meldung eingereicht.' : fr ? 'Déclaration soumise.' : 'Declaration submitted.', validated: de ? 'Zahlung bestätigt.' : fr ? 'Encaissement validé.' : 'Receipt validated.', rejected: de ? 'Zahlung abgelehnt.' : fr ? 'Encaissement rejeté.' : 'Receipt rejected.', noOutstanding: de ? 'Für dieses Mitglied wurde keine offene Beitragsforderung gefunden.' : fr ? 'Aucune cotisation impayée n’a été trouvée pour ce membre.' : 'No outstanding contribution was found for this member.',
  }
})
function memberLabel(id: string | null) { if (!id) return t('receipt.externalIncome'); const member = memberById.value[id]; return member ? `${member.display_name} (${member.member_code})` : id }
function incomeTypeLabel(incomeType: FinancialIncomeType) {
  const keys: Record<FinancialIncomeType, string> = {
    membership_contribution: 'receipt.incomeType.membershipContribution', donation: 'receipt.incomeType.donation', sponsorship: 'receipt.incomeType.sponsorship', tournament_proceeds: 'receipt.incomeType.tournamentProceeds', other_income: 'receipt.incomeType.otherIncome', disciplinary_payment: 'receipt.incomeType.disciplinaryPayment',
  }
  return t(keys[incomeType])
}
function declarationLabel(item: ContributionReceiptDeclarationResponse) { return item.income_type === 'membership_contribution' ? memberLabel(item.membership_profile_id) : (item.source_name || t('receipt.externalIncome')) }
function selectMember(member: ContributionReceiptMemberOption) { form.value.membership_profile_id = member.id; memberSearch.value = member.display_name; showMemberResults.value = false; clearDeclarationFieldError('membership_profile_id') }
function selectMemberById() { const member = selectedMember.value; if (member) selectMember(member); else clearMember() }
function clearMember() { form.value.membership_profile_id = ''; memberSearch.value = ''; showMemberResults.value = true }
function handleIncomeTypeChange() {
  declarationFieldErrors.value = {}
  form.value.disciplinary_record_id = ''
  if (!requiresMember.value) clearMember()
  if (requiresMember.value) form.value.source_name = ''
}
function openMemberDetails(member: ContributionReceiptMemberOption) { detailMember.value = member; showMemberResults.value = false }
function closeMemberDetails() { detailMember.value = null }
function selectMemberFromDetails() { if (detailMember.value) selectMember(detailMember.value); closeMemberDetails() }
function formatDate(value: string) { return new Date(value).toLocaleDateString(locale.currentLocale === 'fr' ? 'fr-FR' : locale.currentLocale === 'de' ? 'de-DE' : 'en-US') }
function membershipTypeLabel(value: string) {
  const labels = locale.currentLocale === 'fr' ? { individual: 'Individuel', family: 'Famille' } : locale.currentLocale === 'de' ? { individual: 'Einzelmitglied', family: 'Familie' } : { individual: 'Individual', family: 'Family' }
  return labels[value as keyof typeof labels] || value
}
function membershipStatusLabel(value: string) {
  const labels = locale.currentLocale === 'fr' ? { active: 'Actif', inactive: 'Inactif', suspended: 'Suspendu', resigned: 'Démissionnaire' } : locale.currentLocale === 'de' ? { active: 'Aktiv', inactive: 'Inaktiv', suspended: 'Gesperrt', resigned: 'Ausgetreten' } : { active: 'Active', inactive: 'Inactive', suspended: 'Suspended', resigned: 'Resigned' }
  return labels[value as keyof typeof labels] || value
}
function statusLabel(status: string) {
  const labels = locale.currentLocale === 'fr'
    ? { draft: 'Brouillon', submitted: 'En attente', clarification_requested: 'Précision demandée', validated: 'Validé', partially_validated: 'Partiellement validé', rejected: 'Rejeté', cancelled: 'Annulé' }
    : locale.currentLocale === 'de'
      ? { draft: 'Entwurf', submitted: 'Ausstehend', clarification_requested: 'Klärung erforderlich', validated: 'Bestätigt', partially_validated: 'Teilweise bestätigt', rejected: 'Abgelehnt', cancelled: 'Storniert' }
      : { draft: 'Draft', submitted: 'Pending', clarification_requested: 'Clarification requested', validated: 'Validated', partially_validated: 'Partially validated', rejected: 'Rejected', cancelled: 'Cancelled' }
  return labels[status as keyof typeof labels] || status
}
function badgeClass(status: string) { return ({ submitted: 'text-bg-warning', validated: 'text-bg-success', partially_validated: 'text-bg-success', rejected: 'text-bg-danger', clarification_requested: 'text-bg-info', cancelled: 'text-bg-secondary' }[status] || 'text-bg-secondary') }
function handoverStatusLabel(value: ContributionReceiptDeclarationResponse['cash_handover_status']) { return value === 'handover_reported' ? t('receipt.handoverReported') : value === 'received_in_treasury' ? t('receipt.treasuryReceived') : t('receipt.cashPending') }
async function reportHandover(item: ContributionReceiptDeclarationResponse, method: 'cash' | 'bank_transfer') { try { await reportContributionReceiptHandover(item.id, { method }); notice.value = t('receipt.handoverReported'); await load() } catch (err) { error.value = err instanceof Error ? err.message : copy.value.processFailed } }
async function load() { loading.value = true; error.value = ''; try { const [memberRows, declarationRows] = await Promise.all([listContributionReceiptDeclarationMemberOptions(), listMyContributionReceiptDeclarations()]); members.value = memberRows; ownDeclarations.value = declarationRows; try { disciplinaryRecords.value = await listDisciplinaryRecords() } catch { disciplinaryRecords.value = [] } } catch (err) { error.value = err instanceof Error ? err.message : copy.value.loadFailed } finally { loading.value = false } }
function clearDeclarationFieldError(field: string) {
  if (!declarationFieldErrors.value[field]) return
  const next = { ...declarationFieldErrors.value }
  delete next[field]
  declarationFieldErrors.value = next
}

function validateDeclarationForm(): boolean {
  const errors: Record<string, string> = {}
  if (requiresMember.value && !form.value.membership_profile_id) errors.membership_profile_id = locale.t('validation.memberRequired')
  if (form.value.income_type === 'disciplinary_payment' && !form.value.disciplinary_record_id) errors.disciplinary_record_id = t('receipt.incomeType.disciplinaryPayment')
  if (!requiresMember.value && !form.value.source_name.trim()) errors.source_name = t('receipt.sourceRequired')
  if (!form.value.amount || !Number.isFinite(Number(form.value.amount)) || Number(form.value.amount) <= 0) errors.amount = locale.t('validation.amountRequired')
  declarationFieldErrors.value = errors
  if (Object.keys(errors).length === 0) return true
  notifyOperation({ level: 'warning', messageKey: 'validation.correctHighlightedFields' })
  return false
}

async function createAndSubmit() { if (!validateDeclarationForm()) return; saving.value = true; error.value = ''; try { const item = await createContributionReceiptDeclaration({ ...form.value, membership_profile_id: requiresMember.value ? form.value.membership_profile_id : null, source_name: requiresMember.value ? null : form.value.source_name, disciplinary_record_id: form.value.disciplinary_record_id || null, reference: form.value.reference || null, note: form.value.note || null }); await submitContributionReceiptDeclaration(item.id); form.value = { membership_profile_id: '', income_type: 'membership_contribution', source_name: '', disciplinary_record_id: '', amount: '', payment_method: 'cash', reference: '', note: '' }; memberSearch.value = ''; declarationFieldErrors.value = {}; notice.value = copy.value.submitted; await load() } catch (err) { error.value = err instanceof Error ? err.message : copy.value.submitFailed } finally { saving.value = false } }
onMounted(load)
</script>

<style scoped>
.receipt-declarations { max-width: 1240px; }
.receipt-member-results { z-index: 1050; max-height: 260px; overflow-y: auto; }
.receipt-member-modal { z-index: 1060; }
.receipt-member-details dt { color: var(--bs-secondary-color); font-weight: 600; }
.receipt-member-details dd { margin-bottom: 1rem; }
</style>
