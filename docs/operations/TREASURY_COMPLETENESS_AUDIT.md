# Treasury, Contributions And Budget Readiness Audit

> **Delivery record.** This document records the F0–F3 implementation history and
> evidence. For the current operational assessment and the remaining P1/P2 gaps, see
> [`TREASURY_OPERATIONAL_AUDIT.md`](./TREASURY_OPERATIONAL_AUDIT.md).

Date: 2026-11-12
Scope: **finance only** — treasury, contributions, receipts and custody, expenses,
budget, auditor (commissaire aux comptes) oversight, finance roles and exports.
Everything outside this perimeter (membership register, meetings, events, documents,
communication) is deliberately deferred and is **not** part of this audit.

Method: source review of `services/api/app/modules/finance/`,
`services/api/app/modules/contributions/`, `core/capabilities.py`,
`modules/tenancy/role_catalog.py`, the finance routes and the Vue treasurer/auditor
workspaces. Every finding below was verified in code, not inferred from documentation.
This document is authoritative for finance decisions and complements the general
production audit in `AUDIT_MISE_EN_PRODUCTION_ASSOCIATION.md`.

Verdict: **the treasury is complete for day-to-day operation and audit.** All six
blocking findings are closed, and F3 closes the audit-pack gaps: replay-safe import,
a chronological finance journal, no disciplinary data in finance reports, and ledger
ownership of exports. What remains is governance (expense approval, segregation of
duties) and minor refinements (export translation, scheduled overdue refresh).

## Delivery status

| Finding | Scope | Status |
| --- | --- | --- |
| P0-1 Ledger writable and destructible | F0 | **Implemented** — payments are the only source of a balance; deletion is refused when payments exist; payments are idempotent and reversible |
| P0-4 Currency hardcoded to EUR | F0 | **Implemented** — organization currency setting, inherited and enforced, used by reports; locked once financial records exist |
| P0-6 Member deletion destroys the ledger | F0 | **Implemented** — a member with financial or disciplinary history cannot be deleted |
| P0-2 Expenses are write-only | F1 | **Implemented** — list, filter, detail, CSV/XLSX export, UI ledger and auditor access |
| P0-3 Auditor cannot see budget or expenses | F1 | **Implemented** — budget reads use `finance:tenant_read`; the auditor workspace shows the budget, expenses and exercise status |
| P1-3 Expenses have no supporting document | F1 | **Implemented** — PDF/JPEG/PNG receipt upload and download, tenant-scoped, audit-logged |
| P1-2 No period close | F1 | **Implemented** — close/reopen an exercise; every financial write in a closed year returns 409 |
| P0-5 No treasury position | F2 | **Implemented** — cash and bank accounts, opening balances, prior-year carry and closing position |
| P1-1 No planned/voted budget | F2 | **Implemented** — per-category plan, planned totals and variance against actual |
| P1-5 Payment dated at validation time | F2 | **Implemented** — validated receipts now use the real `received_at` date |
| P1-7 No numbered receipt | F2 | **Implemented** — per-tenant/per-year sequence and downloadable PDF quittance |
| P1-6 Import duplicates and unexplained balances | F3 | **Implemented** — one contribution per member/exercise, import skips existing rows, imported balances are backed by idempotent payments |
| P1-9 Disciplinary data in the finance export | F3 | **Implemented** — sanctions removed from XLSX, PDF and WhatsApp finance reports |
| P1-11 No finance journal export | F3 | **Implemented** — chronological CSV journal (payments, expenses, receipts, opening balances); legacy report labels remain French |
| P1-12 Treasurer cannot export the ledger | F3 | **Implemented** — `finance:tenant_read` with an audit event on every export |

F0 evidence: migration `0037_finance_ledger_integrity.py`, regression suite
`services/api/tests/test_finance_integrity.py` (6 tests).

F1 evidence: migration `0038_expense_attachments_and_periods.py`, regression suite
`services/api/tests/test_treasury_audit.py` (4 tests).

F2 evidence: migrations `0039_numbered_payment_receipts.py`,
`0040_treasury_accounts_and_opening_balances.py`,
`0041_planned_budget_lines.py`, regression suite
`services/api/tests/test_treasury_f2.py` (4 tests).

F3 evidence: regression suite `services/api/tests/test_treasury_f3.py` (3 tests,
no schema change). Full API suite 439 passed, web type-check and production build
passed, OpenAPI and generated clients regenerated.

Deliberately deferred: the **expense approval workflow** and **segregation of duties
on receipt processing** require explicit governance decisions; the auditor remains
read-only. Export translation and a scheduled overdue refresh are refinements, not
blockers.





---

## 1. What is already implemented and works

### 1.1 Money-in lifecycle

| Step | Implemented behaviour |
| --- | --- |
| Expected contribution | One record per member and year: `expected_amount`, `paid_amount`, `balance`, `currency`, `status`, `due_date` |
| Payment recording | Amount, date, method (cash, bank transfer, card, check, other), reference, actor, audit event, domain event |
| Declaration (cash received by an office holder) | Draft, submit, edit while draft, cancel; member or non-member income |
| Treasurer review | Validate, partially validate, reject, request clarification; required note on rejection |
| Custody | Handover report by declarant, reminder delay, reminder history, treasury confirmation |
| Non-member income | Donations, sponsorship, tournament proceeds, other income, disciplinary payments |
| Dues follow-up | Single and batch reminders, overdue / due-soon filters, per-member email, delivery status history |

### 1.2 Money-out and reporting

- Expenses: amount, category, date, payee, method, reference, actor, audit event.
- Annual summary: realized income by category, realized expenses by category,
  aggregate balance, six most recent expenses.
- Member finance report: XLSX, PDF and WhatsApp summary, with expected, paid, balance,
  status and open sanctions per member.
- CSV exports: raw contributions (admin only) and finance report (audit roles).
- Audit trail: create, update, delete, payment, expense, receipt processing, custody
  and export events.

### 1.3 Role matrix (verified in `role_catalog.py` and route guards)

| Action | Member | Treasurer | Auditor | President | Principal admin |
| --- | --- | --- | --- | --- | --- |
| View own contributions / statement | yes | yes | yes | yes | yes |
| View tenant contributions, payments, reminders | no | yes | yes | yes | yes |
| Create / update / delete contribution | no | yes | no | no | yes |
| Record payment | no | yes | no | no | yes |
| Declare receipt | no | yes | yes | yes | yes |
| Process receipt (validate / reject) | no | yes | no | no | yes |
| Report handover / confirm treasury receipt | declarant | yes | yes | yes | yes |
| Record expense | no | yes | no | no | no |
| View annual budget | no | yes | **no** | **no** | yes |
| Export member finance report | no | yes | yes | yes | yes |
| Export raw contributions CSV | no | **no** | no | no | yes |

The auditor is genuinely read-only on finance (no write capability), which is the
correct starting point.

---

## 2. Blocking defects (P0) — fix before recording real money

### P0-1. The contribution ledger is writable and destructible

Three independent paths let the amount side of the ledger drift from the payment side:

1. `ContributionRecordCreate` and `ContributionRecordUpdate` accept `paid_amount` and
   `status` directly. A contribution can be created as fully paid with **no payment
   record**, or edited to any paid amount afterwards.
2. `DELETE /contributions/{id}` hard-deletes the record and cascades every payment.
   It is wired in `AdminContributionsView.vue` (delete button + confirm modal). The
   audit event records only year and member, not amounts or destroyed payments.
3. `record_payment` performs a read-modify-write on `paid_amount` with no row lock, no
   idempotency key and no overpayment guard. Two concurrent payments can lose an
   increment in the aggregate.

Impact: the balance shown to the committee, the member statement and the audit export
can all disagree with the actual payments, and a paid contribution can be erased
without a trace of what was erased. For an association this is the difference between
books and notes.

Minimal fix: make `paid_amount` and `status` derived values (recomputed from payments
only), never accept them without a matching payment, refuse deletion when payments
exist, record reversed amounts instead of deleting, lock the contribution row when
recording a payment, and make payment creation idempotent.

Delivered in F0: `paid_amount` and `status` are recomputed from the payment ledger on
every write; a create with a paid amount materialises an opening-balance payment; a
PATCH on `paid_amount` is rejected and a contradictory `status` returns 422; deleting
a contribution with payments returns 409; `POST /contributions/payments/{id}/reverse`
keeps the payment with a reason and recomputes the balance; payment creation takes a
row lock and accepts an `idempotency_key` backed by a unique constraint.

### P0-2. Expenses can be created but never reviewed

`POST /contributions/expenses` exists, but there is **no endpoint to list, filter,
read, export or correct expenses**. The only read is `recent_expenses` (the six most
recent rows) inside the annual budget payload, which itself is treasurer-only.

Impact: the treasurer cannot review the expense ledger, produce an expense report for
the committee, or answer an auditor's question about a past invoice. The auditor
cannot see expenses at all. A treasury module where outflows are write-only is not
operational.

Minimal fix: list (year, category, pagination), detail and export endpoints for
expenses, plus a reversal path; no editing of posted expenses.

Delivered in F1: `GET /contributions/expenses` (year, category, limit, offset),
`GET /contributions/expenses/{id}`, `GET /contributions/expenses/export?format=csv|xlsx`,
a treasurer/auditor expense ledger in the PWA with category filter and exports, and an
audit event on every expense export.

### P0-3. The auditor cannot see the budget or the expenses

`GET /contributions/annual-budget` requires `finance:expenses_write`, i.e. the
treasurer capability. The auditor holds `finance:tenant_read` and `finance:audit` only.
The Vue workspace mirrors this: `useFinanceWorkspace.ts` loads the budget only when
`isTreasurer` is true.

Impact: the commissaire aux comptes can check member balances but cannot compare the
voted budget with realized income and expenses, which is the core of the mandate.

Minimal fix: authorise the budget and expense reads through `finance:tenant_read` (or
`finance:audit`), and show the budget in the auditor workspace read-only.

Delivered in F1: the annual budget now requires `finance:tenant_read`, the auditor and
president can read it, and the auditor workspace displays the budget, the expense
ledger, attachments and the exercise status without any write action.

### P0-4. Currency is hardcoded to EUR and never validated

- Every finance model and schema defaults to `"EUR"`.
- No tenant setting exists for currency.
- The XLSX export hardcodes `"Cotisation attendue (EUR)"` and the `"EUR"` number
  format; the auditor view prints `EUR` in the template; the expense form labels the
  amount `(EUR)`.
- Payments carry their own currency, unrelated to the contribution currency.
- The budget sums all amounts without checking that they share one currency.

Impact: for a Swiss association, every report is labelled in the wrong currency, and a
multi-currency tenant would produce meaningless totals.

Minimal fix: one tenant currency (default CHF or EUR), inherited by every record,
rejected on mismatch, and used by exports and labels instead of literals.

Delivered in F0: `tenants.settings_json.currency` is exposed through tenant settings
and `/auth/me`; contributions, payments, expenses and receipt declarations inherit it
and reject a different currency with 422; the budget exposes and enforces a single
currency; XLSX/PDF/WhatsApp exports and the finance UI use the organization currency;
the currency cannot change once a financial record exists (409, with an audit event).

### P0-5. The displayed "treasury balance" is not a treasury position

`AnnualBudgetResponse.available_balance` is computed as `income − expenses` for the
selected year only. There is no opening balance, no prior-year carry, no cash-box vs
bank account dimension, and no transfer between accounts.

Impact: an association with reserves, a cash box and a bank account will read a
"remaining treasury balance" that does not match either account. The treasurer cannot
present a credible cash position at the general assembly.

Minimal fix: an opening balance per year and account, a computed position
(opening + inflows − outflows) per account, and a rename of the current field to "net
flow of the year" until the position exists.

Delivered in F2: default cash and bank accounts, opening balance per account and year,
automatic prior-year carry, per-account inflows/outflows/closing and totals via
`GET /contributions/treasury-position`; the PWA shows the position to the treasurer and
the auditor, and the treasurer can set opening balances. `available_balance` remains a
net-flow indicator, now complemented by the real closing position.

### P0-6. Deleting a member destroys the financial record

`membership_profiles` is referenced with `ON DELETE CASCADE` by
`contribution_records`, `payment_records` (through contributions),
`contribution_reminders` and `contribution_receipt_declarations`, and by
`disciplinary_records`. `DELETE /membership/{id}` is a hard delete exposed in the UI.

Impact: removing a member erases their contributions, payments, custody declarations
and sanctions. Audit evidence disappears with the member, including money already
counted in previous years.

Minimal fix: archive/anonymise members instead of deleting them; block deletion when
financial records exist; keep member code and amounts.

Delivered in F0: `DELETE /memberships/{id}` returns 409 when the member has
contributions, payments, reminders, receipt declarations or disciplinary records; the
message points to the resigned/inactive status; an empty profile can still be deleted.

---

## 3. Important gaps (P1) — needed to actually run the treasury

| # | Gap | Consequence |
| --- | --- | --- |
| P1-1 | **There is no budget, only a realized summary.** No planned amount per category, no voted budget, no budget-vs-actual, no version per year | The treasurer cannot record the budget approved by the assembly nor explain variances |
| P1-2 | **No period close.** Validated contributions and expenses stay editable for ever | A signed exercise can change after the auditor reviewed it |
| P1-3 | **Expenses have no supporting document and no approval trail** | The auditor cannot tie an amount to an invoice; no second pair of eyes |
| P1-4 | **Expense categories are a fixed enum of six values** (equipment, fuel, tournament, cultural, administration, other) | Insurance, rent, bank fees, referees, training cannot be classified, so the budget analysis is wrong |
| P1-5 | **Validation dates the payment at processing time**, not at receipt time (`paid_at = now` in `process_receipt_declaration`) | Cash received on 31 December and validated on 2 January lands in the next exercise |
| P1-6 | **Migration import writes paid amounts without payments**, has no upsert, and no unique constraint on (member, year) | Re-running the import duplicates the ledger and creates balances no payment can explain |
| P1-7 | **No numbered receipt / quittance** for a cash payment | Many associations and fiduciaries require a numbered receipt per cash collection |
| P1-8 | **No segregation of duties on receipt processing**: the treasurer holds both declare and process; nothing prevents validating and closing one's own receipt | The main internal control of the cash cycle can be bypassed by the person it is meant to check |
| P1-9 | **The finance export contains disciplinary amounts** for every member, while the auditor has no disciplinary read capability | Data minimisation breach: a finance role receives sanction data |
| P1-10 | **Reminders depend on the member's own email** and skip any record whose status is `paid` even when a balance remains | Members without email, minors' guardians and inconsistent statuses are never reached |
| P1-11 | **Exports are French-only and currency-hardcoded**; there is no finance journal export (chronological audit pack) | A German or English committee receives French documents; the auditor must assemble evidence by hand |
| P1-12 | **The treasurer cannot export the raw contribution CSV** (`/export` requires tenant administration) while the platform admin can | The ledger owner depends on an administrator for a basic export |
| P1-13 | **`overdue` is not refreshed by a scheduler**: status is derived on every write (F0), but a contribution that becomes late with no subsequent write keeps its last status | Filters can lag until the next write |

Delivered across F1 to F3: P1-1 (planned budget and variance), P1-2 (period close),
P1-3 (supporting receipts), P1-5 (real receipt date), P1-6 (replay-safe import),
P1-7 (numbered receipts and PDF quittance), P1-9 (no disciplinary data in finance
reports), P1-11 (chronological journal) and P1-12 (ledger export permissions).
Remaining: P1-4 (tenant-configurable expense categories), P1-8 (segregation of duties
on receipt processing), P1-10 (reminder fallback, blocked by guardian fields), the
translation of legacy report labels and P1-13 (scheduled overdue refresh). The expense
**approval** step also remains open because it needs an explicit governance decision on
who signs off; the auditor must stay read-only.

---

## 4. Explicitly deferred (not needed for the treasury to work)

Online payments and SEPA mandates, bank reconciliation (CAMT/CSV import and matching),
transfers between cash and bank, fiduciary/ERP export formats, multi-year member
statements, payment reminder letters as PDF, tenant-configurable document templates,
and any redesign of the finance UI. These are improvements, not prerequisites.

---

## 5. Recommended sequence (finance only)

Delivery status: **F0, F1, F2 and F3 are implemented**. Remaining items are governance decisions and refinements.

**Wave F0 — integrity (one sprint, blocking).**
P0-1 ledger integrity, P0-6 archive instead of cascade delete, P0-4 tenant currency.
Nothing else should be developed before this; it protects every number produced later.

**Wave F1 — auditability (one sprint, blocking).**
P0-2 expense read/export, P0-3 auditor budget and expense access, P1-3 expense
attachments, P1-2 period close. **Delivered.** Expense approval is deferred to F2
pending an explicit governance decision.

**Wave F2 — treasurer's year (one sprint).**
P1-1 planned/voted budget and variance, P0-5 opening balance and accounts, P1-5 receipt
date, P1-7 numbered receipts, P1-10 reminder fallback. **Delivered**, except
P1-10 which depends on the future guardian/second-contact fields.

**Wave F3 — migration and audit pack (before go-live).**
P1-6 import with payments and dedupe, P1-11 finance journal export, P1-9 remove
disciplinary data from the finance export, P1-12 export permissions. **Delivered**
(legacy report labels remain French).

Acceptance for go-live: one complete exercise reproduced end to end — opening balance,
imported members, expected contributions, payments in cash and by transfer, two
declarations with custody closure, expenses with attachments, a budget with variance,
a period close, and an auditor review using only the auditor role.

---

## 6. Evidence index

- Ledger: `modules/contributions/models.py`, `repository.py`,
  `finance/contributions/service.py`, `schemas.py`
- Receipts and custody: `finance/receipts/service.py`, `finance/custody/service.py`
- Expenses and budget: `finance/expenses/service.py`, `finance/budgeting/service.py`
- Reminders: `finance/reminders/service.py`
- Reporting: `finance/reporting/service.py`, `modules/contributions/router.py`
- Capabilities and roles: `core/capabilities.py`, `modules/tenancy/role_catalog.py`
- Client: `apps/web/src/views/finance/`, `features/finance/`,
  `views/contributions/AdminContributionsView.vue`, `router/index.ts`
- Operational context: `docs/operations/production-readiness.md`
