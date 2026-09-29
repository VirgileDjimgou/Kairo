# Kairo Performance Baseline

Generated: 2026-09-27T14:49:54.690953+00:00

Harness: `services/api/scripts/performance_baseline.py` (deterministic seed, SQLite).
Regenerate with `npm run perf:baseline`; check with `npm run perf:check`.

## 200 members

| Operation | p50 ms | p95 ms | SQL statements |
| --- | ---: | ---: | ---: |
| members_list | 8.65 | 12.24 | 1 |
| member_statement | 3.89 | 6.34 | 2 |
| contribution_summary | 2.17 | 6.09 | 1 |
| annual_budget | 15.39 | 17.1 | 3 |
| audit_journal | 3.24 | 4.85 | 1 |
| managed_users | 13.17 | 21.9 | 6 |
| unreachable_notifications | 9.94 | 10.9 | 3 |
| attention_overview | 5.65 | 11.93 | 6 |
| global_search | 8.4 | 13.63 | 8 |
| notification_outbox_drain | 665.25 | 717.58 | 103 |
| domain_event_outbox_drain | 560.76 | 601.52 | 52 |

## 1000 members

| Operation | p50 ms | p95 ms | SQL statements |
| --- | ---: | ---: | ---: |
| members_list | 36.61 | 96.18 | 1 |
| member_statement | 3.42 | 5.21 | 2 |
| contribution_summary | 2.72 | 4.23 | 1 |
| annual_budget | 46.8 | 60.85 | 3 |
| audit_journal | 3.83 | 4.33 | 1 |
| managed_users | 53.58 | 128.67 | 6 |
| unreachable_notifications | 23.82 | 27.15 | 3 |
| attention_overview | 5.98 | 9.56 | 6 |
| global_search | 10.58 | 16.14 | 8 |
| notification_outbox_drain | 737.07 | 867.85 | 103 |
| domain_event_outbox_drain | 608.03 | 708.09 | 52 |

## Thresholds

| Operation | max p95 ms | max statements |
| --- | ---: | ---: |
| annual_budget | 343.4 | 6 |
| attention_overview | 147.72 | 12 |
| audit_journal | 119.4 | 2 |
| contribution_summary | 124.36 | 2 |
| domain_event_outbox_drain | 2932.36 | 104 |
| global_search | 164.56 | 16 |
| managed_users | 614.68 | 12 |
| member_statement | 125.36 | 4 |
| members_list | 484.72 | 2 |
| notification_outbox_drain | 3571.4 | 206 |
| unreachable_notifications | 208.6 | 6 |

Thresholds are regression signals, not service level objectives: they allow a
4x p95 margin over the recorded baseline and 2x the statement count.
