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
# PUBLISH — App Store Publishing (founder-approval gated)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/publish')
@login_required
def publish():
    owner    = owner_mgr.get_owner()
    projects = _load_projects()
    requests = _load_publish_requests()
    return render_template('publish.html', owner=owner, projects=projects,
                           pub_requests=requests)


@app.route('/api/publish/request', methods=['POST'])
@login_required
def api_publish_request():
    """Create a pending publish request — must be approved by founder before executing."""
    data    = request.json or {}
    goal    = data.get('goal', '').strip()
    store   = data.get('store', '').strip()        # playstore | appstore | web
    task_id = data.get('task_id', '').strip()
    if not goal or not store:
        return jsonify({'success': False, 'error': 'goal and store are required'}), 400

    req_id  = f"pub_{int(time.time() * 1000)}"
    pub_req = {
        'id'          : req_id,
        'task_id'     : task_id,
        'goal'        : goal,
        'store'       : store,
        'status'      : 'pending',
        'created_at'  : datetime.datetime.now().isoformat(),
        'approved_at' : None,
        'package_path': None,
    }
    requests = _load_publish_requests()
    requests.append(pub_req)
    _save_publish_requests(requests)

    # SMS alert to founder
    owner = owner_mgr.get_owner()
    phone = owner.get('phone', '')
    if phone:
        _send_alert_sms(phone,
            f"⚠️ NEXUS Publish Request\nNEXUS wants to publish '{goal[:60]}' to {store}.\n"
            f"Log in → App Store Publish to approve or reject."
        )
    return jsonify({'success': True, 'request_id': req_id})


@app.route('/api/publish/approve/<req_id>', methods=['POST'])
@login_required
def api_publish_approve(req_id):
    """Founder approves a publish request → NEXUS generates the store package."""
    requests = _load_publish_requests()
    req = next((r for r in requests if r['id'] == req_id), None)
    if not req:
        return jsonify({'success': False, 'error': 'Request not found'}), 404
    if req['status'] != 'pending':
        return jsonify({'success': False, 'error': f"Already {req['status']}"}), 400

    req['status']      = 'approved'
    req['approved_at'] = datetime.datetime.now().isoformat()

    # Generate store package
    package_path = _generate_store_package(req)
    req['package_path'] = package_path
    req['status']       = 'packaged'
    _save_publish_requests(requests)

    owner = owner_mgr.get_owner()
    phone = owner.get('phone', '')
    if phone:
        _send_alert_sms(phone,
            f"✅ NEXUS Published\n'{req['goal'][:60]}' store package ready → {package_path}"
        )
    return jsonify({'success': True, 'package_path': package_path})


@app.route('/api/publish/reject/<req_id>', methods=['POST'])
@login_required
def api_publish_reject(req_id):
    """Founder rejects a publish request."""
    requests = _load_publish_requests()
    req = next((r for r in requests if r['id'] == req_id), None)
    if not req:
        return jsonify({'success': False, 'error': 'Request not found'}), 404
    req['status']      = 'rejected'
    req['rejected_at'] = datetime.datetime.now().isoformat()
    _save_publish_requests(requests)
    return jsonify({'success': True})


@app.route('/api/publish/<req_id>/download')
@login_required
def api_publish_download(req_id):
    """Zip and serve a store package."""
    requests = _load_publish_requests()
    req      = next((r for r in requests if r['id'] == req_id), None)
    if not req or not req.get('package_path'):
        return jsonify({'error': 'Package not found'}), 404
    base = Path(req['package_path'])
    if not base.exists():
        return jsonify({'error': 'Package folder missing'}), 404
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fp in sorted(base.rglob('*')):
            if fp.is_file():
                zf.write(fp, fp.relative_to(base))
    mem_zip.seek(0)
    return send_file(mem_zip, mimetype='application/zip', as_attachment=True,
                     download_name=f"{base.name}.zip")


# ═══════════════════════════════════════════════════════════════════════════════
# PROMOTE — Social Media & Google Ads
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/promote')
@login_required
def promote():
    owner    = owner_mgr.get_owner()
    promo    = _load_promo_data()
    return render_template('promote.html', owner=owner, promo=promo)


@app.route('/api/promote/post', methods=['POST'])
@login_required
def api_promote_post():
    data      = request.json or {}
    message   = data.get('message', '').strip()
    platforms = data.get('platforms', [])
    if not message:
        return jsonify({'success': False, 'error': 'Message is required'}), 400

    promo = _load_promo_data()
    entry = {
        'id'        : f"post_{int(time.time()*1000)}",
        'message'   : message,
        'platforms' : platforms,
        'status'    : 'queued',
        'created_at': datetime.datetime.now().isoformat(),
        'note'      : 'Platform API not yet connected — connect accounts in Settings to post live.',
    }
    promo.setdefault('posts', []).insert(0, entry)
    _save_promo_data(promo)
    return jsonify({'success': True, 'post_id': entry['id'],
                    'note': entry['note']})


@app.route('/api/promote/campaign', methods=['POST'])
@login_required
def api_promote_campaign():
    data   = request.json or {}
    name   = data.get('name', '').strip()
    budget = data.get('budget', 0)
    goal   = data.get('goal', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Campaign name required'}), 400
    promo   = _load_promo_data()
    campaign = {
        'id'        : f"camp_{int(time.time()*1000)}",
        'name'      : name,
        'budget_usd': float(budget),
        'goal'      : goal,
        'status'    : 'draft',
        'created_at': datetime.datetime.now().isoformat(),
        'note'      : 'Google Ads API not yet connected — add credentials in Settings to go live.',
    }
    promo.setdefault('campaigns', []).insert(0, campaign)
    _save_promo_data(promo)
    return jsonify({'success': True, 'campaign_id': campaign['id'],
                    'note': campaign['note']})


# ═══════════════════════════════════════════════════════════════════════════════
# REVENUE — Dashboard & Tracking
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/revenue')
@login_required
def revenue():
    owner   = owner_mgr.get_owner()
    rev     = _load_revenue_data()
    summary = _revenue_summary(rev)
    return render_template('revenue.html', owner=owner, revenue=rev, summary=summary)


@app.route('/api/revenue/entry', methods=['POST'])
@login_required
def api_revenue_entry():
    """Manual revenue entry (until platform APIs are connected)."""
    data   = request.json or {}
    amount = float(data.get('amount', 0))
    source = data.get('source', 'manual').strip()
    note   = data.get('note', '').strip()
    if amount <= 0:
        return jsonify({'success': False, 'error': 'Amount must be > 0'}), 400
    rev = _load_revenue_data()
    entry = {
        'id'        : f"rev_{int(time.time()*1000)}",
        'amount_usd': amount,
        'source'    : source,
        'note'      : note,
        'date'      : datetime.datetime.now().isoformat(),
    }
    rev.setdefault('entries', []).insert(0, entry)
    _save_revenue_data(rev)

    # SMS if milestone hit
    total = sum(e.get('amount_usd', 0) for e in rev['entries'])
    owner = owner_mgr.get_owner()
    phone = owner.get('phone', '')
    for milestone in [10, 50, 100, 500, 1000, 5000, 10000]:
        prev = total - amount
        if prev < milestone <= total and phone:
            _send_alert_sms(phone,
                f"🎉 NEXUS Revenue Milestone!\nYou've earned ${milestone}+ total. "
                f"Latest: ${amount:.2f} from {source}."
            )
            break
    return jsonify({'success': True, 'entry': entry, 'total_usd': total})


@app.route('/api/revenue/alert-threshold', methods=['POST'])
@login_required
def api_revenue_alert_threshold():
    data = request.json or {}
    rev  = _load_revenue_data()
    rev['alert_threshold'] = float(data.get('threshold', 100))
    _save_revenue_data(rev)
    return jsonify({'success': True})


@app.route('/api/revenue/payout-method', methods=['POST'])
@login_required
def api_revenue_payout_method():
    """Save the owner's preferred payout method."""
    data   = request.json or {}
    method = data.get('method', '').strip()   # paypal | bank | stripe
    detail = data.get('detail', '').strip()   # PayPal email / account number / Stripe ID
    name   = data.get('name', '').strip()     # account holder name (bank)
    if not method or not detail:
        return jsonify({'success': False, 'error': 'Method and account detail are required.'}), 400
    rev = _load_revenue_data()
    rev['payout_method'] = {'method': method, 'detail': detail, 'name': name,
                            'updated_at': datetime.datetime.now().isoformat()}
    _save_revenue_data(rev)
    return jsonify({'success': True})


@app.route('/api/revenue/withdraw', methods=['POST'])
@login_required
def api_revenue_withdraw():
    """Request a withdrawal to the saved payout method."""
    data   = request.json or {}
    amount = float(data.get('amount', 0))
    rev    = _load_revenue_data()

    payout_method = rev.get('payout_method')
    if not payout_method:
        return jsonify({'success': False, 'error': 'No payout method saved. Add one first.'}), 400

    # Calculate available balance
    earned    = sum(e.get('amount_usd', 0) for e in rev.get('entries', []))
    withdrawn = sum(w.get('amount_usd', 0) for w in rev.get('withdrawals', [])
                    if w.get('status') != 'rejected')
    available = earned - withdrawn

    if amount <= 0:
        return jsonify({'success': False, 'error': 'Enter an amount greater than $0.'}), 400
    if amount > available:
        return jsonify({'success': False,
                        'error': f'Insufficient balance. Available: ${available:.2f}'}), 400

    withdrawal = {
        'id'        : f"wd_{int(time.time()*1000)}",
        'amount_usd': amount,
        'method'    : payout_method['method'],
        'detail'    : payout_method['detail'],
        'status'    : 'pending',
        'requested_at': datetime.datetime.now().isoformat(),
        'note'      : data.get('note', '').strip(),
    }
    rev.setdefault('withdrawals', []).insert(0, withdrawal)
    _save_revenue_data(rev)

    # SMS confirmation
    owner = owner_mgr.get_owner()
    phone = owner.get('phone', '')
    if phone:
        _send_alert_sms(phone,
            f"💸 NEXUS Withdrawal Request\n"
            f"${amount:.2f} → {payout_method['method'].upper()} ({payout_method['detail'][:30]})\n"
            f"Status: Pending. Log in to confirm."
        )
    return jsonify({'success': True, 'withdrawal': withdrawal, 'available': available - amount})


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
    """
    Run the NEXUS pipeline in a background thread, updating active_builds.

    Honesty contract
    ─────────────────
    • status='complete' is set ONLY when ALL 21 stages pass AND a deployment
      folder exists on disk.
    • status='error' is set for ANY gate halt, missing output, or exception.
    • A download link is NEVER generated unless status='complete'.
    • The exact failed stage, reason, and suggested fix are always surfaced.
    """
    build      = active_builds[task_id]
    start_time = time.time()

    try:
        build['status']    = 'running'
        build['stage']     = 'Initializing'
        build['progress']  = 2
        build['logs'].append("[NEXUS] ⚡ Pipeline starting…")
        build['logs'].append(f"[NEXUS] Goal: {goal[:120]}{'…' if len(goal) > 120 else ''}")
        build['logs'].append(f"[NEXUS] Stages queued: {len(PIPELINE_STAGES)}")

        # Brief stage-listing phase (honest: "queuing", not "running")
        for idx, (wid, name, action) in enumerate(PIPELINE_STAGES):
            build['stage']     = f"Queuing: {name}"
            build['stage_idx'] = idx
            build['progress']  = 2 + int(((idx + 1) / len(PIPELINE_STAGES)) * 13)  # 2→15 %
            build['logs'].append(f"  [{wid:12s}] {action}")
            time.sleep(0.08)

        build['stage']    = 'Executing Pipeline…'
        build['progress'] = 16
        build['logs'].append("[NEXUS] All stages queued. Handing off to orchestrator…")

        # ── Real orchestrator ──────────────────────────────────────────────
        from core.orchestrator import Orchestrator
        orch    = Orchestrator()
        project = orch.run(goal)
        elapsed = round(time.time() - start_time, 1)

        # ── Gate-halt: orchestrator returned None (old path, safety net) ──
        if project is None:
            build['status']   = 'error'
            build['progress'] = 0
            build['stage']    = '✗ Pipeline Halted'
            build['error']    = 'A quality gate blocked the build. Review the logs above for which stage failed.'
            build['logs'].append("[NEXUS] ✗ Pipeline halted — quality gate blocked release.")
            build['logs'].append("[NEXUS] No download generated.")
            return

        # ── Structured error returned by a gate halt ───────────────────────
        if isinstance(project, dict) and project.get('error'):
            failed  = project.get('failed_stage', 'Unknown Stage')
            reason  = project.get('reason',       'No reason provided.')
            suggest = project.get('suggestion',   '')
            build['status']   = 'error'
            build['progress'] = 0
            build['stage']    = f"✗ {failed}"
            build['error']    = f"{failed}: {reason}"
            build['logs'].append(f"[NEXUS] ✗ STAGE FAILED: {failed}")
            build['logs'].append(f"[NEXUS]   Reason  : {reason}")
            if suggest:
                build['logs'].append(f"[NEXUS]   Fix     : {suggest}")
            build['logs'].append("[NEXUS] ✗ No download generated. Fix the issue and rebuild.")
            return

        # ── Unexpected return type ─────────────────────────────────────────
        if not isinstance(project, dict):
            build['status']   = 'error'
            build['progress'] = 0
            build['stage']    = '✗ Internal Error'
            build['error']    = f'Orchestrator returned unexpected type: {type(project).__name__}'
            build['logs'].append(f"[NEXUS] ✗ Internal error — unexpected orchestrator result.")
            return

        # ── Verify deployment output exists on disk ────────────────────────
        deploy_path = project.get('deployment', {}).get('deployment_path')
        if not deploy_path or not Path(deploy_path).exists():
            build['status']   = 'error'
            build['progress'] = 0
            build['stage']    = '✗ No Deployment Output'
            build['error']    = 'All stages ran but no deployment folder was created on disk.'
            build['logs'].append("[NEXUS] ✗ Deployment folder missing — build incomplete.")
            build['logs'].append("[NEXUS] ✗ No download generated.")
            return

        # ── Verification summary (already blocked in orchestrator if failed) #
        verification = project.get('verification', {})
        v_score = verification.get('verification_score', '?')
        v_checks = f"{verification.get('checks_passed','?')}/{verification.get('checks_total','?')}"
        build['logs'].append(f"[VERIFY] Score: {v_score}%  Checks: {v_checks}")

        # ── ALL gates passed — mark complete ───────────────────────────────
        build['status']      = 'complete'
        build['progress']    = 100
        build['stage']       = '✓ Complete'
        build['deploy_path'] = deploy_path
        build['result']      = {
            'framework'    : project.get('architecture', {}).get('framework', 'Python'),
            'language'     : project.get('architecture', {}).get('language',  'Python'),
            'deploy_path'  : deploy_path,
            'has_artifacts': True,
        }
        build['logs'].append(f"[NEXUS] ✓ All {len(PIPELINE_STAGES)} stages passed.")
        build['logs'].append(f"[NEXUS] ✓ Project saved → {deploy_path}")
        build['logs'].append(f"[NEXUS] ✓ Build completed in {elapsed}s")
        _notify_build_complete(goal, deploy_path)

    except Exception as exc:
        elapsed = round(time.time() - start_time, 1)
        build['status']   = 'error'
        build['progress'] = 0
        build['stage']    = '✗ Exception'
        build['error']    = str(exc)
        build['logs'].append(f"[ERROR] {exc}")
        build['logs'].append(f"[NEXUS] ✗ Pipeline crashed after {elapsed}s. No download generated.")


# ── Publish helpers ────────────────────────────────────────────────────────────

def _load_publish_requests() -> list:
    fp = Config.ROOT / 'data' / 'publish_requests.json'
    if fp.exists():
        try:
            with open(fp) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _save_publish_requests(requests: list):
    fp = Config.ROOT / 'data' / 'publish_requests.json'
    fp.parent.mkdir(exist_ok=True)
    with open(fp, 'w') as f:
        json.dump(requests, f, indent=2)

def _generate_store_package(req: dict) -> str:
    """Generate a store submission package folder for the given publish request."""
    store   = req.get('store', 'playstore')
    goal    = req.get('goal', 'app')[:50].replace(' ', '_').replace('/', '_')
    req_id  = req.get('id', 'pkg')
    folder  = Config.ROOT / 'deployments' / f"store_{req_id}_{goal}"
    folder.mkdir(parents=True, exist_ok=True)

    store_meta = {
        'store'           : store,
        'app_name'        : req.get('goal', 'My App')[:30],
        'short_description': req.get('goal', '')[:80],
        'long_description' : (
            f"{req.get('goal', 'App')} — Built and packaged by NEXUS AI Operating System.\n\n"
            "Powered by NEXUS · nexus.ai"
        ),
        'version'         : '1.0.0',
        'package_name'    : f"ai.nexus.{goal.lower()[:20]}",
        'category'        : 'Productivity',
        'content_rating'  : 'Everyone',
        'generated_at'    : datetime.datetime.now().isoformat(),
    }

    with open(folder / 'store_listing.json', 'w') as f:
        json.dump(store_meta, f, indent=2)

    readme_lines = [
        f"# {req.get('goal', 'App')} — Store Submission Package",
        f"\nGenerated by NEXUS AI · {store}",
        "\n## Files in this package",
        "- `store_listing.json` — App metadata (title, description, category, etc.)",
        "- `SUBMISSION_GUIDE.md` — Step-by-step submission instructions",
        "- `screenshots/` — Add your screenshots here (required by stores)",
        "\n## Next Steps",
    ]
    if store == 'playstore':
        readme_lines += [
            "1. Go to https://play.google.com/console",
            "2. Create a new application",
            "3. Copy values from store_listing.json into the store listing form",
            "4. Upload your APK/AAB (from your build output)",
            "5. Add screenshots (min 2, max 8 — 1080×1920 recommended)",
            "6. Submit for review (3–7 days)",
        ]
    elif store == 'appstore':
        readme_lines += [
            "1. Go to https://appstoreconnect.apple.com",
            "2. Create a new app",
            "3. Copy values from store_listing.json",
            "4. Upload IPA via Xcode or Transporter",
            "5. Add screenshots (required for each device size)",
            "6. Submit for review (1–3 days)",
        ]
    else:
        readme_lines += [
            "1. Build your project: `npm run build` or `python main.py`",
            "2. Upload the output folder to your hosting provider",
            "3. Set the domain in your DNS settings",
        ]
    readme_lines.append("\n---\n*Built with NEXUS AI Operating System — nexus.ai*")

    with open(folder / 'SUBMISSION_GUIDE.md', 'w') as f:
        f.write('\n'.join(readme_lines))

    (folder / 'screenshots').mkdir(exist_ok=True)
    with open(folder / 'screenshots' / 'README.txt', 'w') as f:
        f.write("Add your app screenshots here before submitting to the store.\n"
                "Recommended: 1080x1920 PNG, at least 2 screenshots.\n")

    return str(folder)


# ── Promote helpers ────────────────────────────────────────────────────────────

def _load_promo_data() -> dict:
    fp = Config.ROOT / 'data' / 'promo.json'
    if fp.exists():
        try:
            with open(fp) as f:
                return json.load(f)
        except Exception:
            pass
    return {'posts': [], 'campaigns': [], 'connected_platforms': []}

def _save_promo_data(data: dict):
    fp = Config.ROOT / 'data' / 'promo.json'
    fp.parent.mkdir(exist_ok=True)
    with open(fp, 'w') as f:
        json.dump(data, f, indent=2)


# ── Revenue helpers ────────────────────────────────────────────────────────────

def _load_revenue_data() -> dict:
    fp = Config.ROOT / 'data' / 'revenue.json'
    if fp.exists():
        try:
            with open(fp) as f:
                return json.load(f)
        except Exception:
            pass
    return {'entries': [], 'alert_threshold': 100}

def _save_revenue_data(data: dict):
    fp = Config.ROOT / 'data' / 'revenue.json'
    fp.parent.mkdir(exist_ok=True)
    with open(fp, 'w') as f:
        json.dump(data, f, indent=2)

def _revenue_summary(rev: dict) -> dict:
    entries    = rev.get('entries', [])
    total      = sum(e.get('amount_usd', 0) for e in entries)
    now        = datetime.datetime.now()
    this_month = sum(
        e.get('amount_usd', 0) for e in entries
        if e.get('date', '')[:7] == now.strftime('%Y-%m')
    )
    by_source: dict = {}
    for e in entries:
        s = e.get('source', 'other')
        by_source[s] = by_source.get(s, 0) + e.get('amount_usd', 0)
    return {
        'total_usd'      : total,
        'this_month_usd' : this_month,
        'entry_count'    : len(entries),
        'by_source'      : dict(sorted(by_source.items(), key=lambda x: x[1], reverse=True)),
    }


# ── Alert / pipeline helpers ───────────────────────────────────────────────────

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
