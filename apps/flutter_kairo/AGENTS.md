# Kairo Flutter Client Guide

## Purpose

`apps/flutter_kairo/` is the future native-style Kairo client. It is a separate
application from `apps/web/`, not a migration branch and not a WebView wrapper.
It will first ship on Android and Flutter Web, while preserving a path to iOS and
desktop later.

## Required Reading

Before any Flutter change, read in this order:

1. `../../AGENTS.md`
2. `../../docs/flutter/PROJECT_STATUS.md`
3. `../../docs/flutter/FLUTTER_APP_ROADMAP.md`
4. `../../docs/flutter/FEATURE_PARITY.md`
5. `../../prompts/FLUTTER_CONTINUE_UNIVERSAL.md`
6. the relevant existing Vue screen and FastAPI API contract

## Architecture Rules

- Keep this client independent from `apps/web/`; do not edit Vue files for Flutter work.
- FastAPI remains the sole authority for identity, roles, tenant filtering, finance,
  disciplinary access, audit decisions, and business validation.
- Never persist a password. Store only session material in platform secure storage.
- Every locally cached record and queued operation must be isolated by `tenant_id` and
  authenticated user id.
- Offline writes are drafts or idempotent pending operations until the API accepts them.
- Never finalise a payment, sanction, role change, deletion, or backup restore offline.
- User-facing text must support French, English, and German from the first screen.
- Preserve accessibility: semantic labels, focus order, touch targets, contrast, text
  scaling, and keyboard navigation for Flutter Web.

## Required Client Shape

Use feature-oriented packages rather than one large widget tree:

```text
lib/
  app/             bootstrap, routing, themes, localization
  core/            API, security, connectivity, storage, errors
  features/        auth, members, finance, discipline, governance, chat, notifications
  shared/          reusable widgets, models, design tokens
```

Use repositories as the boundary between UI, local data, and remote API. Keep API DTOs
separate from presentation models. Do not recreate backend policies in Dart.

## Definition of Done

A Flutter sprint is complete only when:

- its parity rows are updated in `docs/flutter/FEATURE_PARITY.md`;
- relevant unit, widget, and integration tests pass;
- Android and Flutter Web builds pass;
- visual evidence covers a phone-width and desktop-width viewport;
- API failures, offline state, loading state, and empty state are handled;
- roles and tenant isolation are verified against the real API;
- `docs/flutter/PROJECT_STATUS.md` and the roadmap are updated.

## Commands Once the Flutter Project Exists

```powershell
Set-Location apps/flutter_kairo
.\scripts\flutter.ps1 pub get
.\scripts\flutter.ps1 analyze
.\scripts\flutter.ps1 test
.\scripts\flutter.ps1 build apk --debug
.\scripts\flutter.ps1 build web
```

Use the exact commands appropriate to the active sprint. Do not claim a platform was
validated if its SDK or emulator was unavailable.
