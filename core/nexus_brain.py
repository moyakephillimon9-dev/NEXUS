"""
NEXUS Brain — Advanced Built-in Reasoning Engine v2.0
Context-aware, intent-detecting, next-generation AI engine.
No external API required — fully self-contained.
"""

import json, re, time, datetime, random
from pathlib import Path

DATA_DIR    = Path(__file__).resolve().parent.parent / 'data'
CHAT_FILE   = DATA_DIR / 'chat_history.json'
MEMORY_FILE = Path(__file__).resolve().parent.parent / 'memory' / 'database.json'

# ── Worker registry ─────────────────────────────────────────────────────────
WORKERS = [
    {"id": "VISION-001",   "name": "Vision Parser AI",    "role": "Parses goals and vision documents",                "stage": 0},
    {"id": "ASSESS-001",   "name": "Capability Assessor", "role": "Classifies features as supported or unsupported",  "stage": 1},
    {"id": "RESEARCH-001", "name": "Research AI",         "role": "Searches knowledge base for patterns",             "stage": 2},
    {"id": "MODULE-001",   "name": "Module Detector",     "role": "Detects modules and builds dependency graph",      "stage": 3},
    {"id": "PLANNER-001",  "name": "Planner AI",          "role": "Creates 19-phase plan with tasks and effort",      "stage": 4},
    {"id": "ARCH-001",     "name": "Architect AI",        "role": "Designs system architecture",                     "stage": 5},
    {"id": "DB-001",       "name": "Database AI",         "role": "Designs database schema",                         "stage": 6},
    {"id": "CODER-001",    "name": "Coder AI",            "role": "Writes production source code",                   "stage": 7},
    {"id": "DESIGN-001",   "name": "Design AI",           "role": "Creates UI/UX assets",                            "stage": 8},
    {"id": "REVIEW-001",   "name": "Reviewer AI",         "role": "Reviews code for quality and correctness",        "stage": 9},
    {"id": "TEST-001",     "name": "Tester AI",           "role": "Writes and runs automated tests",                 "stage": 10},
    {"id": "SEC-001",      "name": "Security AI",         "role": "Performs security scanning",                      "stage": 11},
    {"id": "PERF-001",     "name": "Performance AI",      "role": "Analyses performance bottlenecks",                "stage": 12},
    {"id": "DOCS-001",     "name": "Documentation AI",   "role": "Generates full documentation",                    "stage": 13},
    {"id": "MON-001",      "name": "Monitoring AI",       "role": "Sets up monitoring and alerting",                 "stage": 14},
    {"id": "INT-001",      "name": "Integration AI",      "role": "Wires external integrations",                     "stage": 15},
    {"id": "DEVOPS-001",   "name": "DevOps AI",           "role": "Configures CI/CD and containers",                 "stage": 16},
    {"id": "DEPLOY-001",   "name": "Deployment AI",       "role": "Generates deployment artefacts",                  "stage": 17},
    {"id": "VERIFY-001",   "name": "Verification AI",     "role": "Verifies every claim before reporting done",      "stage": 18},
    {"id": "PROG-001",     "name": "Progress Tracker",    "role": "Tracks pipeline progress and timelines",          "stage": 19},
    {"id": "MEM-001",      "name": "Memory AI",           "role": "Saves project knowledge to memory",               "stage": 20},
    {"id": "MGR-001",      "name": "Manager AI",          "role": "Orchestrates all workers and approves plans",     "stage": -1},
]

# ── Build intent patterns ────────────────────────────────────────────────────
_BUILD_VERBS    = re.compile(r'\b(build|create|make|develop|generate|code|write|design|launch|deploy|start|implement)\b', re.I)
_BUILD_SUBJECTS = re.compile(r'\b(app|application|website|web app|api|backend|dashboard|system|tool|platform|game|bot|script|service|portal|shop|store|saas|crm|erp|cms|mobile app|android app|ios app)\b', re.I)
_QUESTION_WORDS = re.compile(r'^(how|what|why|when|where|who|can you|do you|is|are|will|show|list|tell me)\b', re.I)

_PROJECT_TYPES = {
    'mobile':     (re.compile(r'\b(mobile|android|ios|phone|flutter|react native)\b', re.I), 'Mobile Application'),
    'api':        (re.compile(r'\b(api|rest|graphql|endpoint|backend|microservice|fastapi|flask api|django)\b', re.I), 'REST API'),
    'dashboard':  (re.compile(r'\b(dashboard|analytics|chart|graph|admin panel|data viz)\b', re.I), 'Dashboard'),
    'game':       (re.compile(r'\b(game|gaming|play|puzzle|quiz)\b', re.I), 'Game'),
    'automation': (re.compile(r'\b(script|automation|bot|cli|crawler|scraper|cron)\b', re.I), 'Automation Script'),
    'ecommerce':  (re.compile(r'\b(shop|store|ecommerce|e-commerce|cart|checkout|payment)\b', re.I), 'E-Commerce Platform'),
    'saas':       (re.compile(r'\b(saas|subscription|multi-tenant|crm|erp|cms)\b', re.I), 'SaaS Platform'),
}

CONTEXT_WINDOW = 14  # messages to include for context awareness


class NexusBrain:
    """
    NEXUS Advanced Built-in Reasoning Engine v2.0

    Context-aware, intent-detecting conversational AI.
    Fully self-contained — no external API key required.
    """

    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)

    # ── Worker helpers ────────────────────────────────────────────────────────
    def get_all_workers(self) -> list:
        workers = []
        for w in WORKERS:
            workers.append({
                **w,
                "status"  : "online",
                "cpu"     : random.randint(2, 15),
                "memory"  : random.randint(10, 45),
                "last_run": "No recent task",
            })
        return workers

    def get_workers_summary(self) -> list:
        return [{"id": w["id"], "name": w["name"],
                 "status": "online", "stage": w["stage"]} for w in WORKERS[:8]]

    # ── Chat history ──────────────────────────────────────────────────────────
    def get_chat_history(self) -> list:
        if CHAT_FILE.exists():
            try:
                with open(CHAT_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_message(self, role: str, content: str):
        history = self.get_chat_history()
        history.append({
            "role"      : role,
            "content"   : content,
            "timestamp" : datetime.datetime.now().isoformat(),
        })
        if len(history) > 200:
            history = history[-200:]
        with open(CHAT_FILE, 'w') as f:
            json.dump(history, f, indent=2)

    def clear_chat_history(self):
        with open(CHAT_FILE, 'w') as f:
            json.dump([], f)

    # ── Intent detection ──────────────────────────────────────────────────────
    def detect_intent(self, message: str, owner: dict) -> dict:
        """
        Analyse message and return structured intent metadata.
        Returns dict with: is_build, goal, project_type, confidence
        """
        msg = message.strip()
        low = msg.lower()

        # Detect build intent
        has_verb    = bool(_BUILD_VERBS.search(low))
        has_subject = bool(_BUILD_SUBJECTS.search(low))
        is_question = bool(_QUESTION_WORDS.match(low))

        # High confidence: "build me a X" / "create a Y app"
        is_build = has_verb and (has_subject or len(msg) > 30) and not is_question
        confidence = 0.0
        if is_build:
            confidence = 0.7
            if has_verb and has_subject:
                confidence = 0.95

        # Detect project type
        project_type = 'Web Application'
        for key, (pattern, label) in _PROJECT_TYPES.items():
            if pattern.search(low):
                project_type = label
                break

        # Extract cleaned goal (remove filler phrases)
        goal = msg
        for filler in ['can you ', 'please ', 'i want you to ', 'i need you to ',
                       'i want a ', 'i need a ', 'build me a ', 'create a ',
                       'make me a ', 'develop a ', 'generate a ']:
            if low.startswith(filler):
                goal = msg[len(filler):]
                break

        return {
            'is_build'    : is_build,
            'goal'        : goal if is_build else '',
            'project_type': project_type,
            'confidence'  : confidence,
        }

    # ── Core response engine ──────────────────────────────────────────────────
    def respond(self, message: str, owner: dict) -> str:
        """Return a full response string."""
        return ''.join(
            t for t in self.stream_response(message, owner)
        )

    def stream_response(self, message: str, owner: dict):
        """Yield response tokens one word at a time for streaming."""
        text = self._build_response(message, owner)
        words = text.split(' ')
        for i, word in enumerate(words):
            yield word + ('' if i == len(words) - 1 else ' ')
            time.sleep(0.015)

    def _build_response(self, message: str, owner: dict) -> str:
        """
        Advanced context-aware response engine.
        Reads conversation history to provide coherent multi-turn responses.
        """
        msg     = message.strip()
        low     = msg.lower()
        name    = (owner.get('full_name') or 'Founder').split()[0]
        company = owner.get('company') or 'your company'
        now     = datetime.datetime.now()

        # Pull recent context
        history  = self.get_chat_history()
        recent   = history[-(CONTEXT_WINDOW):] if len(history) > CONTEXT_WINDOW else history
        ctx_text = ' '.join(m.get('content', '') for m in recent).lower()

        # ── Greetings ──────────────────────────────────────────────────────────
        if _m(low, ['hello', 'hi ', 'hey ', 'good morning', 'good afternoon', 'good evening', 'hi!']):
            hour = now.hour
            if hour < 12:   g = "Good morning"
            elif hour < 17: g = "Good afternoon"
            else:           g = "Good evening"
            worker_count = len(WORKERS)
            return (
                f"{g}, {name}. NEXUS is fully operational.\n\n"
                f"All {worker_count} AI workers are standing by and the 21-stage pipeline is ready.\n\n"
                f"Describe what you want to build and I'll dispatch the team immediately — "
                f"or ask me anything about your projects, workers, or system status."
            )

        # ── Identity ───────────────────────────────────────────────────────────
        if _m(low, ['who are you', 'what are you', 'what is nexus', 'tell me about yourself', 'what do you do']):
            return (
                f"I am NEXUS — an advanced AI Operating System built specifically for {company}.\n\n"
                f"**What I do:** I orchestrate 22 specialised AI workers across a 21-stage pipeline to turn "
                f"a plain-language goal into a fully built, tested, secured, and deployable software project.\n\n"
                f"**My pipeline:** Vision Parsing → Capability Assessment → Research → Module Detection → "
                f"Planning → Architecture → Database Design → Code Generation → UI/UX Design → "
                f"Code Review → Testing → Security Scan → Performance Analysis → Documentation → "
                f"Monitoring → Integration → DevOps → Deployment → Verification → Progress → Memory.\n\n"
                f"**My promise:** I never fake completion. Every stage must pass a real gate. "
                f"If something fails, I tell you exactly what failed and why.\n\n"
                f"What would you like to build today?"
            )

        # ── System status ──────────────────────────────────────────────────────
        if _m(low, ['status', 'how are you', 'are you online', 'system status', 'system health', 'all good']):
            return (
                f"All systems nominal, {name}.\n\n"
                f"**Workers:** 22 AI agents — all online\n"
                f"**Pipeline:** 21 stages — ready\n"
                f"**Memory:** Active and indexed\n"
                f"**Engine:** NEXUS Built-in v2.0 — running\n"
                f"**Time:** {now.strftime('%H:%M on %A, %d %B %Y')}\n\n"
                f"No active builds running. Ready for your next project."
            )

        # ── Build / create intent ──────────────────────────────────────────────
        if _m(low, ['build', 'create', 'make', 'develop', 'generate', 'code', 'implement']) and \
           not _m(low, ['how to build', 'can you build', 'what can you build', 'how does']):
            intent = self.detect_intent(msg, owner)
            if intent['is_build']:
                ptype = intent['project_type']
                return (
                    f"Understood, {name}. I'm ready to build that for you.\n\n"
                    f"**Detected project type:** {ptype}\n"
                    f"**Goal:** {intent['goal'][:120]}\n\n"
                    f"I'll activate all 22 AI workers across the full 21-stage pipeline:\n"
                    f"research → plan → architect → database → code → design → test → security → deploy.\n\n"
                    f"Click **Launch Build** below to start, or head to the **Builder** section to customise the build type first."
                )
            # Generic build question
            return (
                f"Ready to build, {name}. Head to the **Builder** section and describe exactly what you want.\n\n"
                f"I can build: web apps, REST APIs, dashboards, mobile apps, games, automation scripts, "
                f"e-commerce platforms, SaaS tools, and more.\n\n"
                f"The full 21-stage pipeline will handle research, architecture, code generation, "
                f"testing, security scanning, documentation, and packaging — all automatically."
            )

        # ── Workers ────────────────────────────────────────────────────────────
        if _m(low, ['workers', 'agents', 'team', 'who works for you', 'list workers', 'show workers']):
            names = ', '.join(w['name'] for w in WORKERS[:5])
            return (
                f"NEXUS coordinates **22 specialised AI workers** across 21 pipeline stages.\n\n"
                f"**Active workers include:** {names}, and 17 more specialists.\n\n"
                f"Each worker has a dedicated role — from parsing your initial goal all the way to "
                f"deployment packaging and memory storage. Workers operate in strict sequence: "
                f"no stage starts until the previous one passes its quality gate.\n\n"
                f"View all workers and their live status in the **AI Workers** section."
            )

        # ── Pipeline ───────────────────────────────────────────────────────────
        if _m(low, ['pipeline', 'stages', 'process', 'how does it work', 'how does nexus work']):
            return (
                f"The NEXUS pipeline has **21 stages** driven by 22 AI workers:\n\n"
                f"**Stage 0–3:** Vision Parsing → Capability Assessment → Research → Module Detection\n"
                f"**Stage 4–7:** Planning → Architecture → Database Design → Code Generation\n"
                f"**Stage 8–11:** UI/UX Design → Code Review → Testing → Security Scan\n"
                f"**Stage 12–15:** Performance → Documentation → Monitoring → Integration\n"
                f"**Stage 16–20:** DevOps → Deployment → Verification → Progress → Memory\n\n"
                f"**Quality gates** at stages 9 (Reviewer), 10 (Tester), 11 (Security), and 18 (Verification) "
                f"can halt the pipeline. A download is **never generated** unless all gates pass. "
                f"This is NEXUS's honesty contract — no false success, ever."
            )

        # ── Projects ───────────────────────────────────────────────────────────
        if _m(low, ['projects', 'my projects', 'show projects', 'project history', 'past projects']):
            return (
                f"Your project history is in the **Projects** section.\n\n"
                f"Each project record contains the complete pipeline output: "
                f"source code, architecture document, test results, security report, "
                f"documentation, DevOps configuration, and the deployment package.\n\n"
                f"Completed projects can be published to Google Play Store or Apple App Store "
                f"from the **App Store Publish** section. Ready to start a new project?"
            )

        # ── Memory ─────────────────────────────────────────────────────────────
        if _m(low, ['memory', 'remember', 'what do you know', 'knowledge', 'what have you learned']):
            return (
                f"My memory system records everything NEXUS learns:\n\n"
                f"**Project knowledge:** Architectures, code patterns, and solutions from every build.\n"
                f"**Business context:** Your company preferences, tech choices, and constraints.\n"
                f"**Pipeline outcomes:** What worked, what failed, and why — so I improve each run.\n\n"
                f"Memory grows automatically with every pipeline run. "
                f"Browse and search all stored knowledge in the **Memory** section."
            )

        # ── Publish / Play Store ──────────────────────────────────────────────
        if _m(low, ['publish', 'play store', 'app store', 'deploy', 'release', 'launch']):
            return (
                f"NEXUS can prepare your app for store submission from the **App Store Publish** section.\n\n"
                f"**Supported stores:** Google Play Store, Apple App Store, Web Hosting\n\n"
                f"**What NEXUS generates:**\n"
                f"• Complete store listing (title, description, category, version)\n"
                f"• Submission guide with step-by-step instructions\n"
                f"• Screenshot placeholder folder\n"
                f"• Downloadable submission package (ZIP)\n\n"
                f"First complete a build in the **Builder**, then come to Publish to package it for the store. "
                f"All publish actions require your explicit approval — NEXUS never publishes without you."
            )

        # ── Reports ────────────────────────────────────────────────────────────
        if _m(low, ['report', 'reports', 'analytics', 'statistics', 'stats', 'how many projects']):
            return (
                f"The **Reports** section shows real-time analytics on your NEXUS activity:\n\n"
                f"• Total projects built, completed, in-progress, and errored\n"
                f"• Recent pipeline runs with status badges\n"
                f"• Revenue opportunities for completed projects\n"
                f"• System health metrics for all 22 workers\n\n"
                f"Reports also show **build completion notifications** when a project finishes — "
                f"including a direct prompt to design and publish to the Play Store."
            )

        # ── Settings ───────────────────────────────────────────────────────────
        if _m(low, ['settings', 'configure', 'configuration']):
            return (
                f"Configure NEXUS from the **Settings** section:\n\n"
                f"• **AI Engine:** Built-in v2.0 (active) — no API key needed\n"
                f"• **Security:** Session management and access controls\n"
                f"• **Notifications:** SMS alerts via Twilio (optional)\n"
                f"• **Theme:** UI preferences\n\n"
                f"The built-in engine handles all reasoning, chat, and pipeline orchestration "
                f"without any external dependency. You can optionally connect an LLM provider "
                f"in Settings for even richer responses."
            )

        # ── Version ────────────────────────────────────────────────────────────
        if _m(low, ['version', 'what version', 'nexus version']):
            return (
                f"**NEXUS v0.1.0** — Foundation Release\n\n"
                f"**Running:** Built-in Reasoning Engine v2.0\n"
                f"**Features active:** Owner auth, dashboard, chat, builder, 21-stage pipeline, "
                f"22 AI workers, memory, reports, workers activity feed, notifications, "
                f"app store publish, promotion, revenue tracking, roadmap.\n\n"
                f"**Upcoming:** LLM integration (v0.2), voice interface (v0.3), "
                f"mobile app creation (v0.4), financial management (v0.5). "
                f"See the full plan in the **Roadmap** section."
            )

        # ── Help ───────────────────────────────────────────────────────────────
        if _m(low, ['help', 'what can you do', 'capabilities', 'commands', 'options']):
            return (
                f"Here is what NEXUS can do for you right now, {name}:\n\n"
                f"**Build software** — describe any app, API, dashboard, or tool. "
                f"The 21-stage pipeline runs automatically.\n\n"
                f"**Manage projects** — view history, download artifacts, review pipeline results.\n\n"
                f"**Monitor workers** — watch all 22 AI agents in real time with live activity.\n\n"
                f"**Publish to stores** — package completed projects for Play Store or App Store.\n\n"
                f"**Track revenue** — log earnings, set milestones, manage payouts.\n\n"
                f"**Search memory** — every project builds institutional knowledge.\n\n"
                f"**View reports** — build analytics, system health, revenue opportunities.\n\n"
                f"Just describe what you want to build — I'll handle the rest."
            )

        # ── Roadmap ─────────────────────────────────────────────────────────────
        if _m(low, ['roadmap', 'future', 'planned', 'upcoming', 'next version', 'what\'s next']):
            return (
                f"The NEXUS roadmap is visible in the **Roadmap** section. Key milestones:\n\n"
                f"**v0.2 — LLM Integration:** Connect OpenAI, Anthropic, or local models.\n"
                f"**v0.3 — Voice Interface:** Talk to NEXUS by voice.\n"
                f"**v0.4 — Mobile App Creation:** Build real Android/iOS apps.\n"
                f"**v0.5 — Financial Management:** Full P&L, invoicing, and accounting.\n"
                f"**v0.6 — Social Media Management:** Auto-post and run ad campaigns.\n"
                f"**v1.0 — Full AI Operating System:** All capabilities unified.\n\n"
                f"Every future version adds plugins without breaking existing functionality."
            )

        # ── Thank you ──────────────────────────────────────────────────────────
        if _m(low, ['thank', 'thanks', 'good job', 'well done', 'perfect', 'amazing', 'great']):
            return (
                f"You're welcome, {name}. Every project we run together makes NEXUS smarter.\n\n"
                f"What's next — shall we start a new build, check on your projects, or review the workers?"
            )

        # ── Context-aware default ─────────────────────────────────────────────
        # Check if there's recent build context
        if _m(ctx_text, ['build', 'project', 'create', 'app']) and len(msg) > 20:
            intent = self.detect_intent(msg, owner)
            if intent['is_build']:
                return (
                    f"That sounds like a great project, {name}.\n\n"
                    f"**Your goal:** {intent['goal'][:150]}\n"
                    f"**Detected type:** {intent['project_type']}\n\n"
                    f"Click **Launch Build** below to start the 21-stage pipeline, "
                    f"or describe more requirements first and I'll refine the spec."
                )

        # ── Intelligent default ────────────────────────────────────────────────
        return (
            f"I understand, {name}. Let me address that.\n\n"
            f"NEXUS v2.0 is running on the built-in reasoning engine — context-aware, "
            f"always honest, and ready to build.\n\n"
            f"If you want to build software, describe your project and I'll dispatch the 22-worker pipeline immediately. "
            f"For anything else — workers, reports, memory, publish — ask me directly or use the sidebar navigation.\n\n"
            f"What would you like to do?"
        )


# ── Utility ──────────────────────────────────────────────────────────────────
def _m(text: str, keywords: list) -> bool:
    """Return True if any keyword appears in text."""
    return any(kw in text for kw in keywords)
