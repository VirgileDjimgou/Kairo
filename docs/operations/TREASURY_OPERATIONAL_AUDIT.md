# Treasury Operational Audit — Current State

Date: 2026-11-13
Scope: **finance only** — treasury, member contributions, receipts and custody,
expenses, budget, auditor (commissaire aux comptes) oversight, finance roles, exports.
Everything outside this perimeter is out of scope.

Method: source review of the finance domain, route and capability matrix, data model,
migrations and regression suites, after the F0–F3 delivery. Findings below were
verified in code; the delivery history is recorded in
`TREASURY_COMPLETENESS_AUDIT.md`.

---

## 1. Verdict

**No blocking (P0) or P1 defect remains.** The core finance cycle is implemented end to
end and covered by 447 passing API tests. A single association can run its
contributions, cash receipts, custody, expenses, budget and auditor review on the
current build.

All nine P1 items from the previous audit are fixed: receipt-year booking, cash in
custody, expense correction and approval, exercise-close guards, opening-balance reset,
currency lock, auditor declarations, configurable categories and segregation of duties.

| Category | Count |
| --- | --- |
| P0 blockers | 0 |
| P1 open | 0 |
| P1 fixed | 9 |
| P2 refinements | 10 |
| Governance defaults delivered | 2 (configurable)

---

## 2. What is operational today

| Capability | Verified behaviour |
| --- | --- |
| Contributions | One record per member and exercise; expected/paid/balance derived from payments; partial, paid, overdue and waived statuses |
| Payments | Amount, date, method, reference, account, receipt number; idempotent submission; reversal with reason; no destructive deletion |
| Receipt declarations | Draft, submit, validate, partially validate, reject, clarify, cancel; member and non-member income |
| Custody | Handover report, reminder delay, treasury confirmation, audit trail |
| Expenses | Record, category, payee, date, account, supporting PDF/JPEG/PNG receipt, list, filter, detail, CSV/XLSX export |
| Budget | Realized income/expenses by category, voted plan per category, planned totals and variance |
| Treasury position | Cash and bank accounts, opening balances, prior-year carry, inflows/outflows/closing per account and totals |
| Receipts | Per-tenant/per-year numbered quittances, downloadable PDF, self-service for the member, 403 for another member |
| Auditor | Read-only budget, expenses, position, ledger exports, exercise status; no finance write capability |
| Exercise closing | Close/reopen with reason; every financial write in a closed year returns 409 |
| Currency | Organization currency inherited by every record, enforced, locked once records exist |
| Exports | Raw ledger CSV, member finance XLSX/PDF/WhatsApp, expense CSV/XLSX, chronological journal CSV; all audited |
| Import | CSV replay-safe: existing member/exercise rows skipped, balances backed by payments |
| Audit | Every create, update, payment, reversal, expense, receipt processing, custody step, period action and export is journaled |

Regression evidence: `test_finance_integrity.py` (6), `test_treasury_audit.py` (4),
`test_treasury_f2.py` (4), `test_treasury_f3.py` (3), `test_treasury_p1_fixes.py` (8),
plus the existing finance suites. Full API suite: **447 passed**.

---

## 3. P1 — status (all nine fixed)

| Finding | Status | Evidence |
| --- | --- | --- |
| P1-1 Non-membership income year | **Fixed** | Budget and journal now use `received_at` |
| P1-2 Cash in custody | **Fixed** | Position exposes `pending_custody` and excludes it from closing |
| P1-3 Expense correction | **Fixed** | `POST /contributions/expenses/{id}/reverse` keeps history and excludes totals |
| P1-4 Close with pending items | **Fixed** | Close returns 409 while declarations or handovers are open |
| P1-5 Opening balance double count | **Fixed** | An explicit opening is a reset; later years carry from the latest baseline |
| P1-6 Currency lock ignores budget/openings | **Fixed** | Budget lines and opening balances are part of the lock check |
| P1-7 Auditor receipt declarations | **Fixed** | Read-only declaration list in the auditor workspace |
| P1-8 Fixed expense categories | **Fixed** | Tenant category table, API, expense/budget validation and creation UI |
| P1-9 Approval / segregation of duties | **Fixed** | Expense approval capability (president/VP/admin) and configurable separate validator |


### P1-1. Non-membership income is booked in the validation year, not the receipt year

Membership receipts now create a payment dated `received_at`, but non-membership
income (donations, sponsorship, tournament proceeds, other income) has no payment row.
The budget and the journal count it by `processed_at.year`:

```python
# finance/budgeting/service.py
and receipt.processed_at.year == year
```

Impact: a donation received on 31 December and validated on 2 January is reported in
the next exercise. The annual accounts and the tax/fiduciary view are wrong at every
year boundary.

Minimal correction: use `received_at.year` for the accounting year in the budget and
the journal (keep `processed_at` for the audit trail), exactly as membership receipts
now do.

**Fixed:** the budget and the journal now select and date non-membership receipts by
`received_at`; the regression test books a 31 December donation and finds it in the
2025 budget and journal, not 2026.

### P1-2. Cash still in custody is counted as cash on hand

Validating a cash receipt creates a payment immediately, in the cash account, while
`cash_handover_status` is still `pending_handover`. The treasury position counts every
payment, regardless of custody state.

Impact: the cash position includes money that is still with the secretary or another
office holder. The closing balance is overstated until the handover is confirmed, and
the association can believe it holds cash it does not have.

Minimal correction: either
- expose a "pending custody" line per account and exclude it from available cash, or
- count cash receipts in the cash position only once `received_in_treasury`.

Bank receipts are unaffected.

**Fixed:** each position row exposes `pending_custody`; the closing balance subtracts
it. A validated cash receipt shows the money as pending and keeps the available cash at
zero until `confirm-treasury-receipt`. The UI displays the pending column.

### P1-3. An expense can never be corrected

Expenses expose `POST`, list, detail, export and attachment. There is **no update,
reversal or compensating entry**. A wrong amount, category or payee is permanent.

Impact: the treasurer cannot fix a typo without falsifying the ledger through another
record, and the auditor sees an error that cannot be corrected with a trace.

Minimal correction: add a reversal (status + reason + actor) that keeps the original
row and excludes it from totals, or a negative adjustment expense; never a destructive
edit.

**Fixed:** `POST /contributions/expenses/{id}/reverse` keeps the row with `reversed_at`,
`reversed_by` and `reversal_reason`; reversed expenses are excluded from the budget,
the position and the journal totals, appear as `reversed` in the list and CSV/XLSX
export, and cannot be reversed twice. The ledger UI offers the action to the treasurer.

### P1-4. Closing an exercise ignores pending receipts and handovers

`close_finance_period` only checks whether the year is already closed. It does not look
at submitted declarations, validated receipts awaiting handover, or treasury
confirmations.

Impact: the treasurer can close a year while a receipt is still pending. Processing it
afterwards is blocked by the closed-year guard, so the only path is to reopen the
exercise. The "closed" state does not represent a real cut-off.

Minimal correction: block the close (or require an explicit override with a reason)
while the year has submitted declarations or open handovers.

**Fixed:** `close_finance_period` returns 409 while the exercise has submitted or
clarification-pending declarations, or cash handovers not received in treasury. The
message reports both counts.

### P1-5. An opening balance entered after prior-year activity is counted twice

The position computes:

```python
opening = explicit_opening(year) + prior_year_inflows - prior_year_outflows
```

If the association used Kairo in 2025 and then enters the bank balance at 1 January 2026
as the 2026 opening balance, the 2025 movements are added on top of a balance that
already contains them.

Impact: the closing position can be overstated by a full prior year of movements.

Minimal correction: treat an explicit opening as a reset (ignore prior movements for
that account/year), or only allow opening balances for the first year with data and
display a warning.

**Fixed:** an explicit opening is a reset. Later exercises carry from the latest
baseline for that account, not from the whole history. The UI states that an entered
opening replaces the carry-over. The regression test covers both the reset and the
carry into the next year.

### P1-6. The currency can change while a budget or opening balance exists

`_has_financial_records` checks contributions, expenses and receipt declarations only.
It ignores `finance_budget_lines` and `finance_opening_balances`.

Impact: a tenant that has voted a budget or entered opening balances but no
contribution yet can switch currency, leaving those amounts in the previous currency.

Minimal correction: include budget lines and opening balances in the lock check.

**Fixed:** the currency lock now counts `finance_budget_lines` and
`finance_opening_balances` as financial records. A tenant with only a voted budget or an
opening balance receives 409 on a currency change. Regression coverage exists for both.

### P1-7. The auditor workspace does not show receipt declarations

The API allows the auditor to read tenant declarations (`receipt:tenant_read`), but the
auditor view only shows the budget, expenses, position, member balances and payments.
The declaration lifecycle — submitted, validated, rejected, clarification — is not
visible.

Impact: the commissaire cannot review the cash-receipt cycle from their workspace.
They can only see validated movements in the journal, not what was rejected or is
pending.

Minimal correction: add a read-only declaration list (same data as the treasurer queue,
without actions) to the auditor workspace.

**Fixed:** `ReceiptDeclarationsList.vue` renders every declaration with member/source,
income type, amount, status, handover state and processing note. It is included in the
auditor workspace and exposes no action.

### P1-8. Expense categories are fixed to six values

The enum is `sport_equipment`, `fuel_transport`, `tournament`, `cultural_event`,
`administration`, `other`. There is no per-tenant category.

Impact: insurance, rent, bank fees, referees, training or equipment maintenance cannot
be classified. The budget variance and the fiduciary export are therefore approximate
for most associations.

Minimal correction: a tenant-level category table (name + direction), seeded with the
current six values. This is the only P1 that needs a small product decision, not just a
guard.

**Fixed:** `finance_expense_categories` stores tenant categories, seeded on first use
with the six defaults. `GET/POST /contributions/expense-categories` list and create
them; expenses and budget lines validate against the tenant list; the budget aggregates
custom categories; the expense form lists them and can add a category inline.

### P1-9. Expense approval and segregation of duties are still undefined

The treasurer records and can also validate their own declared cash receipt; there is
no expense approval step. This is a governance decision, not a code defect, but it is
an internal-control gap the auditor will ask about.

Minimal correction (once the rule is decided): a `submitted → approved/rejected` state
on expenses, and a processing rule that prevents the declarant from validating their
own receipt. The auditor must remain read-only.

**Fixed with explicit defaults:**
- Expenses now carry `recorded → approved/rejected` with `approved_at`, `approved_by`
  and `approval_note`. Approval requires the new `finance:expenses_approve` capability,
  held by the president, the vice-president and the principal administrator — not by
  the treasurer and not by the auditor.
- Rejected expenses are excluded from the budget and the position.
- Tenants can require a separate receipt validator through
  `finance.require_separate_receipt_validator` in tenant settings (default `false`).
  When enabled, the declarant cannot process their own declaration.


---

## 4. P2 — refinements, not blockers

| # | Finding | Consequence |
| --- | --- | --- |
| P2-1 | First receipt-number allocation can race: two concurrent first payments can both create the counter, one hitting the unique constraint | A 500 on a rare concurrent first payment; retry would fix it |
| P2-2 | Import dedupe is service-level only; two concurrent imports can still duplicate a row | Low risk for a single treasurer |
| P2-3 | Legacy/imported amounts without an account stay in "Non affecté"; there is no reclassification endpoint | The cash/bank split is incomplete for migrated history |
| P2-4 | Reversed payments are hidden only by disabling the receipt link; no visible "reversed" badge or reason in the payments list | A treasurer can miss a reversal |
| P2-5 | The journal export lists reversed payments with a positive amount and a `reversed` status | A naive sum over the CSV overstates income |
| P2-6 | Replacing an expense attachment leaves the previous object in storage; downloads are not audited | Storage leak and incomplete access trail |
| P2-7 | Legacy XLSX/PDF/WhatsApp report labels remain French | A German or English committee receives French documents |
| P2-8 | `overdue` is derived on write but not refreshed by a scheduler | A late contribution keeps its last status until the next write |
| P2-9 | Member statements do not show receipt numbers | The member has to download each quittance separately |
| P2-10 | Budget plan changes are audited as one event with totals, not line by line; there is no "voted on" date or minute reference | Weak traceability of the assembly vote |

---

## 5. Go-live checklist (finance only)

Before the first real exercise:

1. Set the organization currency **before** creating any financial record.
2. Create the cash and bank accounts, then enter the opening balances for the first
   year only.
3. Import the member register, then the contribution ledger once; verify
   `skipped_count = 0` on the first run and `success_count = 0` on a replay.
4. Reconcile every imported amount into an account (or accept the "Non affecté" line
   until reclassification exists).
5. Confirm the custody operating rule: pending cash is already excluded from the
   available position, so the treasurer must confirm handovers to make it available.
6. Confirm the approval policy: expenses are approved by a holder of
   `finance:expenses_approve` (president, vice-president, principal administrator);
   enable `finance.require_separate_receipt_validator` if the declarant must never
   validate their own receipt.
7. Closing an exercise is now refused while declarations or handovers are open; process
   them first.
8. Give the auditor an `auditor` account only; verify `403` on every write.
9. Run one full cycle on staging: contribution, cash receipt with handover, bank
   payment, expense with attachment, budget plan, position, close, journal export,
   auditor review.
10. Record a restore drill before loading real data.

---

## 6. Explicitly out of scope

Online payments and SEPA mandates, bank reconciliation (CAMT/CSV import and matching),
transfers between cash and bank, fiduciary/ERP export formats, multi-year member
statements, payment reminder letters as PDF, tenant-configurable report templates, and
any finance UI redesign. These are improvements, not prerequisites.

---

## 7. Evidence index

- Ledger and payments: `modules/contributions/models.py`,
  `modules/contributions/repository.py`, `finance/contributions/service.py`,
  `finance/ledger.py`
- Receipts and custody: `finance/receipts/service.py`, `finance/custody/service.py`
- Expenses: `finance/expenses/service.py`, `modules/contributions/router.py`
- Budget and position: `finance/budgeting/service.py`, `finance/treasury/service.py`
- Periods: `finance/periods/service.py`
- Reporting: `finance/reporting/service.py`
- Roles: `core/capabilities.py`, `modules/tenancy/role_catalog.py`
- Client: `apps/web/src/views/finance/`, `features/finance/`,
  `views/contributions/AdminContributionsView.vue`
- Tests: `services/api/tests/test_finance_integrity.py`,
  `test_treasury_audit.py`, `test_treasury_f2.py`, `test_treasury_f3.py`,
  `test_treasury_p1_fixes.py`
- P1 fixes: `finance/treasury/service.py` (pending custody, opening reset),
  `finance/budgeting/service.py` and `finance/reporting/service.py` (receipt year),
  `finance/expenses/service.py` (reversal and approval), `finance/periods/service.py`
  (close guard), `finance/categories/service.py` (tenant categories),
  `tenancy/service.py` (currency lock and separate validator),
  migrations `0042_expense_reversal.py`, `0043_tenant_expense_categories.py`,
  `0044_expense_approval.py`
- Delivery history: `TREASURY_COMPLETENESS_AUDIT.md`
