"""
NEXUS — AI Operating System
Web Application Entry Point

Version : 0.1.0
Owner   : Moyake Phillimon
"""

import os, json, threading, time, datetime, zipfile, io
from pathlib import Path
from functools import wraps

from flask import (Flask, render_template, request, session,
                   redirect, url_for, jsonify, Response, send_file)

from core.auth import Auth
from core.owner_manager import OwnerManager
from core.nexus_brain import NexusBrain
from core.config import Config
from core import sms_otp

# ── App bootstrap ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'nexus-internal-key-change-me')

auth     = Auth()
owner_mgr = OwnerManager()
brain    = NexusBrain()

# task_id → progress dict (in-memory; survives the request lifecycle)
active_builds: dict = {}


# ── Auth decorator ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('owner_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if not owner_mgr.has_owner():
        return redirect(url_for('setup'))
    if not session.get('owner_id'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if owner_mgr.has_owner():
        return redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        d = request.form
        pw  = d.get('password', '')
        pw2 = d.get('password2', '')
        if pw != pw2:
            error = 'Passwords do not match.'
        elif len(pw) < 8:
            error = 'Password must be at least 8 characters.'
        else:
            result = owner_mgr.create_owner(
                full_name = d.get('full_name', '').strip(),
                email     = d.get('email', '').strip().lower(),
                phone     = d.get('phone', '').strip(),
                company   = d.get('company', '').strip(),
                country   = d.get('country', '').strip(),
                timezone  = d.get('timezone', 'UTC'),
                password  = pw,
            )
            if result['success']:
                session['owner_id']   = result['owner_id']
                session['owner_name'] = result['name']
                return redirect(url_for('dashboard'))
            error = result.get('error', 'Setup failed.')
    return render_template('setup.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not owner_mgr.has_owner():
        return redirect(url_for('setup'))
    if session.get('owner_id'):
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        result = auth.verify(
            request.form.get('email', '').strip().lower(),
            request.form.get('password', ''),
        )
        if result['success']:
            session['owner_id']   = result['owner_id']
            session['owner_name'] = result['name']
            return redirect(url_for('dashboard'))
        error = 'Invalid email or password.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ═══════════════════════════════════════════════════════════════════════════════
# SMS / PHONE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/phone/send-otp', methods=['POST'])
def api_phone_send_otp():
    """Send a 6-digit OTP to the given phone number (no auth required — used at setup)."""
    phone = (request.json or {}).get('phone', '').strip()
    if not phone:
        return jsonify({'success': False, 'error': 'Phone number is required.'}), 400
    result = sms_otp.send_otp(phone)
    return jsonify(result)


@app.route('/api/phone/verify-otp', methods=['POST'])
def api_phone_verify_otp():
    """Verify an OTP code against a phone number (no auth required — used at setup)."""
    data  = request.json or {}
    phone = data.get('phone', '').strip()
    code  = data.get('code', '').strip()
    if not phone or not code:
        return jsonify({'success': False, 'error': 'Phone and code are required.'}), 400
    result = sms_otp.verify_otp(phone, code)
    if result['success']:
        # Store verified phone in session so setup form can confirm it
        session['phone_verified'] = phone
    return jsonify(result)


@app.route('/api/phone/send-otp-auth', methods=['POST'])
@login_required
def api_phone_send_otp_auth():
    """Send OTP to an authenticated owner's phone (from Settings)."""
    phone = (request.json or {}).get('phone', '').strip()
    if not phone:
        owner = owner_mgr.get_owner()
        phone = owner.get('phone', '')
    if not phone:
        return jsonify({'success': False, 'error': 'No phone number on file.'}), 400
    result = sms_otp.send_otp(phone)
    return jsonify(result)


@app.route('/api/phone/verify-otp-auth', methods=['POST'])
@login_required
def api_phone_verify_otp_auth():
    """Verify OTP and mark phone as verified on the owner profile."""
    data  = request.json or {}
    phone = data.get('phone', '').strip()
    code  = data.get('code', '').strip()
    if not phone or not code:
        return jsonify({'success': False, 'error': 'Phone and code are required.'}), 400
    result = sms_otp.verify_otp(phone, code)
    if result['success']:
        owner_mgr.update_owner({'phone': phone, 'phone_verified': True})
    return jsonify(result)


@app.route('/api/twilio/status')
def api_twilio_status():
    return jsonify({'configured': sms_otp.is_configured()})


@app.route('/api/sms/test', methods=['POST'])
@login_required
def api_sms_test():
    """Send a test SMS to the owner's registered phone."""
    owner = owner_mgr.get_owner()
    phone = owner.get('phone', '').strip()
    if not phone:
        return jsonify({'success': False, 'error': 'No phone number on your profile. Add one in Settings first.'}), 400
    if not sms_otp.is_configured():
        return jsonify({'success': False, 'error': 'Twilio secrets not set. Add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in Replit Secrets.'}), 400
    result = _send_alert_sms(phone, f"✅ NEXUS SMS Test — your alerts are working! System is online.")
    return jsonify(result)


@app.route('/api/sms/alert', methods=['POST'])
@login_required
def api_sms_alert():
    """Send a manual SMS alert with a custom message."""
    data    = request.json or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'success': False, 'error': 'Message is required.'}), 400
    owner = owner_mgr.get_owner()
    phone = owner.get('phone', '').strip()
    if not phone:
        return jsonify({'success': False, 'error': 'No phone number on your profile.'}), 400
    result = _send_alert_sms(phone, message)
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/dashboard')
@login_required
def dashboard():
    owner    = owner_mgr.get_owner()
    projects = _load_projects()[:6]
    workers  = brain.get_workers_summary()
    stats    = {
        'total_projects' : len(_load_projects()),
        'workers_online' : len([w for w in workers if w.get('status') == 'online']),
        'memory_entries' : _count_memory_entries(),
        'active_builds'  : len([b for b in active_builds.values() if b.get('status') == 'running']),
    }
    return render_template('dashboard.html', owner=owner, projects=projects,
                           workers=workers, stats=stats)


# ═══════════════════════════════════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/chat')
@login_required
def chat():
    owner   = owner_mgr.get_owner()
    history = brain.get_chat_history()
    return render_template('chat.html', owner=owner, history=history)


@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    msg   = (request.json or {}).get('message', '').strip()
    if not msg:
        return jsonify({'error': 'Empty message'}), 400
    owner = owner_mgr.get_owner()
    brain.save_message('user', msg)
    response = brain.respond(msg, owner)
    brain.save_message('nexus', response)
    return jsonify({'response': response})


@app.route('/api/chat/stream')
@login_required
def api_chat_stream():
    msg   = request.args.get('message', '').strip()
    owner = owner_mgr.get_owner()

    def generate():
        brain.save_message('user', msg)
        full = ''
        for token in brain.stream_response(msg, owner):
            full += token
            yield f"data: {json.dumps({'token': token})}\n\n"
        brain.save_message('nexus', full)
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route('/api/chat/clear', methods=['POST'])
@login_required
def api_chat_clear():
    brain.clear_chat_history()
    return jsonify({'success': True})


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/projects')
@login_required
def projects():
    owner    = owner_mgr.get_owner()
    all_proj = _load_projects()
    return render_template('projects.html', owner=owner, projects=all_proj)


# ═══════════════════════════════════════════════════════════════════════════════
# BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/builder')
@login_required
def builder():
    owner = owner_mgr.get_owner()
    return render_template('builder.html', owner=owner)


@app.route('/api/build', methods=['POST'])
@login_required
def api_build():
    data = request.json or {}
    goal = data.get('goal', '').strip()
    if not goal:
        return jsonify({'error': 'Goal is required'}), 400

    task_id = f"task_{int(time.time() * 1000)}"
    active_builds[task_id] = {
        'goal'      : goal,
        'status'    : 'starting',
        'progress'  : 0,
        'stage'     : 'Initializing',
        'stage_idx' : 0,
        'logs'      : [f'[NEXUS] Received goal: {goal}'],
        'started_at': datetime.datetime.now().isoformat(),
        'result'    : None,
    }

    thread = threading.Thread(target=_run_pipeline, args=(task_id, goal), daemon=True)
    thread.start()
    return jsonify({'task_id': task_id})


@app.route('/api/build/<task_id>/status')
@login_required
def api_build_status(task_id):
    build = active_builds.get(task_id)
    if not build:
        return jsonify({'status': 'not_found'}), 404
    return jsonify(build)


@app.route('/api/build/<task_id>/files')
@login_required
def api_build_files(task_id):
    """List files generated in the deployment folder for a completed build."""
    build = active_builds.get(task_id)
    if not build:
        return jsonify({'error': 'Build not found'}), 404
    deploy_path = build.get('deploy_path')
    if not deploy_path or not Path(deploy_path).exists():
        return jsonify({'files': [], 'deploy_path': deploy_path})

    files = []
    base = Path(deploy_path)
    for fp in sorted(base.rglob('*')):
        if fp.is_file():
            rel = str(fp.relative_to(base))
            size = fp.stat().st_size
            files.append({'name': rel, 'size': size})
    return jsonify({'files': files, 'deploy_path': str(base)})


@app.route('/api/build/<task_id>/download')
@login_required
def api_build_download(task_id):
    """Zip and serve the generated project as a downloadable archive."""
    build = active_builds.get(task_id)
    if not build:
        return jsonify({'error': 'Build not found'}), 404
    deploy_path = build.get('deploy_path')
    if not deploy_path or not Path(deploy_path).exists():
        return jsonify({'error': 'No deployment artefacts found — pipeline may have not completed.'}), 404

    mem_zip = io.BytesIO()
    base    = Path(deploy_path)
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fp in sorted(base.rglob('*')):
            if fp.is_file():
                zf.write(fp, fp.relative_to(base))
    mem_zip.seek(0)

    project_name = base.name.replace(' ', '_')
    return send_file(
        mem_zip,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{project_name}.zip",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# WORKERS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/workers')
@login_required
def workers():
    owner       = owner_mgr.get_owner()
    worker_list = brain.get_all_workers()
    return render_template('workers.html', owner=owner, workers=worker_list)


@app.route('/api/workers')
@login_required
def api_workers():
    return jsonify(brain.get_all_workers())


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/memory')
@login_required
def memory():
    owner    = owner_mgr.get_owner()
    memories = _load_memory_timeline()
    return render_template('memory.html', owner=owner, memories=memories)


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/reports')
@login_required
def reports():
    owner = owner_mgr.get_owner()
    rpt   = _generate_report()
    return render_template('reports.html', owner=owner, report=rpt)


# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    owner          = owner_mgr.get_owner()
    nexus_settings = _load_nexus_settings()
    saved          = False
    if request.method == 'POST':
        _save_nexus_settings(request.form.to_dict())
        nexus_settings = _load_nexus_settings()
        saved = True
    return render_template('settings.html', owner=owner,
                           nexus_settings=nexus_settings, saved=saved)


@app.route('/api/settings', methods=['POST'])
@login_required
def api_settings():
    _save_nexus_settings(request.json or {})
    return jsonify({'success': True})


# ═══════════════════════════════════════════════════════════════════════════════
# ROADMAP
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/roadmap')
@login_required
def roadmap():
    owner        = owner_mgr.get_owner()
    roadmap_data = _load_roadmap()
    return render_template('roadmap.html', owner=owner, roadmap=roadmap_data)


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

PIPELINE_STAGES = [
    ("VISION-001",  "Vision Parser",        "Parsing your goal"),
    ("ASSESS-001",  "Capability Assessor",  "Assessing capabilities"),
    ("RESEARCH-001","Research AI",          "Researching patterns"),
    ("MODULE-001",  "Module Detector",      "Detecting modules"),
    ("PLANNER-001", "Planner AI",           "Creating project plan"),
    ("ARCH-001",    "Architect AI",         "Designing architecture"),
    ("DB-001",      "Database AI",          "Designing database"),
    ("CODER-001",   "Coder AI",             "Writing source code"),
    ("DESIGN-001",  "Design AI",            "Creating UI/UX"),
    ("REVIEW-001",  "Reviewer AI",          "Reviewing code"),
    ("TEST-001",    "Tester AI",            "Writing tests"),
    ("SEC-001",     "Security AI",          "Security scanning"),
    ("PERF-001",    "Performance AI",       "Performance analysis"),
    ("DOCS-001",    "Documentation AI",     "Generating docs"),
    ("MON-001",     "Monitoring AI",        "Setting up monitoring"),
    ("INT-001",     "Integration AI",       "Wiring integrations"),
    ("DEVOPS-001",  "DevOps AI",            "Preparing DevOps"),
    ("DEPLOY-001",  "Deployment AI",        "Generating deployment"),
    ("VERIFY-001",  "Verification AI",      "Verifying pipeline"),
    ("PROG-001",    "Progress Tracker",     "Tracking progress"),
    ("MEM-001",     "Memory AI",            "Saving to memory"),
]


def _run_pipeline(task_id: str, goal: str):
    """Run the NEXUS pipeline in a background thread, updating active_builds."""
    build = active_builds[task_id]
    try:
        build['status'] = 'running'

        # Stage-by-stage progress updates (real orchestrator runs underneath)
        for idx, (wid, name, action) in enumerate(PIPELINE_STAGES):
            build['stage']     = name
            build['stage_idx'] = idx
            build['progress']  = int(((idx) / len(PIPELINE_STAGES)) * 95)
            build['logs'].append(f"[{wid}] {action}…")
            time.sleep(0.3)   # yield to let the thread breathe

        # Run actual orchestrator
        from core.orchestrator import Orchestrator
        build['logs'].append("[NEXUS] Pipeline executing…")
        orch    = Orchestrator()
        project = orch.run(goal)

        # Surface generated artefacts to the UI
        deploy_path = None
        if isinstance(project, dict):
            deploy_path = project.get('deployment', {}).get('deployment_path')

        build['status']      = 'complete'
        build['progress']    = 100
        build['stage']       = 'Complete'
        build['deploy_path'] = deploy_path
        build['result']      = {
            'framework'    : project.get('architecture', {}).get('framework', 'Python') if isinstance(project, dict) else 'Python',
            'language'     : project.get('architecture', {}).get('language', 'Python')  if isinstance(project, dict) else 'Python',
            'deploy_path'  : deploy_path,
            'has_artifacts': bool(deploy_path and Path(deploy_path).exists()),
        }
        if deploy_path:
            build['logs'].append(f"[NEXUS] ✓ Pipeline complete. Project saved → {deploy_path}")
        else:
            build['logs'].append("[NEXUS] ✓ Pipeline complete. (Deployment path not generated)")

        # ── SMS alert on completion ────────────────────────────────────────
        _notify_build_complete(goal, deploy_path)

    except Exception as exc:
        build['status'] = 'error'
        build['error']  = str(exc)
        build['logs'].append(f"[ERROR] {exc}")


def _send_alert_sms(phone: str, message: str) -> dict:
    """Send an SMS alert via Twilio. Silent no-op if Twilio not configured."""
    if not sms_otp.is_configured():
        return {'success': False, 'error': 'Twilio not configured'}
    try:
        import os
        from twilio.rest import Client
        client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
        client.messages.create(
            body=message[:1600],
            from_=os.environ['TWILIO_PHONE_NUMBER'],
            to=phone,
        )
        return {'success': True}
    except Exception as exc:
        return {'success': False, 'error': str(exc)}


def _notify_build_complete(goal: str, deploy_path):
    """Fire-and-forget SMS when a pipeline build completes."""
    owner = owner_mgr.get_owner()
    phone = owner.get('phone', '').strip()
    if not phone:
        return
    short_goal = goal[:80] + ('…' if len(goal) > 80 else '')
    has_files  = bool(deploy_path and Path(deploy_path).exists())
    msg = (
        f"⚡ NEXUS Build Complete\n"
        f"Goal: {short_goal}\n"
        + (f"Files ready to download at {deploy_path}" if has_files else "Pipeline finished (no deploy artefacts).")
    )
    threading.Thread(target=_send_alert_sms, args=(phone, msg), daemon=True).start()


def _load_projects() -> list:
    folder = Config.PROJECTS_FOLDER
    projects = []
    if folder.exists():
        for fp in sorted(folder.glob('*.json'), reverse=True)[:50]:
            try:
                with open(fp) as f:
                    projects.append(json.load(f))
            except Exception:
                pass
    return projects


def _load_memory_timeline() -> dict:
    db = Config.MEMORY_FOLDER / 'database.json'
    if db.exists():
        try:
            with open(db) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _count_memory_entries() -> int:
    data = _load_memory_timeline()
    return sum(len(v) if isinstance(v, (list, dict)) else 1 for v in data.values())


def _generate_report() -> dict:
    projects = _load_projects()
    now      = datetime.datetime.now()
    return {
        'generated_at'   : now.strftime('%Y-%m-%d %H:%M'),
        'total_projects' : len(projects),
        'completed'      : sum(1 for p in projects if p.get('status') == 'complete'),
        'in_progress'    : sum(1 for p in projects if p.get('status') not in ('complete', 'error')),
        'errors'         : sum(1 for p in projects if p.get('status') == 'error'),
        'recent'         : projects[:5],
    }


def _load_nexus_settings() -> dict:
    fp = Config.ROOT / 'nexus_settings.json'
    if fp.exists():
        with open(fp) as f:
            return json.load(f)
    return {}


def _save_nexus_settings(updates: dict):
    fp      = Config.ROOT / 'nexus_settings.json'
    current = _load_nexus_settings()
    current.update({k: v for k, v in updates.items() if v not in (None, '')})
    with open(fp, 'w') as f:
        json.dump(current, f, indent=2)


def _load_roadmap() -> dict:
    fp = Config.ROOT / 'roadmap.json'
    if fp.exists():
        with open(fp) as f:
            return json.load(f)
    return {'version': '0.1.0', 'milestones': []}


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n  NEXUS v0.1.0  —  http://0.0.0.0:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
