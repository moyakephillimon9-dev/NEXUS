/* ═══════════════════════════════════════════════════════
   NEXUS — Main JavaScript
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
    // Bold **text**, line breaks, code blocks
    return t
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  async function sendMessage(msg) {
    if (!msg || !msg.trim()) return;
    const input = inputEl();
    if (input) input.value = '';
    resizeTextarea(input);

    appendMsg('user', escHtml(msg));
    setWorking(true);

    const thinkEl = appendThinking();

    try {
      // Use SSE streaming
      const evtSrc = new EventSource(`/api/chat/stream?message=${encodeURIComponent(msg)}`);
      let full = '';
      let bubble = null;

      evtSrc.onmessage = e => {
        const data = JSON.parse(e.data);
        if (data.done) {
          evtSrc.close();
          setWorking(false);
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

    // Suggestion chips
    document.querySelectorAll('.chat-suggestion').forEach(el => {
      el.addEventListener('click', () => sendMessage(el.textContent.trim()));
    });

    // Clear chat
    const clearBtn = document.getElementById('chat-clear');
    if (clearBtn) clearBtn.addEventListener('click', async () => {
      await fetch('/api/chat/clear', {method:'POST'});
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
    // Type selection
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
        headers: {'Content-Type':'application/json'},
        body   : JSON.stringify({goal: `[${selectedType}] ${goal}`}),
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
    if (label) label.textContent = data.stage || '';

    const logs = data.logs || [];
    const console_el = document.getElementById('build-console');
    if (console_el) {
      // Only append new lines
      const existing = console_el.querySelectorAll('.log-line').length;
      for (let i = existing; i < logs.length; i++) {
        logLine(logs[i], logs[i].startsWith('[ERROR]') ? 'error' : (logs[i].includes('✓') ? 'success' : ''));
      }
    }

    if (data.status === 'complete') {
      logLine('✓ Build complete! Artifacts saved to deployments/', 'success');
    } else if (data.status === 'error') {
      logLine(`✗ Build failed: ${data.error || 'Unknown error'}`, 'error');
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

// ══════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function resizeTextarea(el) {
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
}

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
        if (cpuEl) cpuEl.style.width = `${w.cpu}%`;
        if (memEl) memEl.style.width = `${w.memory}%`;
      });
    } catch (_) {}
  }, 5000);
}

// ── Init ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Chat.init();
  Builder.init();
  initWorkersRefresh();

  // Fade-in page
  document.body.classList.add('fade-in');

  // Auto-expand textareas
  document.querySelectorAll('textarea.form-input').forEach(el => {
    el.addEventListener('input', () => resizeTextarea(el));
  });
});
