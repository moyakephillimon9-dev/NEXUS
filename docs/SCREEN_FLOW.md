# NEXUS Screen Flow
**Version:** 0.1.0

---

## Auth Flow

```
App Start
    │
    ▼
data/owner.json exists?
    │
    ├── NO  ──► /setup ──► Form submit OK ──► Session created ──► /dashboard
    │
    └── YES ──► session.owner_id set?
                    │
                    ├── YES ──► /dashboard
                    │
                    └── NO  ──► /login ──► Credentials OK ──► Session ──► /dashboard
                                               │
                                               └── FAIL ──► /login (error shown)
```

---

## Dashboard Navigation

```
/dashboard (Home)
    ├── Click "Chat"             ──► /chat
    ├── Click "Build Something"  ──► /builder
    ├── Click project            ──► /projects (future: /projects/<id>)
    ├── Click "View All" workers ──► /workers
    └── Quick launch cards       ──► respective routes
```

---

## Build Flow

```
/builder
    │
    ├── Select app type (Web/Android/iOS/Desktop/AI/Game/…)
    ├── Enter goal + optional target users + features
    └── Click "Start Pipeline"
            │
            ▼
        POST /api/build → { task_id }
            │
            ▼
        Background thread starts (21 stages)
        Frontend polls GET /api/build/<task_id>/status every 1.5s
            │
            ├── stage updates → console log, progress bar, % label
            ├── status = "complete" → success message, stop polling
            └── status = "error"   → error message, stop polling
```

---

## Chat Flow

```
/chat
    │
    ├── No history? → Show welcome screen + suggestion chips
    │
    ├── User types message or clicks suggestion
    │       │
    │       └── GET /api/chat/stream?message=…  (SSE)
    │               │
    │               ├── data: { token: "…" }  → append token to bubble
    │               └── data: { done: true }  → close EventSource, set Online
    │
    └── Click "Clear" → POST /api/chat/clear → reload messages div
```

---

## Settings Flow

```
/settings (GET)
    │ Display current nexus_settings.json values
    │
    └── Form submit (POST)
            │
            ▼
        _save_nexus_settings(form data)
        Redirect back → /settings (GET) with saved=True flash
```

---

## Logout Flow

```
Any page → Click logout ──► GET /logout ──► session.clear() ──► /login
```

---

## Future Flows (planned — not yet implemented)

### Project detail (v0.2)
```
/projects ──► click project card ──► /projects/<task_id>
    Shows: full pipeline output, generated files, architecture diagram, deploy button
```

### Builder approval gate (v0.2)
```
Pipeline complete ──► "Review & Approve" modal ──► Founder approves ──► deploy artefacts
```

### Voice flow (v0.3)
```
/chat ──► click mic button ──► Web Speech API recording ──► auto-send to /api/chat/stream
NEXUS response ──► SpeechSynthesis.speak()
```

### 2FA flow (v0.2)
```
/login (password OK) ──► /login/2fa ──► Enter TOTP code ──► session created
/setup (final step)  ──► Show QR code ──► Scan in authenticator ──► verify first code
```
