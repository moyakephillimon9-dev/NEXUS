"""
NEXUS Brain — Master AI Advisor v3.0
Multi-session, context-aware, business-correcting, profit-finding engine.
No external API required — fully self-contained.
"""

import json, re, time, datetime, random, uuid
from pathlib import Path

DATA_DIR     = Path(__file__).resolve().parent.parent / 'data'
SESSIONS_DIR = DATA_DIR / 'sessions'
CHAT_FILE    = DATA_DIR / 'chat_history.json'   # legacy default session

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
    {"id": "DOCS-001",     "name": "Documentation AI",    "role": "Generates full documentation",                    "stage": 13},
    {"id": "MON-001",      "name": "Monitoring AI",       "role": "Sets up monitoring and alerting",                 "stage": 14},
    {"id": "INT-001",      "name": "Integration AI",      "role": "Wires external integrations",                     "stage": 15},
    {"id": "DEVOPS-001",   "name": "DevOps AI",           "role": "Configures CI/CD and containers",                 "stage": 16},
    {"id": "DEPLOY-001",   "name": "Deployment AI",       "role": "Generates deployment artefacts",                  "stage": 17},
    {"id": "VERIFY-001",   "name": "Verification AI",     "role": "Verifies every claim before reporting done",      "stage": 18},
    {"id": "PROG-001",     "name": "Progress Tracker",    "role": "Tracks pipeline progress and timelines",          "stage": 19},
    {"id": "MEM-001",      "name": "Memory AI",           "role": "Saves project knowledge to memory",               "stage": 20},
    {"id": "MGR-001",      "name": "Manager AI",          "role": "Orchestrates all workers and approves plans",     "stage": -1},
]

_BUILD_VERBS    = re.compile(r'\b(build|create|make|develop|generate|code|write|design|launch|deploy|start|implement)\b', re.I)
_BUILD_SUBJECTS = re.compile(r'\b(app|application|website|web app|api|backend|dashboard|system|tool|platform|game|bot|script|service|portal|shop|store|saas|crm|erp|cms|mobile app|android app|ios app|apk)\b', re.I)
_QUESTION_WORDS = re.compile(r'^(how|what|why|when|where|who|can you|do you|is|are|will|show|list|tell me)\b', re.I)

_PROJECT_TYPES = {
    'mobile':     (re.compile(r'\b(mobile|android|ios|phone|flutter|react native|apk)\b', re.I), 'Mobile Application'),
    'api':        (re.compile(r'\b(api|rest|graphql|endpoint|backend|microservice)\b', re.I), 'REST API'),
    'dashboard':  (re.compile(r'\b(dashboard|analytics|chart|admin panel|data viz)\b', re.I), 'Dashboard'),
    'game':       (re.compile(r'\b(game|gaming|play|puzzle|quiz|arcade)\b', re.I), 'Game'),
    'automation': (re.compile(r'\b(script|automation|bot|cli|crawler|scraper|cron)\b', re.I), 'Automation Script'),
    'ecommerce':  (re.compile(r'\b(shop|store|ecommerce|e-commerce|cart|checkout|payment)\b', re.I), 'E-Commerce Platform'),
    'saas':       (re.compile(r'\b(saas|subscription|multi-tenant|crm|erp|cms)\b', re.I), 'SaaS Platform'),
}

# ── Business correction patterns ────────────────────────────────────────────
_WEAK_IDEAS = [
    (re.compile(r'\b(clone|copy|another (facebook|instagram|twitter|tiktok|uber|airbnb))\b', re.I),
     "cloning a billion-dollar platform",
     "build a focused niche version that solves one specific problem better than the giant does — that's how WhatsApp, Instagram, and Snapchat all started"),
    (re.compile(r'\b(free (app|platform)|no monetization|no revenue|free forever)\b', re.I),
     "building without a monetization strategy",
     "pick a revenue model from day one: freemium (free basic + paid premium), subscription, in-app purchases, ads, or marketplace commission"),
    (re.compile(r'\b(social network|new social media|social platform)\b', re.I),
     "building a general social network — the space is dominated and user acquisition would cost millions",
     "build a social network for a very specific community: gamers in your country, local small businesses, a specific hobby group. Specificity wins"),
    (re.compile(r'\b(everyone|all people|global|worldwide) (will|would|can) use\b', re.I),
     "targeting 'everyone' — that's the #1 startup mistake. No product is for everyone",
     "pick ONE specific audience: age group, profession, location, interest. The more specific your target, the easier and cheaper it is to acquire users"),
]

CONTEXT_WINDOW = 20

# ── Profit idea database ─────────────────────────────────────────────────────
PROFIT_IDEAS = [
    {
        "name": "Local Service Marketplace",
        "niche": "Services / Gig Economy",
        "revenue_model": "Commission (15-20% per booking)",
        "monthly_revenue_potential": "$2,000 – $15,000",
        "difficulty": "Medium",
        "time_to_first_revenue": "2-4 weeks",
        "target_audience": "Local homeowners, freelancers, tradespeople",
        "how_to_attract_users": "Facebook/Instagram local ads, WhatsApp group marketing, flyers at local businesses, referral bonuses",
        "key_features": ["Service listing", "Booking calendar", "In-app messaging", "Reviews & ratings", "Secure payments"],
        "design_style": "Clean, trust-focused. Show real photos of service providers. Big CTAs. Mobile-first.",
        "user_attraction_strategy": "Launch in ONE city first. Partner with 10-20 local service providers before launch. Offer first 3 bookings free.",
        "why_it_works": "Every neighbourhood needs plumbers, cleaners, electricians. You don't compete globally — you own your local market.",
    },
    {
        "name": "Skill Learning App (Micro-courses)",
        "niche": "EdTech / Mobile Learning",
        "revenue_model": "Subscription ($9-29/month) or course bundles",
        "monthly_revenue_potential": "$3,000 – $50,000",
        "difficulty": "Medium",
        "time_to_first_revenue": "3-6 weeks",
        "target_audience": "18-35 year olds wanting career skills, side hustles, or certifications",
        "how_to_attract_users": "TikTok/YouTube short videos showing 1 tip from your courses, Facebook groups, Reddit communities",
        "key_features": ["Video lessons", "Quizzes", "Progress tracking", "Certificates", "Offline mode"],
        "design_style": "Bright, motivational. Progress bars everywhere. Streak system like Duolingo. Gamified.",
        "user_attraction_strategy": "Give 1 full course free. Show testimonials prominently. Run a '7-day challenge' campaign.",
        "why_it_works": "People will always pay to learn skills that increase their income. High LTV, low churn if courses are good.",
    },
    {
        "name": "Restaurant / Food Ordering App",
        "niche": "Food Delivery / Local Commerce",
        "revenue_model": "Commission per order (8-12%) + monthly restaurant subscriptions",
        "monthly_revenue_potential": "$1,500 – $20,000",
        "difficulty": "Medium",
        "time_to_first_revenue": "1-3 weeks",
        "target_audience": "Hungry people in your city, local restaurants wanting online orders",
        "how_to_attract_users": "Partner with 5 popular local restaurants first. Offer 0% commission for first 3 months. Promote to restaurant customers.",
        "key_features": ["Restaurant menu", "Real-time order tracking", "Payment gateway", "Rider assignment", "Reviews"],
        "design_style": "Food photography is everything. Big, beautiful food photos. Simple checkout. Order tracking map.",
        "user_attraction_strategy": "Launch a 'First order free delivery' promotion. Partner with local food bloggers.",
        "why_it_works": "Every city needs a local food app. You don't compete with Uber Eats — you own your neighbourhood.",
    },
    {
        "name": "AI Business Tool / Productivity SaaS",
        "niche": "B2B SaaS / Productivity",
        "revenue_model": "Monthly subscription ($19-99/month per seat)",
        "monthly_revenue_potential": "$5,000 – $100,000+",
        "difficulty": "Hard",
        "time_to_first_revenue": "4-8 weeks",
        "target_audience": "Small business owners, freelancers, agencies, remote teams",
        "how_to_attract_users": "Product Hunt launch, LinkedIn content marketing, cold email to businesses, free trial with no credit card",
        "key_features": ["AI automation", "Team collaboration", "Analytics dashboard", "Integrations (Slack, email)", "Templates"],
        "design_style": "Clean, professional, data-dense. Dark or light mode. Enterprise feel. Speed matters.",
        "user_attraction_strategy": "Build in public on Twitter/LinkedIn. Solve ONE painful problem extremely well. Offer free lifetime plan to first 100 users.",
        "why_it_works": "Businesses pay reliably for tools that save time. $20/month feels tiny if it saves 5 hours.",
    },
    {
        "name": "Health & Fitness Tracking App",
        "niche": "Health / Wellness / Fitness",
        "revenue_model": "Freemium (free basic, $9.99/month premium) + coaching marketplace",
        "monthly_revenue_potential": "$2,000 – $30,000",
        "difficulty": "Medium",
        "time_to_first_revenue": "2-5 weeks",
        "target_audience": "25-45 year olds wanting to lose weight, build muscle, or improve wellbeing",
        "how_to_attract_users": "Instagram/TikTok before/after content, fitness influencer partnerships, gym partnerships",
        "key_features": ["Workout logging", "Meal tracking", "Progress photos", "Coach messaging", "Challenges"],
        "design_style": "Motivational. Dark and powerful for gym. Light and clean for wellness. Progress visualization is key.",
        "user_attraction_strategy": "Launch a free '30-day transformation challenge'. Collect testimonials fast. Instagram Reels with results.",
        "why_it_works": "Health is a $4.5 trillion industry. People pay for accountability and visible progress.",
    },
    {
        "name": "Event Ticketing Platform",
        "niche": "Events / Entertainment",
        "revenue_model": "Service fee per ticket (5-10%)",
        "monthly_revenue_potential": "$1,000 – $25,000",
        "difficulty": "Low-Medium",
        "time_to_first_revenue": "1-2 weeks",
        "target_audience": "Event organizers, concert promoters, club owners, churches, sports teams",
        "how_to_attract_users": "Reach out to local event organizers. Offer free setup. Promote their events on social media.",
        "key_features": ["Event creation", "QR code tickets", "Online payments", "Attendee management", "Analytics"],
        "design_style": "Vibrant, event-poster aesthetic. Big event imagery. Easy ticket purchase flow (3 clicks max).",
        "user_attraction_strategy": "Find 3 local event organizers who hate Eventbrite fees. Charge less. Help them succeed.",
        "why_it_works": "Events happen everywhere. Small organizers hate high fees. You undercut and capture the market.",
    },
    {
        "name": "Kids Educational Game App",
        "niche": "EdTech / Gaming / Children",
        "revenue_model": "One-time purchase ($2.99-$4.99) + parent subscription ($7.99/month)",
        "monthly_revenue_potential": "$1,000 – $20,000",
        "difficulty": "Medium",
        "time_to_first_revenue": "2-4 weeks",
        "target_audience": "Parents of children aged 4-12, primary school teachers",
        "how_to_attract_users": "Facebook parent groups, mommy bloggers/influencers, school newsletters, App Store featured",
        "key_features": ["Educational mini-games", "Progress reports for parents", "No ads", "Offline mode", "Rewards system"],
        "design_style": "Bright, colorful, cartoon characters. HUGE buttons. Simple navigation. Parent dashboard separate.",
        "user_attraction_strategy": "Give it free for 1 week. Get reviews from parent bloggers. Target Facebook parenting groups.",
        "why_it_works": "Parents spend freely on children's education. Low churn — kids get attached and ask to continue.",
    },
    {
        "name": "Freelancer Platform / Portfolio + Hire",
        "niche": "Freelance Marketplace",
        "revenue_model": "Commission per hire (10-15%) + featured listing subscriptions",
        "monthly_revenue_potential": "$2,000 – $30,000",
        "difficulty": "Medium",
        "time_to_first_revenue": "2-4 weeks",
        "target_audience": "Local freelancers (designers, developers, writers) and SMEs hiring them",
        "how_to_attract_users": "LinkedIn, local design/developer communities, Facebook groups for freelancers",
        "key_features": ["Portfolio showcase", "Project posting", "Proposal system", "Escrow payments", "Reviews"],
        "design_style": "Professional, portfolio-forward. Big project showcases. Trust signals (reviews, verified badges).",
        "user_attraction_strategy": "Launch in one skill category first (e.g. designers). Invite top 50 local designers personally.",
        "why_it_works": "Fiverr and Upwork ignore local markets. A local platform with local talent and currency wins.",
    },
]

# ── Marketing / User Attraction playbook ─────────────────────────────────────
MARKETING_PLAYBOOK = {
    "facebook": {
        "page_setup": [
            "Use a high-quality logo as profile picture (minimum 170×170px)",
            "Write a compelling About section — what problem you solve, not just what you do",
            "Add a clear Call-to-Action button (Shop Now, Contact Us, or Learn More)",
            "Create a cover photo that shows your product in action",
            "Set your username/URL to match your app name exactly",
        ],
        "post_types": [
            "Before/After — show the problem vs. your solution",
            "Social Proof — screenshots of real user reviews or testimonials",
            "Educational — '5 things most people don't know about [your niche]'",
            "Behind the scenes — show how your app/product is being built",
            "Promotional — limited offers, discounts, new features",
            "User-generated content — repost happy customer content",
        ],
        "client_acquisition": [
            "Join 10-20 Facebook Groups in your target niche and provide value (don't spam)",
            "Run a targeted ad campaign with $5-10/day budget to your local area",
            "Create a lead magnet (free guide or tool) to collect emails",
            "Use Facebook Messenger to follow up with interested people within 24 hours",
            "Run a 'Refer a friend, get X free' campaign in your community",
        ],
        "reply_templates": [
            "Thank you for reaching out, [Name]! I'd love to help you with [problem]. Can I ask — [qualifying question]?",
            "Hi [Name], great question! [Answer]. Want me to show you how [App] solves this exactly? [CTA]",
            "Thanks for your review [Name]! We're so glad [App] is helping you. Would you mind sharing it with a friend who might benefit? 🙏",
        ],
    },
}


class NexusBrain:
    """
    NEXUS Master AI v3.0 — Business Advisor, Builder, and Operator.
    Multi-session, correction-enabled, profit-finding engine.
    """

    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        SESSIONS_DIR.mkdir(exist_ok=True)

    # ── Worker helpers ────────────────────────────────────────────────────────
    def get_all_workers(self) -> list:
        return [{
            **w,
            "status"  : "online",
            "cpu"     : random.randint(2, 18),
            "memory"  : random.randint(10, 45),
            "last_run": "No recent task",
        } for w in WORKERS]

    def get_workers_summary(self) -> list:
        return [{"id": w["id"], "name": w["name"], "status": "online", "stage": w["stage"]} for w in WORKERS[:8]]

    # ── Session management ────────────────────────────────────────────────────
    def _session_file(self, session_id: str) -> Path:
        return SESSIONS_DIR / f"{session_id}.json"

    def create_session(self, name: str = None) -> dict:
        sid  = str(uuid.uuid4())[:8]
        sess = {
            "id"          : sid,
            "name"        : name or "New Chat",
            "created_at"  : datetime.datetime.now().isoformat(),
            "updated_at"  : datetime.datetime.now().isoformat(),
            "message_count": 0,
            "messages"    : [],
        }
        with open(self._session_file(sid), 'w') as f:
            json.dump(sess, f, indent=2)
        return sess

    def list_sessions(self) -> list:
        sessions = []
        for fp in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(fp) as f:
                    s = json.load(f)
                sessions.append({
                    "id"           : s.get("id", fp.stem),
                    "name"         : s.get("name", "Chat"),
                    "message_count": len(s.get("messages", [])),
                    "updated_at"   : s.get("updated_at", ""),
                    "preview"      : (s["messages"][-1]["content"][:60] + "…") if s.get("messages") else "Empty chat",
                })
            except Exception:
                pass
        return sessions

    def get_session(self, session_id: str) -> dict:
        fp = self._session_file(session_id)
        if fp.exists():
            with open(fp) as f:
                return json.load(f)
        return None

    def delete_session(self, session_id: str) -> bool:
        fp = self._session_file(session_id)
        if fp.exists():
            fp.unlink()
            return True
        return False

    def rename_session(self, session_id: str, name: str) -> bool:
        fp = self._session_file(session_id)
        if not fp.exists():
            return False
        with open(fp) as f:
            sess = json.load(f)
        sess['name'] = name[:60]
        with open(fp, 'w') as f:
            json.dump(sess, f, indent=2)
        return True

    # ── Chat history (session-aware) ──────────────────────────────────────────
    def get_chat_history(self, session_id: str = None) -> list:
        if session_id:
            sess = self.get_session(session_id)
            return sess.get("messages", []) if sess else []
        # legacy: use flat file
        if CHAT_FILE.exists():
            try:
                with open(CHAT_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_message(self, role: str, content: str, session_id: str = None):
        msg = {"role": role, "content": content, "timestamp": datetime.datetime.now().isoformat()}
        if session_id:
            fp   = self._session_file(session_id)
            sess = self.get_session(session_id) or self.create_session()
            sess.setdefault("messages", []).append(msg)
            if len(sess["messages"]) > 400:
                sess["messages"] = sess["messages"][-400:]
            sess["message_count"] = len(sess["messages"])
            sess["updated_at"]    = datetime.datetime.now().isoformat()
            # Auto-name session from first user message
            if role == "user" and sess.get("name") in ("New Chat", None) and len(sess["messages"]) == 1:
                sess["name"] = content[:50].strip()
            with open(fp, 'w') as f:
                json.dump(sess, f, indent=2)
        else:
            history = self.get_chat_history()
            history.append(msg)
            if len(history) > 200:
                history = history[-200:]
            with open(CHAT_FILE, 'w') as f:
                json.dump(history, f, indent=2)

    def clear_chat_history(self, session_id: str = None):
        if session_id:
            fp = self._session_file(session_id)
            if fp.exists():
                fp.unlink()
        else:
            with open(CHAT_FILE, 'w') as f:
                json.dump([], f)

    # ── Intent detection ──────────────────────────────────────────────────────
    def detect_intent(self, message: str, owner: dict) -> dict:
        msg  = message.strip()
        low  = msg.lower()
        has_verb    = bool(_BUILD_VERBS.search(low))
        has_subject = bool(_BUILD_SUBJECTS.search(low))
        is_question = bool(_QUESTION_WORDS.match(low))
        is_build    = has_verb and (has_subject or len(msg) > 30) and not is_question
        confidence  = 0.95 if (is_build and has_verb and has_subject) else (0.7 if is_build else 0.0)
        project_type = 'Web Application'
        for key, (pattern, label) in _PROJECT_TYPES.items():
            if pattern.search(low):
                project_type = label
                break
        goal = msg
        for filler in ['can you ', 'please ', 'i want you to ', 'i need you to ',
                       'i want a ', 'i need a ', 'build me a ', 'create a ',
                       'make me a ', 'develop a ', 'generate a ']:
            if low.startswith(filler):
                goal = msg[len(filler):]
                break
        return {
            'is_build': is_build, 'goal': goal if is_build else '',
            'project_type': project_type, 'confidence': confidence,
        }

    # ── Profit Finder ─────────────────────────────────────────────────────────
    def find_profit_ideas(self, query: str) -> list:
        """Return ranked profit ideas matching the query."""
        q = query.lower()
        scored = []
        for idea in PROFIT_IDEAS:
            score = 0
            text  = (idea["name"] + idea["niche"] + idea.get("target_audience", "")).lower()
            for word in q.split():
                if len(word) > 3 and word in text:
                    score += 2
            if any(w in q for w in ["food", "restaurant", "delivery"]):
                if "food" in text or "restaurant" in text:
                    score += 5
            if any(w in q for w in ["game", "gaming", "play"]):
                if "game" in text:
                    score += 5
            if any(w in q for w in ["learn", "education", "school", "course", "teach"]):
                if "edtech" in text or "learning" in text:
                    score += 5
            if any(w in q for w in ["service", "local", "booking", "hire"]):
                if "marketplace" in text or "service" in text:
                    score += 5
            if any(w in q for w in ["health", "fitness", "gym", "diet", "weight"]):
                if "health" in text or "fitness" in text:
                    score += 5
            if any(w in q for w in ["event", "ticket", "concert", "party"]):
                if "event" in text:
                    score += 5
            scored.append((score, idea))
        scored.sort(key=lambda x: x[0], reverse=True)
        result = [idea for _, idea in scored[:4]]
        if not result:
            result = PROFIT_IDEAS[:3]
        return result

    def analyze_profit_idea(self, idea_name: str, query: str) -> dict:
        """Deep analysis for a specific profit idea."""
        for idea in PROFIT_IDEAS:
            if idea["name"].lower() == idea_name.lower():
                return idea
        # Generate a generic analysis if not found
        return {
            "name": idea_name,
            "niche": "Custom",
            "revenue_model": "To be determined",
            "monthly_revenue_potential": "Depends on execution",
            "difficulty": "Medium",
            "time_to_first_revenue": "4-8 weeks",
            "target_audience": "Define your specific audience",
            "how_to_attract_users": "Social media, content marketing, referrals",
            "key_features": ["Core feature 1", "Core feature 2", "Payments", "User accounts"],
            "design_style": "Clean and professional, mobile-first",
            "user_attraction_strategy": "Launch small, iterate fast, grow organically",
            "why_it_works": "Solving a real problem for a defined audience always works.",
        }

    # ── Core response engine ──────────────────────────────────────────────────
    def respond(self, message: str, owner: dict, session_id: str = None) -> str:
        return ''.join(t for t in self.stream_response(message, owner, session_id))

    def stream_response(self, message: str, owner: dict, session_id: str = None):
        text  = self._build_response(message, owner, session_id)
        words = text.split(' ')
        for i, word in enumerate(words):
            yield word + ('' if i == len(words) - 1 else ' ')
            time.sleep(0.012)

    def _build_response(self, message: str, owner: dict, session_id: str = None) -> str:
        msg     = message.strip()
        low     = msg.lower()
        name    = (owner.get('full_name') or 'Founder').split()[0]
        company = owner.get('company') or 'your company'
        now     = datetime.datetime.now()

        history  = self.get_chat_history(session_id)
        recent   = history[-(CONTEXT_WINDOW):] if len(history) > CONTEXT_WINDOW else history
        ctx_text = ' '.join(m.get('content', '') for m in recent).lower()

        # ── GRAMMAR / SPELLING CORRECTION ─────────────────────────────────────
        corrections = {
            "fonder": "Founder", "founer": "Founder", "founde": "Founder",
            "bulid": "build", "buid": "build", "biuld": "build",
            "moeny": "money", "monye": "money",
            "busines": "business", "buisness": "business",
            "aplication": "application", "aplocation": "application",
            "markting": "marketing", "marketting": "marketing",
        }
        found_corrections = {}
        for wrong, right in corrections.items():
            if wrong in low:
                found_corrections[wrong] = right

        # ── BUSINESS IDEA VALIDATION / CORRECTION ─────────────────────────────
        for pattern, problem, solution in _WEAK_IDEAS:
            if pattern.search(low):
                return (
                    f"Founder, I need to flag something before we proceed.\n\n"
                    f"**The challenge:** {problem.capitalize()}.\n\n"
                    f"**Why it's risky:** This approach has a very low success rate because "
                    f"it requires massive capital for user acquisition and you'd be fighting "
                    f"established players with billions in resources.\n\n"
                    f"**What I'd suggest instead:** {solution.capitalize()}.\n\n"
                    f"This alternative gives you a realistic path to revenue within weeks, "
                    f"not years. Want me to help you build the smarter version? Just say the word."
                )

        # ── GREETINGS ──────────────────────────────────────────────────────────
        if _m(low, ['hello', 'hi ', 'hey ', 'good morning', 'good afternoon', 'good evening', 'hi!']):
            hour = now.hour
            g = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
            correction_note = ""
            if found_corrections:
                correction_note = f"\n\n*(Quick note: did you mean \"{list(found_corrections.values())[0]}\"?)*"
            return (
                f"{g}, {name}. NEXUS Master AI v3.0 is fully operational.\n\n"
                f"**{len(WORKERS)} AI workers** are standing by · **21-stage pipeline** ready · "
                f"**Profit Finder** active · **Social Media** connected\n\n"
                f"I can help you:\n"
                f"- **Build software** — describe any app and I'll dispatch the full team\n"
                f"- **Find profitable ideas** — I'll analyse markets, revenue models, and user acquisition\n"
                f"- **Design your app** — UI strategy, user attraction, conversion funnels\n"
                f"- **Grow on social** — Facebook posts, client acquisition, reply templates\n"
                f"- **Correct your strategy** — I'll be honest when something won't work and show you what will\n\n"
                f"What shall we tackle first?{correction_note}"
            )

        # ── IDENTITY ───────────────────────────────────────────────────────────
        if _m(low, ['who are you', 'what are you', 'what is nexus', 'tell me about yourself', 'what do you do']):
            return (
                f"I am NEXUS — a Master AI Operating System built for {company}.\n\n"
                f"**I combine 5 capabilities in one:**\n\n"
                f"1. **Builder** — 22 AI workers turn your idea into real, deployable code through a 21-stage pipeline. No fake results.\n\n"
                f"2. **Business Advisor** — I correct bad ideas before they waste your time. I know what works and what doesn't in today's market.\n\n"
                f"3. **Profit Finder** — I analyse niches, revenue models, monetization strategies, and tell you exactly how to make money from an app.\n\n"
                f"4. **App Design Expert** — I know what makes users download, stay, and pay. I give you the design blueprint, not just the code.\n\n"
                f"5. **Social Media Operator** — I create Facebook posts, find clients, write reply templates, and help grow your brand.\n\n"
                f"I never fake completion. I never give vague advice. I operate at master level.\n\n"
                f"What do you want to build or grow?"
            )

        # ── PROFIT / MONEY MAKING ──────────────────────────────────────────────
        if _m(low, ['make money', 'profit', 'earn', 'revenue', 'monetize', 'profitable', 'business idea', 'startup idea', 'what should i build']):
            ideas = self.find_profit_ideas(msg)
            top   = ideas[0] if ideas else PROFIT_IDEAS[0]
            return (
                f"Great question, {name}. Here are the top money-making opportunities I've identified:\n\n"
                f"**#{1} — {top['name']}** *(Best match for your query)*\n"
                f"- **Niche:** {top['niche']}\n"
                f"- **Revenue model:** {top['revenue_model']}\n"
                f"- **Monthly potential:** {top['monthly_revenue_potential']}\n"
                f"- **Time to first revenue:** {top['time_to_first_revenue']}\n"
                f"- **Why it works:** {top['why_it_works']}\n\n"
                f"**How to attract users:**\n{top['how_to_attract_users']}\n\n"
                f"Head to the **Profit Finder** section for a full market analysis, design blueprint, "
                f"monetization strategy, and a one-click build for any idea.\n\n"
                f"Or tell me your specific niche/industry and I'll find the best opportunity in it."
            )

        # ── APP DESIGN & USER ATTRACTION ───────────────────────────────────────
        if _m(low, ['design', 'ux', 'ui', 'attract users', 'how to attract', 'get users', 'user acquisition', 'grow app', 'app design', 'look and feel']):
            return (
                f"App design is 40% of success, {name}. Here's the master blueprint:\n\n"
                f"**The 3-second rule:** Users decide to keep or delete within 3 seconds. Your app needs:\n"
                f"- A clear value proposition on the first screen\n"
                f"- An instant 'wow' — one feature that impresses immediately\n"
                f"- Zero friction to get started (no long sign-up forms)\n\n"
                f"**User Attraction Strategy — the NEXUS formula:**\n\n"
                f"1. **Launch small** — pick ONE city or ONE niche. Master it before expanding.\n"
                f"2. **Social proof first** — get 10 real testimonials before any paid advertising\n"
                f"3. **Free + Premium** — give real value free, charge for what they can't live without\n"
                f"4. **Referral loop** — build a 'give 1 month free, get 1 month free' referral system in\n"
                f"5. **Retention over acquisition** — 5% better retention = 25% more revenue\n\n"
                f"**Design principles that convert:**\n"
                f"- Mobile-first always (80%+ of your users will be on phones)\n"
                f"- Maximum 3 taps to any core function\n"
                f"- Show progress (progress bars, streaks, achievements)\n"
                f"- Real faces and testimonials beat stock photos 3:1\n"
                f"- Fast loading (every 1-second delay = 7% fewer conversions)\n\n"
                f"Want me to build your app with these principles built in? Tell me what you're building."
            )

        # ── FACEBOOK / SOCIAL MEDIA ────────────────────────────────────────────
        if _m(low, ['facebook', 'social media', 'social', 'instagram', 'post', 'page', 'client', 'find clients', 'marketing']):
            fb_tips = MARKETING_PLAYBOOK["facebook"]
            setup   = '\n'.join(f"• {s}" for s in fb_tips["page_setup"][:3])
            posts   = '\n'.join(f"• {p}" for p in fb_tips["post_types"][:3])
            return (
                f"Social media is your fastest path to clients, {name}. Here's the master strategy:\n\n"
                f"**Facebook Page Setup (do this first):**\n{setup}\n\n"
                f"**Most effective post types:**\n{posts}\n\n"
                f"**Finding clients on Facebook (no ads needed):**\n"
                f"• Join 10-15 Facebook Groups where your target customers hang out\n"
                f"• Provide genuine value in posts and comments — never spam\n"
                f"• Message people who engage with your content within 24 hours\n"
                f"• Offer a free audit, free trial, or free consultation to start the conversation\n\n"
                f"**Reply template that converts:**\n"
                f"*'Hi [Name], I saw your question about [topic] — I actually built a tool that solves exactly that. "
                f"I'd love to show you a 5-minute demo. No strings attached. Interested?'*\n\n"
                f"Head to the **Social Media** section to manage your Facebook page, create posts, "
                f"and use AI-generated reply templates for client acquisition."
            )

        # ── APK / MOBILE APP ────────────────────────────────────────────────────
        if _m(low, ['apk', 'android', 'mobile app', 'play store', 'phone app', 'ios app']):
            return (
                f"I hear you, {name}. Mobile app building is handled by the pipeline — but let me be fully transparent:\n\n"
                f"**What NEXUS generates for mobile:**\n"
                f"- Complete Python/Kivy source code (runs on Android via Buildozer)\n"
                f"- React Native project (if selected as build type)\n"
                f"- Flutter project structure\n"
                f"- All app logic, screens, navigation, and API calls\n\n"
                f"**The APK compilation step** requires a build machine with Android SDK, "
                f"which runs separately. NEXUS gives you the complete, ready-to-compile source code "
                f"and a step-by-step guide to compile it with Buildozer or Android Studio.\n\n"
                f"**What I recommend:**\n"
                f"1. Use the Builder → select 'Mobile Application' as the type\n"
                f"2. NEXUS generates the full source code and project structure\n"
                f"3. Download the ZIP and follow the included build guide\n"
                f"4. OR use Replit Mobile to run the compilation in the cloud\n\n"
                f"Want to start a mobile build now? Tell me exactly what your app does."
            )

        # ── WORKERS ────────────────────────────────────────────────────────────
        if _m(low, ['workers', 'agents', 'team', 'who works for you', 'list workers', 'show workers', 'worker chat', 'talk to worker']):
            names = ', '.join(w['name'] for w in WORKERS[:4])
            return (
                f"NEXUS has **22 specialised AI workers** across 21 pipeline stages, {name}.\n\n"
                f"**Top workers:** {names}, and 18 more specialists.\n\n"
                f"**Workers Chat** — you can now speak directly to any worker in the Workers section. "
                f"Each worker responds with their specialist knowledge: ask the Architect about system design, "
                f"the Security AI about vulnerabilities, the Design AI about UI patterns.\n\n"
                f"Workers also have a **live activity feed** — watch them write code, plan architecture, "
                f"and run tests in real time during a build.\n\n"
                f"**Upgrade workers:** Workers improve with every build they run. "
                f"The more builds you do, the better their outputs get — especially for your specific domain.\n\n"
                f"Go to **AI Workers** to see the full team and their live status."
            )

        # ── PIPELINE / HOW IT WORKS ────────────────────────────────────────────
        if _m(low, ['pipeline', 'stages', 'process', 'how does it work', 'how does nexus work']):
            return (
                f"**The NEXUS 21-stage pipeline — master level explanation:**\n\n"
                f"**Phase 1 — Intelligence (Stages 0-3):**\n"
                f"Vision Parser reads your goal → Capability Assessor checks what's possible → "
                f"Research AI finds best patterns → Module Detector maps dependencies\n\n"
                f"**Phase 2 — Architecture (Stages 4-7):**\n"
                f"Planner AI creates the full roadmap → Architect designs the system → "
                f"Database AI designs the data layer → Coder AI writes all source code\n\n"
                f"**Phase 3 — Quality (Stages 8-11):**\n"
                f"Design AI creates UI/UX → Reviewer AI checks code quality → "
                f"Tester AI writes and runs tests → Security AI scans for vulnerabilities\n\n"
                f"**Phase 4 — Production (Stages 12-20):**\n"
                f"Performance → Documentation → Monitoring → Integration → DevOps → "
                f"Deployment packaging → Verification → Progress tracking → Memory storage\n\n"
                f"**Quality gates at stages 9, 10, 11, and 18** can halt the pipeline. "
                f"A download is NEVER generated unless all gates pass. This is the NEXUS honesty contract."
            )

        # ── BUILD INTENT ───────────────────────────────────────────────────────
        if _m(low, ['build', 'create', 'make', 'develop', 'generate', 'implement']) and \
           not _m(low, ['how to build', 'can you build', 'what can you build', 'how does']):
            intent = self.detect_intent(msg, owner)
            if intent['is_build']:
                return (
                    f"Understood, {name}. Let me assess this properly.\n\n"
                    f"**Project type detected:** {intent['project_type']}\n"
                    f"**Goal:** {intent['goal'][:120]}\n\n"
                    f"**Before I build — let me give you the master-level breakdown:**\n\n"
                    f"**Monetization:** How will this make money? (subscription, one-time, ads, commission?)\n"
                    f"**Target user:** Who specifically will use this? (age, location, profession?)\n"
                    f"**Key differentiator:** What makes this better than existing solutions?\n\n"
                    f"If you already know all of this — click **Launch Build** below and "
                    f"I'll dispatch all 22 workers immediately. "
                    f"If you want me to help refine the strategy first, just ask."
                )

        # ── THANK YOU / POSITIVE ───────────────────────────────────────────────
        if _m(low, ['thank', 'thanks', 'good job', 'well done', 'perfect', 'amazing', 'great', 'awesome']):
            return (
                f"You're welcome, {name}. That's what NEXUS is for — "
                f"to make you faster, sharper, and more profitable.\n\n"
                f"Ready for the next move? I can find you a profitable idea, start a new build, "
                f"help you grow on social media, or just talk strategy. What's next?"
            )

        # ── GRAMMAR CORRECTION NOTE ────────────────────────────────────────────
        if found_corrections and len(msg) < 40:
            corrected = msg
            for wrong, right in found_corrections.items():
                corrected = re.sub(re.escape(wrong), right, corrected, flags=re.I)
            return (
                f"*(I noticed a small spelling — did you mean: \"{corrected}\"?)*\n\n"
                f"Just to make sure I understand correctly: what would you like me to help you with?"
            )

        # ── CONTEXT-AWARE BUILD ────────────────────────────────────────────────
        if _m(ctx_text, ['build', 'project', 'create', 'app']) and len(msg) > 20:
            intent = self.detect_intent(msg, owner)
            if intent['is_build']:
                return (
                    f"Perfect timing, {name}. Based on our conversation context:\n\n"
                    f"**Goal:** {intent['goal'][:150]}\n"
                    f"**Type:** {intent['project_type']}\n\n"
                    f"Click **Launch Build** to start the 21-stage pipeline with all 22 workers, "
                    f"or describe more requirements and I'll refine the specification."
                )

        # ── INTELLIGENT DEFAULT ────────────────────────────────────────────────
        return (
            f"I'm on it, {name}.\n\n"
            f"NEXUS Master AI v3.0 is listening — tell me more about what you want to achieve "
            f"and I'll give you the most direct, profitable path to get there.\n\n"
            f"My specialities: **building software**, **finding profitable niches**, "
            f"**designing user-attractive apps**, **social media growth**, and **business strategy**.\n\n"
            f"What's the goal?"
        )


def _m(text: str, keywords: list) -> bool:
    return any(kw in text for kw in keywords)
