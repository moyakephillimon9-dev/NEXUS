---
name: Chat and Workers Integration
description: How chat build-intent detection, workers live activity SSE, and build notifications work
---

# Chat ↔ Workers Integration

## Build intent detection
- `NexusBrain.detect_intent(message, owner)` returns `{is_build, goal, project_type, confidence}`
- `api_chat_stream` calls detect_intent and includes result in the SSE `done` event as `intent`
- Frontend `Chat` module checks `data.intent.is_build` and calls `ChatBuild.show(goal, type)` to render the Launch Build card
- Launch Build card links to `/builder?goal=...&type=...` — Builder.init() pre-fills from URL params

## Workers Live Activity SSE
- Endpoint: `GET /api/workers/live` (login required)
- Streams from `active_builds[task_id]['worker_activity']` list
- `_wa(task_id, worker_name, worker_id, message, type, code)` helper appends to worker_activity
- Types: info, code, thinking, success, error
- Frontend: `WorkersSidebar` (chat page) and `WorkersActivity` (workers page) both subscribe
- Workers page highlights the active worker card and pipeline stage chip

## Pipeline worker activity messages
- `_wa()` called during stage-listing loop with STAGE_CODES (actual code snippets for Coder/DB/etc.)
- On pipeline success: two `_wa()` calls from Verification AI and Memory AI
- On success: `_save_notification({type: build_complete, title, goal, deploy_path})`

## Notifications
- Stored in `data/notifications.json`
- GET `/api/notifications` — returns list
- POST `/api/notifications/<id>/dismiss` — removes by id
- Reports page loads them on DOMContentLoaded and renders `.notif-card` with "Design & Publish to Play Store" CTA

**Why:** User wanted workers to "know" about chat builds and have a separate workers chat with animations.
**How to apply:** Any new pipeline stage should call `_wa()` to emit to the live feed.
