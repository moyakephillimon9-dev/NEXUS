"""
NEXUS Brain — Built-in Reasoning Engine
Provides chat, worker info, and streaming responses.
No external API required; optionally enhanced by LLM providers.
"""

import json, re, time, datetime, random
from pathlib import Path

DATA_DIR    = Path(__file__).resolve().parent.parent / 'data'
CHAT_FILE   = DATA_DIR / 'chat_history.json'
MEMORY_FILE = Path(__file__).resolve().parent.parent / 'memory' / 'database.json'


# ── Worker registry ────────────────────────────────────────────────────────────
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


class NexusBrain:
    """Built-in NEXUS reasoning engine with streaming chat support."""

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
        # Keep last 200 messages
        if len(history) > 200:
            history = history[-200:]
        with open(CHAT_FILE, 'w') as f:
            json.dump(history, f, indent=2)

    def clear_chat_history(self):
        with open(CHAT_FILE, 'w') as f:
            json.dump([], f)

    # ── Core response engine ──────────────────────────────────────────────────
    def respond(self, message: str, owner: dict) -> str:
        """Return a full response string."""
        return ''.join(self.stream_response(message, owner))

    def stream_response(self, message: str, owner: dict):
        """Yield response tokens one word at a time for streaming."""
        text = self._build_response(message, owner)
        words = text.split(' ')
        for i, word in enumerate(words):
            yield word + ('' if i == len(words) - 1 else ' ')
            time.sleep(0.018)

    def _build_response(self, message: str, owner: dict) -> str:
        """Pattern-match the message and return an appropriate response."""
        msg   = message.lower().strip()
        name  = owner.get('full_name', 'Founder').split()[0]
        company = owner.get('company', 'your company')
        now   = datetime.datetime.now()

        # ── Greetings ──
        if _match(msg, ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            hour = now.hour
            if hour < 12:    greeting = "Good morning"
            elif hour < 17:  greeting = "Good afternoon"
            else:            greeting = "Good evening"
            return (f"{greeting}, {name}. I'm NEXUS — your AI Operating System. "
                    f"I'm online and all 22 workers are standing by. "
                    f"What would you like to build or manage today?")

        # ── Identity ──
        if _match(msg, ['who are you', 'what are you', 'what is nexus', 'tell me about yourself']):
            return (f"I am NEXUS — an AI Operating System built for {company}. "
                    f"I orchestrate a team of 22 specialised AI workers across a 21-stage pipeline "
                    f"to plan, design, code, review, test, secure, document and deploy software. "
                    f"I am your private digital operations centre. "
                    f"I never fake results, never make decisions without your approval, and I grow smarter with every project.")

        # ── Status ──
        if _match(msg, ['status', 'how are you', 'are you online', 'system status']):
            return (f"All systems operational, {name}. "
                    f"22 AI workers are online. Memory is active. Pipeline is ready. "
                    f"Current time: {now.strftime('%H:%M on %A, %d %B %Y')}. "
                    f"What shall we build?")

        # ── Workers ──
        if _match(msg, ['workers', 'agents', 'team', 'who works for you', 'list workers']):
            names = ', '.join(w['name'] for w in WORKERS[:6])
            return (f"I coordinate 22 AI workers across 21 pipeline stages. "
                    f"The team includes: {names}, and 16 more specialists. "
                    f"Each worker has a dedicated role — from parsing your goal all the way to deployment and memory. "
                    f"You can view all workers in the AI Workers section.")

        # ── Build / create ──
        if _match(msg, ['build', 'create', 'make', 'develop', 'generate']):
            return (f"Ready to build, {name}. Head to the Builder section and describe what you want — "
                    f"a web app, mobile app, API, dashboard, game, or business system. "
                    f"NEXUS will activate the full 21-stage pipeline: research, plan, architect, code, test, secure, document and deploy. "
                    f"What type of software are you building?")

        # ── Projects ──
        if _match(msg, ['projects', 'my projects', 'show projects', 'project history']):
            return (f"Your projects are stored in the Projects section. "
                    f"Each project record contains the full pipeline output: source code, architecture, documentation, security report and deployment artefacts. "
                    f"Would you like to start a new project or review an existing one?")

        # ── Memory ──
        if _match(msg, ['memory', 'remember', 'what do you know', 'knowledge']):
            return (f"My memory system stores everything NEXUS learns: "
                    f"project architectures, solved problems, your preferences, business information, and pipeline outcomes. "
                    f"This knowledge grows with every project and helps me work faster and smarter over time. "
                    f"You can browse and search memories in the Memory section.")

        # ── Pipeline ──
        if _match(msg, ['pipeline', 'stages', 'process', 'how does it work']):
            return (f"The NEXUS pipeline has 21 stages: "
                    f"Vision Parsing → Capability Assessment → Research → Module Detection → Planning → Architecture → "
                    f"Database Design → Coding → UI Design → Code Review → Testing → Security → Performance → "
                    f"Documentation → Monitoring → Integration → DevOps → Deployment → Verification → Progress Tracking → Memory. "
                    f"Every stage must complete before the next begins. Verification (stage 18) blocks false success claims. "
                    f"What would you like to pipeline?")

        # ── Settings ──
        if _match(msg, ['settings', 'configure', 'configuration', 'setup']):
            return (f"You can configure NEXUS in the Settings section: "
                    f"AI provider (built-in, OpenRouter, Ollama, LM Studio), memory, security, theme and more. "
                    f"By default I use the built-in reasoning engine — no API key required. "
                    f"Would you like to enable an external LLM provider?")

        # ── Reports ──
        if _match(msg, ['report', 'reports', 'analytics', 'statistics', 'stats']):
            return (f"The Reports section shows daily, weekly and monthly summaries of your NEXUS activity: "
                    f"projects built, pipeline success rates, worker performance and system health. "
                    f"All reports are generated automatically. Check the Reports section for the latest data.")

        # ── Version ──
        if _match(msg, ['version', 'what version', 'nexus version']):
            return ("NEXUS v0.1.0 — Foundation Release.\n"
                    "This version delivers: owner authentication, dashboard, chat, project builder, "
                    "21-stage pipeline, worker management, memory, reports, settings and roadmap. "
                    "Future versions will add LLM integration, voice, mobile apps, financial management, "
                    "social media management, and more. Check the Roadmap for the full plan.")

        # ── Help ──
        if _match(msg, ['help', 'what can you do', 'capabilities', 'commands']):
            return (f"Here is what I can do for you right now, {name}:\n\n"
                    f"🔨 **Build software** — describe any app and the 21-stage pipeline runs automatically.\n"
                    f"📂 **Manage projects** — view history, artifacts, and pipeline results.\n"
                    f"🤖 **Monitor workers** — see the status and logs of all 22 AI workers.\n"
                    f"🧠 **Search memory** — I remember every project and solution.\n"
                    f"📊 **View reports** — daily and weekly activity summaries.\n"
                    f"⚙️ **Configure settings** — AI provider, security, and preferences.\n"
                    f"🗺️ **Roadmap** — see planned features and future milestones.\n\n"
                    f"Just ask me anything or use the menu on the left.")

        # ── Roadmap / future ──
        if _match(msg, ['roadmap', 'future', 'planned', 'upcoming', 'next version']):
            return ("The NEXUS roadmap is visible in the Roadmap section. "
                    "Planned milestones include: LLM integration (v0.2), voice interface (v0.3), "
                    "mobile app creation (v0.4), financial management (v0.5), social media management (v0.6), "
                    "and the full AI Operating System vision (v1.0). "
                    "All future capabilities will be added as plugins without breaking existing functionality.")

        # ── Thank you ──
        if _match(msg, ['thank', 'thanks', 'good job', 'well done', 'perfect']):
            return (f"You're welcome, {name}. NEXUS exists to multiply your capabilities. "
                    f"Every project we complete together makes the system smarter. What's next?")

        # ── Default ──
        return (f"Understood, {name}. I'm processing your request: \"{message}\"\n\n"
                f"As NEXUS v0.1.0, I'm running on the built-in reasoning engine. "
                f"For richer responses, you can connect an external LLM provider in Settings. "
                f"Currently I can help you build software, manage projects, monitor workers, "
                f"search memory, and view reports. "
                f"What would you like to do?")


# ── Utility ───────────────────────────────────────────────────────────────────
def _match(text: str, keywords: list) -> bool:
    return any(kw in text for kw in keywords)
