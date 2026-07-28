# Contribution Receipt Declaration Workflow

## Purpose

A physical cash receipt reported by an office role is not an official payment. It becomes an official payment only when the treasurer processes the submitted declaration.

## Roles

- `president` and `secretary_general` manage member profiles and invitations.
- `treasurer` is the sole normal processor of receipt declarations and finance writer.
- `president`, `vice_president`, `secretary_general`, `auditor`, `censor`, and `sports_manager` may declare a receipt they received.
- `auditor` may declare a receipt but cannot process any declaration or mutate official finance data.
- `member` can only view declarations tied to their own profile.
- `admin` and `principal_admin` are retained as audited break-glass roles.

## State machine

`draft` → `submitted` → `validated` | `partially_validated` | `rejected` | `clarification_requested` | `cancelled`

Only a submitted declaration can be processed. A validation creates a `PaymentRecord` and updates the selected contribution in the same transaction. Rejection, cancellation, and clarification never change the official contribution balance.

## Audit and tenant isolation

Every declaration query is tenant-scoped. Creation, update, submission, and processing write an audit event under the contributions module. The declaration records the reporting office role, the processor, processed amount, and the official payment created after validation.
