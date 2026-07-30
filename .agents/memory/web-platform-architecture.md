---
name: Web platform architecture
description: How the NEXUS web layer sits on top of the existing CLI pipeline; entry points, auth, and design decisions
---

# Web Platform Architecture

## Rule
`app.py` is the Flask web entry point for NEXUS v0.1+. `nexus.py` remains the CLI entry point. Both use the same `core/` and `plugins/` stack — do not merge or replace either.

**Why:** The owner wanted a futuristic web UI without losing the existing CLI pipeline. The web layer is purely additive.

## How to apply
- Workflow `Start application` runs `python app.py` (port 5000).
- CLI still works via `python nexus.py`.
- Owner profile is stored in `data/owner.json` (git-ignored). First run → `/setup`. Subsequent runs → `/login` → `/dashboard`.
- Auth: SHA-256 + random 32-byte salt, handled in `core/auth.py`.
- Chat uses SSE streaming via `/api/chat/stream` (GET with `?message=`).
- Pipeline builds run in a `threading.Thread` writing to `active_builds` dict; frontend polls `/api/build/<task_id>/status`.
- All 22 workers defined statically in `core/nexus_brain.py` `WORKERS` list — do not duplicate in any other file.

## Key files
- `app.py` — all Flask routes
- `core/auth.py` — password hashing + verification
- `core/owner_manager.py` — owner CRUD (data/owner.json)
- `core/nexus_brain.py` — built-in chat engine + worker registry
- `static/css/nexus.css` — full design system (Electric Blue #00d4ff, bg #05050d)
- `static/js/nexus.js` — Chat SSE, Builder polling, live clock
- `templates/base.html` — sidebar + topbar layout base
- `roadmap.json` — v0.1 → v1.0 milestones (source of truth for roadmap page)

## Design tokens
- Primary blue: `#00d4ff`
- Background: `#05050d`
- Card bg: `#0b0b18`
- Green (success/online): `#00ff99`
- All CSS vars in `:root` block of `nexus.css`
