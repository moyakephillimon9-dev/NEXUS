# NEXUS — AI Operating System

**Version:** 0.1.0  
**Owner:** Moyake Phillimon  
**Type:** Private AI Operating System (Web + CLI)

---

## What is NEXUS?

NEXUS is a private AI Operating System that orchestrates 22 specialised AI agents across a 21-stage pipeline to plan, design, code, review, test, secure, document and deploy software from a natural-language goal.

---

## How to Run

### Web Interface (recommended)

```bash
python app.py
```

Opens at `http://localhost:5000`. First run shows the owner setup screen.

### CLI Interface

```bash
python nexus.py
```

Interactive menu for pipeline runs, worker listing and project history.

### CLI one-shot

```bash
python nexus.py --goal "Build a REST API"
python nexus.py --vision path/to/vision.txt
python nexus.py --workers
python nexus.py --version
```

---

## Architecture

```
app.py                  ← Flask web server (NEXUS v0.1 main entry point)
nexus.py                ← CLI entry point (preserved)
core/
  auth.py               ← Password hashing & credential verification
  owner_manager.py      ← Founder profile management
  nexus_brain.py        ← Built-in reasoning engine & chat
  orchestrator.py       ← 21-stage pipeline wiring
  kernel.py             ← System boot & plugin discovery
  config.py             ← Centralised paths and constants
  shared_memory.py      ← Inter-agent key-value state store
  ai_registry.py        ← Plugin registry
  plugin_manager.py     ← Auto-discovers plugin directories
  logger.py             ← Timestamped logger
plugins/                ← 22 AI agent plugins (one folder each)
templates/              ← Jinja2 HTML templates
static/css/nexus.css    ← NEXUS design system
static/js/nexus.js      ← Frontend interactivity
data/                   ← Owner profile (git-ignored, encrypted)
memory/                 ← Persistent knowledge graph
roadmap.json            ← Full NEXUS roadmap (v0.1 → v1.0)
```

---

## Web Routes

| Route | Description |
|-------|-------------|
| `/` | Redirects to setup (first run) or dashboard |
| `/setup` | First-time owner registration |
| `/login` | Owner login |
| `/dashboard` | Main control centre |
| `/chat` | Chat with NEXUS |
| `/builder` | Project builder (runs 21-stage pipeline) |
| `/projects` | All project history |
| `/workers` | 22 AI workers status |
| `/memory` | Memory timeline & knowledge base |
| `/reports` | Pipeline analytics |
| `/settings` | AI provider, security, system config |
| `/roadmap` | Full NEXUS roadmap |

---

## Pipeline (21 stages, 22 agents)

Vision Parser → Capability Assessor → Research AI → Module Detector → Planner AI → Architect AI → Database AI → Coder AI → Design AI → Reviewer AI → Tester AI → Security AI → Performance AI → Documentation AI → Monitoring AI → Integration AI → DevOps AI → Deployment AI → Verification AI → Progress Tracker → Memory AI

---

## Security

- Owner credentials are SHA-256 hashed with a random salt
- `data/owner.json` is git-ignored and never committed
- NEXUS never acts on dangerous operations without explicit Founder approval
- Session secret managed via `SESSION_SECRET` environment variable

---

## Roadmap

| Version | Name | Status |
|---------|------|--------|
| 0.1.0 | Foundation Release | ✅ Complete |
| 0.2.0 | LLM Integration | 📋 Planned |
| 0.3.0 | Voice Interface | 📋 Planned |
| 0.4.0 | Mobile App Creation | 🔭 Future |
| 0.5.0 | Financial Management | 🔭 Future |
| 1.0.0 | Full AI Operating System | 🔭 Future |

---

## User Preferences

- Preserve all existing plugin agents — do not remove functionality.
- Rename NEXUS Builder → NEXUS throughout (completed in v0.1.0).
- No external dependencies beyond Flask — keep the project lean.
- Built-in reasoning engine must always work without any API key.
- Pipeline order: Vision → Assess → Research → Module → Planner → Architect → Database → Coder → Design → Reviewer → Tester → Security → Performance → Docs → Monitor → Integration → DevOps → Deploy → Verify → Progress → Memory.
- Push to GitHub after every significant update.
- Dark futuristic UI: Electric Blue (#00d4ff), Black background, White text.
- NEXUS is a private system — only the Founder has access.
- Never fake completion. Always be honest about what is and isn't implemented.
