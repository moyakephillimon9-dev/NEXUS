/* ═══════════════════════════════════════════════════════
   NEXUS — Main JavaScript v2.0
   ═══════════════════════════════════════════════════════ */

'use strict';

// ── Live clock ─────────────────────────────────────────
function updateClock() {
  const el = document.getElementById('nexus-clock');
  if (!el) return;
  const now = new Date();
  const hh = String(now.getHours()).padStart(2,'0');
  const mm = String(now.getMinutes()).padStart(2,'0');
  const ss = String(now.getSeconds()).padStart(2,'0');
  const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  el.textContent = `${days[now.getDay()]}  ${hh}:${mm}:${ss}`;
}
setInterval(updateClock, 1000);
updateClock();

// ── Sidebar active state ───────────────────────────────
(function markActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href && path.startsWith(href)) a.classList.add('active');
    else a.classList.remove('active');
  });
})();

// ── Utility ────────────────────────────────────────────
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function resizeTextarea(el) {
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
}

// ══════════════════════════════════════════════════════
// CHAT BUILD INTENT — handles the "Launch Build" card
// ══════════════════════════════════════════════════════
const ChatBuild = (function() {
  let _goal = '';
  let _type = 'Web Application';

  function show(goal, type) {
    _goal = goal;
    _type = type || 'Web Application';
    const card = document.getElementById('build-intent-card');
    const label = document.getElementById('build-intent-goal-text');
    if (!card) return;
    if (label) label.textContent = goal.length > 90 ? goal.substring(0,90)+'…' : goal;
    card.style.display = 'block';
  }

  function dismiss() {
    const card = document.getElementById('build-intent-card');
    if (card) card.style.display = 'none';
  }

  function launch() {
    dismiss();
    // Open builder with pre-filled goal
    const encoded = encodeURIComponent(_goal);
    window.location.href = `/builder?goal=${encoded}&type=${encodeURIComponent(_type)}`;
  }

  return { show, dismiss, launch };
})();

// ══════════════════════════════════════════════════════
// WORKERS SIDEBAR (on chat page)
// ══════════════════════════════════════════════════════
const WorkersSidebar = (function() {
  let _evtSrc = null;
  let _msgCount = 0;

  function start() {
    const feed = document.getElementById('ws-feed');
    if (!feed) return;
    stop();

    _evtSrc = new EventSource('/api/workers/live');

    _evtSrc.onmessage = e => {
      try {
        const d = JSON.parse(e.data);
        if (d.heartbeat) {
          setActive(d.active_builds > 0);
          return;
        }
        appendActivity(d);
        setActive(true);
      } catch (_) {}
    };

    _evtSrc.onerror = () => {
      // Reconnect handled by browser
    };
  }

  function stop() {
    if (_evtSrc) { _evtSrc.close(); _evtSrc = null; }
  }

  function setActive(active) {
    const dot   = document.getElementById('ws-dot');
    const label = document.getElementById('ws-status-label');
    const stby  = document.getElementById('ws-standby');
    if (dot)   dot.className = 'ws-dot ' + (active ? 'active' : '');
    if (label) label.textContent = active ? 'Building' : 'Standby';
    if (stby)  stby.style.display = active ? 'none' : 'flex';
  }

  function appendActivity(d) {
    const feed  = document.getElementById('ws-feed');
    const stby  = document.getElementById('ws-standby');
    if (!feed) return;
    if (stby) stby.style.display = 'none';

    _msgCount++;
    // Keep feed manageable
    const existing = feed.querySelectorAll('.ws-msg');
    if (existing.length > 40) existing[0].remove();

    const div = document.createElement('div');
    div.className = 'ws-msg ws-msg-' + (d.type || 'info');
    const ico = {info:'⚡',code:'💻',success:'✅',error:'✗',thinking:'🔄'}[d.type] || '⚡';
    div.innerHTML = `
      <div class="ws-msg-header">
        <span class="ws-msg-icon">${ico}</span>
        <span class="ws-msg-worker">${escHtml(d.worker_name || 'Worker')}</span>
        <span class="ws-msg-time">${new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'})}</span>
      </div>
      <div class="ws-msg-body">${escHtml(d.message || '')}</div>
      ${d.code ? `<pre class="ws-code">${escHtml(d.code)}</pre>` : ''}
    `;
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  }

  return { start, stop };
})();

// ══════════════════════════════════════════════════════
// WORKERS ACTIVITY FEED (on workers page)
// ══════════════════════════════════════════════════════
const WorkersActivity = (function() {
  let _evtSrc = null;
  let _active = false;

  // Worker ID → element id mapping for card highlighting
  const WORKER_IDS = [
    'VISION-001','ASSESS-001','RESEARCH-001','MODULE-001','PLANNER-001',
    'ARCH-001','DB-001','CODER-001','DESIGN-001','REVIEW-001','TEST-001',
    'SEC-001','PERF-001','DOCS-001','MON-001','INT-001','DEVOPS-001',
    'DEPLOY-001','VERIFY-001','PROG-001','MEM-001','MGR-001'
  ];

  function start() {
    const feed = document.getElementById('activity-feed');
    if (!feed) return;
    stop();

    _evtSrc = new EventSource('/api/workers/live');

    _evtSrc.onmessage = e => {
      try {
        const d = JSON.parse(e.data);
        if (d.heartbeat) {
          if (!_active && d.active_builds === 0) setStandby();
          return;
        }
        setRunning();
        appendMsg(d);
        highlightWorker(d.worker_id);
      } catch (_) {}
    };
  }

  function stop() {
    if (_evtSrc) { _evtSrc.close(); _evtSrc = null; }
  }

  function setRunning() {
    _active = true;
    const dot    = document.getElementById('activity-live-dot');
    const badge  = document.getElementById('activity-status-badge');
    const sub    = document.getElementById('activity-subtitle');
    const stby   = document.getElementById('activity-standby');
    if (dot)   { dot.className = 'activity-dot active'; }
    if (badge) { badge.className = 'badge badge-cyan'; badge.textContent = '● Live'; }
    if (sub)   sub.textContent = 'Pipeline running — watching worker activity…';
    if (stby)  stby.style.display = 'none';
  }

  function setStandby() {
    _active = false;
    const dot   = document.getElementById('activity-live-dot');
    const badge = document.getElementById('activity-status-badge');
    const sub   = document.getElementById('activity-subtitle');
    if (dot)   dot.className = 'activity-dot standby';
    if (badge) { badge.className = 'badge badge-gray'; badge.textContent = 'Standby'; }
    if (sub)   sub.textContent = 'No active build — workers standing by';
  }

  function appendMsg(d) {
    const feed = document.getElementById('activity-feed');
    if (!feed) return;

    // Trim old messages
    const all = feed.querySelectorAll('.act-msg');
    if (all.length > 80) all[0].remove();

    const ico = {info:'⚡',code:'💻',success:'✅',error:'✗',thinking:'🔄'}[d.type||'info'] || '⚡';
    const typeClass = d.type || 'info';

    const div = document.createElement('div');
    div.className = `act-msg act-${typeClass}`;
    div.innerHTML = `
      <div class="act-header">
        <span class="act-icon">${ico}</span>
        <span class="act-worker">${escHtml(d.worker_name||'Worker')}</span>
        <span class="act-time">${new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'})}</span>
      </div>
      <div class="act-text">${escHtml(d.message||'')}</div>
      ${d.code ? `<pre class="act-code">${escHtml(d.code)}</pre>` : ''}
    `;

    // Typing animation for code
    if (d.type === 'code' && d.code) {
      animateCode(div.querySelector('.act-code'), d.code);
    }

    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  }

  function animateCode(el, code) {
    if (!el) return;
    el.textContent = '';
    const chars = code.split('');
    let i = 0;
    const iv = setInterval(() => {
      if (i >= chars.length) { clearInterval(iv); return; }
      el.textContent += chars[i++];
      el.parentElement && (el.parentElement.parentElement.scrollTop = el.parentElement.parentElement.scrollHeight);
    }, 18);
  }

  function highlightWorker(workerId) {
    if (!workerId) return;
    const card = document.getElementById(`wcard-${workerId}`);
    const chip = document.getElementById(`chip-${workerId}`);
    const task = document.getElementById(`wtask-${workerId}`);

    if (card) {
      card.classList.add('worker-card-active');
      setTimeout(() => card.classList.remove('worker-card-active'), 4000);
    }
    if (chip) {
      chip.classList.add('pipeline-stage-chip-active');
      setTimeout(() => chip.classList.remove('pipeline-stage-chip-active'), 4000);
    }
    if (task) {
      task.style.display = 'block';
      task.textContent = 'Working…';
      setTimeout(() => { task.style.display = 'none'; }, 5000);
    }

    // Update CPU/mem to show activity
    const cpuEl  = document.getElementById(`cpu-${workerId}`);
    const memEl  = document.getElementById(`mem-${workerId}`);
    const cpuPct = document.getElementById(`cpu-pct-${workerId}`);
    const memPct = document.getElementById(`mem-pct-${workerId}`);
    if (cpuEl) {
      const v = Math.floor(Math.random() * 50) + 40;
      cpuEl.style.width = v + '%';
      if (cpuPct) cpuPct.textContent = v + '%';
      setTimeout(() => {
        const idle = Math.floor(Math.random() * 13) + 2;
        cpuEl.style.width = idle + '%';
        if (cpuPct) cpuPct.textContent = idle + '%';
      }, 5000);
    }
    if (memEl) {
      const v = Math.floor(Math.random() * 30) + 30;
      memEl.style.width = v + '%';
      if (memPct) memPct.textContent = v + '%';
      setTimeout(() => {
        const idle = Math.floor(Math.random() * 35) + 10;
        memEl.style.width = idle + '%';
        if (memPct) memPct.textContent = idle + '%';
      }, 5000);
    }
  }

  return { start, stop };
})();

// ══════════════════════════════════════════════════════
// CHAT
// ══════════════════════════════════════════════════════
const Chat = (function() {
  const messagesEl = () => document.getElementById('chat-messages');
  const inputEl    = () => document.getElementById('chat-input');
  const statusEl   = () => document.getElementById('ai-status');

  function setWorking(yes) {
    const el = statusEl();
    if (!el) return;
    if (yes) { el.classList.add('working'); el.querySelector('.ai-label').textContent = 'Working'; }
    else     { el.classList.remove('working'); el.querySelector('.ai-label').textContent = 'Online'; }
  }

  function appendMsg(role, html, id) {
    const welcome = document.getElementById('chat-welcome');
    if (welcome) welcome.remove();

    const msgEl = messagesEl();
    if (!msgEl) return null;

    const isUser = (role === 'user');
    const avatar = isUser ? '👤' : '⚡';
    const sender = isUser ? 'You' : 'NEXUS';

    const div = document.createElement('div');
    div.className = `msg ${role}`;
    if (id) div.id = id;
    div.innerHTML = `
      <div class="msg-avatar">${avatar}</div>
      <div class="msg-body">
        <div class="msg-sender">${sender}</div>
        <div class="msg-bubble">${html}</div>
      </div>`;
    msgEl.appendChild(div);
    msgEl.scrollTop = msgEl.scrollHeight;
    return div;
  }

  function appendThinking() {
    return appendMsg('nexus',
      '<div class="thinking-dots"><span></span><span></span><span></span></div>',
      'thinking-bubble');
  }

  function removeThinking() {
    const el = document.getElementById('thinking-bubble');
    if (el) el.remove();
  }

  function formatText(t) {
    return t
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  async function sendMessage(msg) {
    if (!msg || !msg.trim()) return;
    const input = inputEl();
    if (input) { input.value = ''; resizeTextarea(input); }

    // Dismiss any previous build intent card
    ChatBuild.dismiss();

    appendMsg('user', escHtml(msg));
    setWorking(true);
    appendThinking();

    try {
      const evtSrc = new EventSource(`/api/chat/stream?message=${encodeURIComponent(msg)}`);
      let full   = '';
      let bubble = null;

      evtSrc.onmessage = e => {
        const data = JSON.parse(e.data);

        if (data.done) {
          evtSrc.close();
          setWorking(false);
          // Handle build intent
          if (data.intent && data.intent.is_build && data.intent.goal) {
            ChatBuild.show(data.intent.goal, data.intent.project_type);
          }
          return;
        }

        if (data.token !== undefined) {
          removeThinking();
          if (!bubble) {
            appendMsg('nexus', '', 'stream-bubble');
            bubble = document.querySelector('#stream-bubble .msg-bubble');
          }
          full += data.token;
          if (bubble) bubble.innerHTML = formatText(full);
          const mc = messagesEl();
          if (mc) mc.scrollTop = mc.scrollHeight;
        }
      };

      evtSrc.onerror = () => {
        evtSrc.close();
        removeThinking();
        setWorking(false);
        if (!bubble) appendMsg('nexus', '<span class="text-muted">Connection error. Please try again.</span>');
      };
    } catch (err) {
      removeThinking();
      setWorking(false);
      appendMsg('nexus', '<span class="text-muted">Error sending message.</span>');
    }
  }

  function init() {
    const input = inputEl();
    if (!input) return;

    input.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(input.value.trim());
      }
    });
    input.addEventListener('input', () => resizeTextarea(input));

    const sendBtn = document.getElementById('chat-send');
    if (sendBtn) sendBtn.addEventListener('click', () => sendMessage(input.value.trim()));

    document.querySelectorAll('.chat-suggestion').forEach(el => {
      el.addEventListener('click', () => sendMessage(el.textContent.trim()));
    });

    const clearBtn = document.getElementById('chat-clear');
    if (clearBtn) clearBtn.addEventListener('click', async () => {
      await fetch('/api/chat/clear', { method: 'POST' });
      const mc = messagesEl();
      if (mc) mc.innerHTML = '';
    });
  }

  return { init, sendMessage };
})();

// ══════════════════════════════════════════════════════
// BUILDER
// ══════════════════════════════════════════════════════
const Builder = (function() {
  let selectedType = 'Web Application';
  let currentTaskId = null;
  let pollTimer = null;

  function init() {
    document.querySelectorAll('.build-type').forEach(el => {
      el.addEventListener('click', () => {
        document.querySelectorAll('.build-type').forEach(x => x.classList.remove('selected'));
        el.classList.add('selected');
        selectedType = el.dataset.type;
        const goalInput = document.getElementById('build-goal');
        if (goalInput) goalInput.placeholder = `Describe your ${selectedType}…`;
      });
    });

    const form = document.getElementById('build-form');
    if (form) form.addEventListener('submit', startBuild);

    // Pre-fill from URL params (set by ChatBuild.launch())
    const params = new URLSearchParams(window.location.search);
    const preGoal = params.get('goal');
    const preType = params.get('type');
    if (preGoal) {
      const goalInput = document.getElementById('build-goal');
      if (goalInput) goalInput.value = decodeURIComponent(preGoal);
    }
    if (preType) {
      document.querySelectorAll('.build-type').forEach(el => {
        if (el.dataset.type === decodeURIComponent(preType)) {
          el.click();
        }
      });
    }
  }

  async function startBuild(e) {
    e.preventDefault();
    const goalEl = document.getElementById('build-goal');
    const goal   = goalEl ? goalEl.value.trim() : '';
    if (!goal) return;

    const btn = document.getElementById('build-btn');
    if (btn) { btn.disabled = true; btn.textContent = 'Starting…'; }

    showConsole();
    logLine(`[NEXUS] Starting pipeline for: ${goal}`);
    logLine(`[NEXUS] Type: ${selectedType}`);

    try {
      const res  = await fetch('/api/build', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ goal: `[${selectedType}] ${goal}` }),
      });
      const data = await res.json();
      if (data.task_id) {
        currentTaskId = data.task_id;
        logLine(`[NEXUS] Task ID: ${data.task_id}`);
        startPolling();
      } else {
        logLine(`[ERROR] ${data.error || 'Failed to start build'}`, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Start Building'; }
      }
    } catch (err) {
      logLine(`[ERROR] ${err.message}`, 'error');
      if (btn) { btn.disabled = false; btn.textContent = 'Start Building'; }
    }
  }

  function startPolling() {
    pollTimer = setInterval(async () => {
      if (!currentTaskId) return;
      try {
        const res  = await fetch(`/api/build/${currentTaskId}/status`);
        const data = await res.json();
        updateProgress(data);
        if (data.status === 'complete' || data.status === 'error') {
          clearInterval(pollTimer);
          const btn = document.getElementById('build-btn');
          if (btn) { btn.disabled = false; btn.textContent = 'Start New Build'; }
        }
      } catch (_) {}
    }, 1500);
  }

  function updateProgress(data) {
    const bar   = document.getElementById('build-progress-bar');
    const label = document.getElementById('build-stage-label');
    const pct   = document.getElementById('build-pct');
    if (bar)   bar.style.width = `${data.progress || 0}%`;
    if (pct)   pct.textContent = `${data.progress || 0}%`;
    if (label) {
      label.textContent = data.stage || '';
      label.className = 'build-stage-label' +
        (data.status === 'error' ? ' error' : data.status === 'complete' ? ' success' : '');
    }

    const logs     = data.logs || [];
    const cons_el  = document.getElementById('build-console');
    if (cons_el) {
      const existing = cons_el.querySelectorAll('.log-line').length;
      for (let i = existing; i < logs.length; i++) {
        const cls = logs[i].startsWith('[ERROR]') || logs[i].includes('✗') ? 'error'
                  : logs[i].includes('✓') ? 'success' : '';
        logLine(logs[i], cls);
      }
    }

    if (data.status === 'complete') {
      logLine('✓ All pipeline stages passed. Download your project from the artifacts section.', 'success');
    } else if (data.status === 'error') {
      logLine(`✗ Build failed: ${data.error || 'Pipeline was halted by a quality gate.'}`, 'error');
      logLine('✗ No download generated. Fix the issue and rebuild.', 'error');
    }
  }

  function showConsole() {
    const wrap = document.getElementById('build-progress-wrap');
    if (wrap) wrap.style.display = 'block';
    const con = document.getElementById('build-console');
    if (con) con.innerHTML = '';
  }

  function logLine(text, cls = '') {
    const con = document.getElementById('build-console');
    if (!con) return;
    const span = document.createElement('span');
    span.className = `log-line${cls ? ' ' + cls : ''}`;
    span.textContent = text;
    con.appendChild(span);
    con.appendChild(document.createElement('br'));
    con.scrollTop = con.scrollHeight;
  }

  return { init };
})();

// ── Workers auto-refresh ───────────────────────────────
function initWorkersRefresh() {
  const grid = document.getElementById('workers-grid');
  if (!grid) return;
  setInterval(async () => {
    try {
      const res = await fetch('/api/workers');
      const workers = await res.json();
      workers.forEach(w => {
        const cpuEl  = document.getElementById(`cpu-${w.id}`);
        const memEl  = document.getElementById(`mem-${w.id}`);
        // Only update if not currently highlighted as active
        if (cpuEl && !document.getElementById(`wcard-${w.id}`)?.classList.contains('worker-card-active')) {
          cpuEl.style.width = `${w.cpu}%`;
        }
        if (memEl && !document.getElementById(`wcard-${w.id}`)?.classList.contains('worker-card-active')) {
          memEl.style.width = `${w.memory}%`;
        }
      });
    } catch (_) {}
  }, 5000);
}

// ── Init ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Chat.init();
  Builder.init();
  initWorkersRefresh();

  // Start SSE feeds
  if (document.getElementById('ws-feed')) {
    WorkersSidebar.start();
  }
  if (document.getElementById('activity-feed')) {
    WorkersActivity.start();
  }

  // Fade-in
  document.body.classList.add('fade-in');

  document.querySelectorAll('textarea.form-input').forEach(el => {
    el.addEventListener('input', () => resizeTextarea(el));
  });
});
