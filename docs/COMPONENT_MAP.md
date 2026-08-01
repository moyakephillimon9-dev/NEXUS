# NEXUS Component Map
**Version:** 0.1.0

---

## Shared Layout Components (templates/base.html)

### `.sidebar`
- **`.sidebar-logo`** — NX SVG mark + "NEXUS" gradient text + "AI OPERATING SYSTEM" sub
- **`.sidebar-nav`** — `<nav>` with nav-section-label groups and nav-item links
  - **`.nav-item`** — icon + label, active state has gradient left border
- **`.sidebar-footer`** — owner-pill with avatar initial, name, role, logout button

### `.topbar`
- **`.topbar-title`** — page name
- **`.topbar-right`** — clock (id=`nexus-clock`), AI status pill (id=`ai-status`)

---

## Auth Components

### Setup page (templates/setup.html)
- Logo block
- Progress dots (4 step indicators)
- Info banner (private/secure notice)
- Form: full_name, company, email, phone, country, timezone, password, password2
- Submit: "Activate NEXUS"

### Login page (templates/login.html)
- Animated glow logo
- Form: email, password
- Security notice footer

---

## Dashboard (templates/dashboard.html)

### Welcome bar
- Greeting with gradient name highlight
- Sub-line: NEXUS status
- Quick action buttons: Chat, Build Something

### Stats grid (`.stats-grid`)
Four `.stat-card` components:
| Icon zone | Value | Label |
|-----------|-------|-------|
| cyan  | Total Projects | # |
| green | Workers Online | 22 |
| purple | Memory Entries | # |
| yellow | Active Builds | # |

### Dashboard grid (`.dashboard-grid` — 2 col)
- **Recent Projects card** — list of `.project-card` rows with status dot, name, timestamp, %
- **AI Workers card** — 8 `.worker-row` items with status badge

### Quick Launch grid (`.launch-grid`)
Six `.launch-card` tiles: Builder, Projects, Workers, Memory, Reports, Settings

---

## Chat (templates/chat.html)

### Welcome state (shown when no history)
- Floating NX logo (float animation)
- Headline, subtitle
- `.chat-suggestions` chips (6 preset questions)

### Message thread (`#chat-messages`)
Each `.msg` has:
- `.msg-avatar` — "⚡" (NEXUS) or "👤" (user), gradient background for NEXUS
- `.msg-sender` — uppercase label
- `.msg-bubble` — styled differently for nexus vs user

### Input area
- Clear button
- `.chat-input-box` — textarea + Send button
- Version/provider notice

---

## Builder (templates/builder.html)

### App type selector (`.builder-types` grid)
10 `.build-type` tiles: Web, Android, iOS, Desktop, AI, Game, Business, Dashboard, API, Automation

### Goal form
- Textarea goal input
- Optional: target users, key features
- Submit → Start Pipeline button + inline progress bar

### Pipeline console (`#build-console`)
- Monospace dark terminal
- Log lines: default (cyan), success (green), error (red), stage (purple)

### Pipeline overview grid
21 stage cards (0–20) showing stage number, worker name, brief description

---

## Workers (templates/workers.html)

### Status banner
Badge: "All Systems Online"

### Workers grid (`#workers-grid`)
Each `.worker-card`:
- ID badge + worker name + role description
- Stage number
- CPU + Memory metric bars (live-updated via `/api/workers` polling)

### Pipeline flow
Linear sequence of stage labels with → arrows

---

## Memory (templates/memory.html)

### Summary stats (2-col grid)
- Memory categories count
- Total entries count

### `.memory-timeline`
Vertical timeline with pseudo-element line (cyan→purple gradient).
Each `.memory-item` has: timestamp, key (cyan), value text.

### Memory categories grid
6 tiles: Projects, Architecture, Solutions, Mistakes, Patterns, Preferences

---

## Reports (templates/reports.html)

### Stats grid
Total Projects, Completed, In Progress, Errors

### Two-column grid
- Recent pipeline runs list
- System health with progress bars + overall score

### Future notice alert

---

## Settings (templates/settings.html)

### AI Provider card
- Provider selector dropdown
- OpenRouter URL + model
- Ollama host + model
- Max tokens + temperature
- Security note about API keys → Replit Secrets

### System card
- Version (read-only)
- Debug mode toggle

### Security card
- Read-only notice about approval requirements
- Link to roadmap for 2FA

---

## Roadmap (templates/roadmap.html)

### Header badges
Released / Planned count / Future count

### Honesty alert
Explains separation of pipeline %, feature %, roadmap %

### Milestone list
Each `.roadmap-item` has:
- Version badge, name, status badge, target date
- Description
- Feature tags (`.feature-list`)

### Vision statement card (gradient background)
Future capabilities in rounded tags

---

## JS Modules (static/js/nexus.js)

| Module | Responsibility |
|--------|---------------|
| `updateClock()` | Live clock every 1s |
| `markActiveNav()` | Sidebar active state on load |
| `Chat` | SSE streaming, message append, thinking dots, suggestion chips, clear |
| `Builder` | Type selection, form submit, pipeline polling, console log |
| `initWorkersRefresh()` | Polls `/api/workers` every 5s, updates metric bars |
