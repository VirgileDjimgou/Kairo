# UI / UX Specification

## 1. Design Goal

The UI must look elegant, modern, and professional. It should be suitable for a GitHub portfolio and later commercialization.

The design should communicate:

- trust
- clarity
- security
- organization
- intelligence
- calm professionalism

---

## 2. Visual Style

Use:

- Bootstrap 5
- subtle shadows
- rounded cards
- muted backgrounds
- strong typography hierarchy
- clear badges
- structured tables
- clean empty states
- professional icons

Avoid:

- childish colors
- excessive gradients
- cluttered dashboards
- hardcoded COMBIS branding
- unreadable dense UI

---

## 3. Layout Structure

### App Layout

```text
Topbar
  - tenant name
  - search
  - user menu
  - status indicator

Sidebar
  - Dashboard
  - AI Chat
  - Documents
  - My Records
  - Contributions
  - Events
  - Policies
  - Admin

Main content
  - page title
  - action buttons
  - content cards
```

### Admin Layout

```text
Admin sidebar
  - Overview
  - Users
  - Roles
  - Documents
  - Ingestion Jobs
  - Business Records
  - Audit Logs
  - Settings
```

---

## 4. Key Screens

### Login

Elements:

- product logo/title
- email/password form
- clean split panel
- demo credentials note in development mode

### Dashboard

Cards:

- documents indexed
- active users
- pending ingestion jobs
- recent questions
- upcoming events
- alerts

### Chat

Layout:

- conversation list left
- chat center
- citations panel right or collapsible
- source chips below answers
- confidence indicator

### Documents

Elements:

- upload button
- search/filter
- access scope badge
- ingestion status badge
- actions menu

### Admin Users

Elements:

- user table
- role badges
- status filters
- invite/create button

### Contributions

Elements:

- personal balance card
- yearly table
- payment history
- admin import/action buttons

---

## 5. Component Standards

Each component should:

- accept typed props
- emit typed events where possible
- avoid direct API calls unless it is a page-level smart component
- show loading state
- show empty state
- show error state

---

## 6. Bootstrap Theme Direction

Suggested CSS variables:

```scss
:root {
  --om-primary: #1f4f8f;
  --om-primary-dark: #163861;
  --om-bg: #f5f7fb;
  --om-card-bg: #ffffff;
  --om-border: #d9e2ec;
  --om-text: #1f2937;
  --om-muted: #6b7280;
}
```

Use Bootstrap classes first, custom SCSS only where needed.

---

## 7. UX Copy Rules

The product should use generic terminology:

- Organization, not COMBIS
- Member, User, Admin
- Contribution, Payment, Record
- Policy, Rule, Document
- Source, Citation, Evidence

COMBIS wording appears only in demo seed data.
