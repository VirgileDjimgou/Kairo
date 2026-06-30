# Import / Export — Data Import And Backoffice Automation

## Overview

Sprint 21 added structured CSV import and export for core business records to reduce manual administration effort.

### Exports

All four export endpoints return CSV via `StreamingResponse` with `Content-Disposition: attachment`.

| Module | Endpoint | Auth | Filename |
|---|---|---|---|
| Members | `GET /api/v1/memberships/export` | Any authenticated user | `members.csv` |
| Contributions | `GET /api/v1/contributions/export` | Any authenticated user | `contributions.csv` |
| Events | `GET /api/v1/events/export` | Admin only | `events.csv` |
| Announcements | `GET /api/v1/announcements/export` | Admin only | `announcements.csv` |

### Imports

Both import endpoints accept a CSV file via `multipart/form-data` with an optional `?dry_run=true` query parameter. Admin role required.

| Module | Endpoint | Admin required | Dry-run |
|---|---|---|---|
| Members | `POST /api/v1/memberships/import` | Yes | `?dry_run=true` |
| Contributions | `POST /api/v1/contributions/import` | Yes | `?dry_run=true` |

---

## Member Import

### CSV Format

Required columns: `member_code`, `first_name`, `last_name`

Optional columns: `display_name`, `email`, `phone`, `status`

```csv
member_code,first_name,last_name,display_name,email,phone,status
M001,Alice,Martin,Alice Martin,alice@example.com,+33123456789,active
M002,Bob,Dupont,Bob Dupont,bob@example.com,,active
M003,Claire,Petit,Claire Petit,claire@example.com,+33987654321,inactive
```

Sample CSV file: [`seed/sample-members.csv`](../../seed/sample-members.csv)

### Validation rules

| Field | Rule |
|---|---|
| `member_code` | Required, must be unique per tenant |
| `first_name` | Required, must not be empty |
| `last_name` | Required, must not be empty |
| `status` | Optional, defaults to `active`. Allowed: `active`, `inactive`, `suspended`, `resigned` |
| `display_name` | Optional, defaults to `{first_name} {last_name}` if empty |

### Workflow

1. Upload CSV with `?dry_run=true` to validate rows without persisting
2. Review the validation summary (total rows, success count, errors per row)
3. If no errors, re-upload without `?dry_run=true` to persist
4. In the frontend, use the Import CSV modal which implements this two-step flow

---

## Contribution Import

### CSV Format

Required columns: `member_code`, `year`, `expected_amount`

Optional columns: `paid_amount`, `currency`, `status`, `due_date`

```csv
member_code,year,expected_amount,paid_amount,currency,status,due_date
M001,2026,100.00,50.00,EUR,partial,2026-06-30
M002,2026,100.00,0.00,EUR,pending,2026-06-30
M001,2025,100.00,100.00,EUR,paid,
```

Sample CSV file: [`seed/sample-contributions.csv`](../../seed/sample-contributions.csv)

### Validation rules

| Field | Rule |
|---|---|
| `member_code` | Required, must resolve to an existing member in the tenant |
| `year` | Required, must be between 2000 and 2100 |
| `expected_amount` | Required, must be >= 0 |
| `paid_amount` | Optional, defaults to 0, must be >= 0 |
| `currency` | Optional, defaults to EUR |
| `status` | Optional, defaults to `pending`. Allowed: `pending`, `paid`, `partial`, `overdue`, `waived` |

### Workflow

Same two-step dry-run workflow as member import.

---

## Export column reference

### Members export columns

`member_code`, `first_name`, `last_name`, `display_name`, `email`, `phone`, `status`, `joined_at`

### Contributions export columns

`year`, `member_code`, `first_name`, `last_name`, `expected_amount`, `paid_amount`, `balance`, `currency`, `status`, `due_date`

### Events export columns

`title`, `description`, `start_at`, `end_at`, `location`, `visibility_scope`, `status`, `created_at`

### Announcements export columns

`title`, `body`, `visibility_scope`, `published_at`, `expires_at`, `created_at`

---

## Architecture notes

- Shared CSV utilities live in `app/core/import_export.py`: `parse_csv()`, `generate_csv()`, `ImportResult`, `ImportRowError`
- Import validation is module-specific (membership vs contribution) and placed in the respective service methods
- Exports use `StreamingResponse` to stream CSV without buffering the entire file in memory
- Route ordering in FastAPI is critical: fixed-path routes like `/export` must be defined before parameterized paths like `/{id}` in the router file
- All operations are tenant-scoped; imports and exports never cross tenant boundaries
