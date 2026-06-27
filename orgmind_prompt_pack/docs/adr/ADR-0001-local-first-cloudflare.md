# ADR-0001 - Use Local-first Deployment with Cloudflare Tunnel

## Status

Accepted

## Context

The platform should run on a personal machine to avoid mandatory hosting costs. Users still need remote access from browsers and potentially mobile devices.

Firebase was considered as a message relay, but it would create an external dependency and make the architecture less direct.

## Decision

Use Docker Compose on the local machine and expose the web/API through Cloudflare Tunnel.

## Consequences

Positive:

- no paid backend required for MVP
- no router port forwarding required
- local data ownership
- realistic API architecture
- easier migration to VPS later

Negative:

- local machine must remain online
- upload and AI performance depend on local hardware
- backups become the operator's responsibility

## Alternatives Considered

- Firebase/Firestore relay
- VPS hosting from day one
- fully local LAN-only app
- hosted SaaS from day one
