"""
NEXUS
Vision Parser AI — Master Vision Document Intelligence Engine

Module ID : VISION-001
Version   : 1.0.0

Responsibilities
----------------
• Parse large vision documents (plain text, structured documents)
• Extract functional requirements
• Extract non-functional requirements
• Extract features, modules, dependencies, technologies
• Extract security, infrastructure, business, financial, AI requirements
• Organize everything into structured specifications
• Detect whether input is a simple goal or a full vision document
"""

import re
import hashlib
from datetime import datetime


class VisionParserAI:
    """
    Master Vision Document Intelligence Engine.

    Parses vision documents of any size and extracts structured
    specifications before any code is generated.
    """

    # ------------------------------------------------------------------ #
    # Keyword maps for requirement extraction                              #
    # ------------------------------------------------------------------ #

    _FUNCTIONAL_KEYWORDS = [
        "shall", "must", "will", "should", "capable of", "able to",
        "support", "provide", "allow", "enable", "generate", "create",
        "manage", "monitor", "track", "analyse", "analyze", "detect",
        "report", "produce", "build", "design", "implement", "integrate",
    ]

    _NON_FUNCTIONAL_KEYWORDS = [
        "scalable", "reliable", "secure", "maintainable", "extensible",
        "modular", "transparent", "efficient", "performant", "available",
        "resilient", "auditable", "observable", "testable", "upgradeable",
        "encrypted", "compliant", "accessible", "responsive", "portable",
    ]

    _MODULE_KEYWORDS = {
        "ai_core":            ["intelligence core", "reasoning engine", "ai core", "central ai", "decision engine"],
        "memory":             ["memory system", "long-term memory", "working memory", "memory architecture", "persistent memory"],
        "knowledge_graph":    ["knowledge graph", "knowledge system", "knowledge base", "semantic relationship", "fact store"],
        "security":           ["security", "vulnerability", "encryption", "access control", "audit", "threat"],
        "authentication":     ["authentication", "authorisation", "authorization", "login", "sso", "oauth", "jwt", "2fa"],
        "finance":            ["financial", "finance", "accounting", "revenue", "expense", "budget", "invoice", "tax"],
        "business":           ["business operating", "company", "enterprise", "crm", "customer", "supplier", "inventory"],
        "research":           ["research", "knowledge retrieval", "information gathering", "market research"],
        "creative_studio":    ["creative studio", "graphic design", "image", "video", "visual", "brand", "logo", "poster"],
        "marketing":          ["marketing", "advertising", "campaign", "seo", "social media", "content creation", "brand"],
        "analytics":          ["analytics", "predictive", "forecasting", "trend", "metric", "kpi", "dashboard"],
        "monitoring":         ["monitoring", "health check", "observability", "alert", "logging", "metrics"],
        "deployment":         ["deployment", "devops", "dockerfile", "ci/cd", "kubernetes", "infrastructure", "cloud"],
        "documentation":      ["documentation", "readme", "api docs", "changelog", "user guide", "developer guide"],
        "testing":            ["testing", "unit test", "integration test", "quality assurance", "validation"],
        "api_layer":          ["api", "rest", "graphql", "webhook", "endpoint", "integration layer"],
        "automation":         ["automation", "automated", "scheduler", "workflow", "repetitive", "pipeline"],
        "data_management":    ["database", "data store", "data management", "sql", "nosql", "schema"],
        "prediction":         ["prediction", "predictive analysis", "forecasting", "probability", "machine learning", "ml"],
        "mobile":             ["android", "ios", "mobile app", "flutter", "react native", "swift", "kotlin"],
        "desktop":            ["desktop", "gui", "tkinter", "electron", "native application"],
        "web":                ["web application", "website", "frontend", "html", "css", "javascript", "react", "vue"],
    }

    _TECHNOLOGY_KEYWORDS = [
        "python", "javascript", "typescript", "kotlin", "swift", "java", "go", "rust",
        "react", "vue", "angular", "flutter", "fastapi", "flask", "django", "express",
        "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
        "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
        "jwt", "oauth", "rest", "graphql", "grpc", "websocket",
        "tensorflow", "pytorch", "scikit-learn", "openai", "llm",
        "stripe", "paypal", "twilio", "sendgrid", "firebase",
    ]

    _SECURITY_KEYWORDS = [
        "encrypt", "authentication", "authorisation", "authorization", "audit trail",
        "access control", "rbac", "vulnerability", "penetration", "firewall",
        "tls", "ssl", "secret", "token", "hash", "salt", "certificate",
        "gdpr", "compliance", "data protection", "privacy",
    ]

    _INFRASTRUCTURE_KEYWORDS = [
        "cloud", "server", "docker", "kubernetes", "container", "vm", "virtual machine",
        "load balancer", "cdn", "dns", "nginx", "apache", "reverse proxy",
        "backup", "recovery", "disaster", "high availability", "failover",
        "ci/cd", "pipeline", "terraform", "ansible",
    ]

    _BUSINESS_KEYWORDS = [
        "business", "company", "revenue", "customer", "product", "service",
        "market", "competitor", "supplier", "contract", "license", "brand",
        "employee", "hr", "payroll", "inventory", "crm", "erp",
    ]

    _FINANCIAL_KEYWORDS = [
        "financial", "finance", "accounting", "revenue", "expense", "profit",
        "cash flow", "budget", "forecast", "tax", "invoice", "payment",
        "subscription", "billing", "stripe", "paypal", "transaction",
        "stock", "forex", "investment", "portfolio",
    ]

    _AI_KEYWORDS = [
        "artificial intelligence", "machine learning", "neural network", "llm",
        "natural language", "nlp", "computer vision", "prediction", "classification",
        "reinforcement learning", "recommendation", "generative ai", "embedding",
        "reasoning engine", "knowledge graph", "semantic", "inference",
    ]

    _DEPLOYMENT_KEYWORDS = [
        "deploy", "deployment", "release", "publish", "production", "staging",
        "docker", "kubernetes", "ci/cd", "pipeline", "artifact", "package",
        "version", "rollback", "blue-green", "canary",
    ]

    # ------------------------------------------------------------------ #

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Vision Parser AI] Connected to Shared Memory.")

    def start(self):
        print("[Vision Parser AI] Master Vision Document Intelligence Engine Ready.")

    # ------------------------------------------------------------------ #
    # Detection: is this a vision doc or a simple goal?                   #
    # ------------------------------------------------------------------ #

    def _is_vision_document(self, text: str) -> bool:
        """Return True if text looks like a full vision/spec document."""
        indicators = [
            len(text) > 500,
            text.lower().count("shall") > 3,
            text.lower().count("\n") > 10,
            any(h in text.lower() for h in ["mission", "objective", "philosophy", "vision", "requirement"]),
            text.count("•") > 5 or text.count("-") > 10,
        ]
        return sum(indicators) >= 3

    # ------------------------------------------------------------------ #
    # Extraction helpers                                                   #
    # ------------------------------------------------------------------ #

    def _extract_sentences(self, text: str) -> list:
        sentences = re.split(r'(?<=[.!?])\s+|\n', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    def _extract_functional_requirements(self, text: str) -> list:
        reqs = []
        seen = set()
        for sentence in self._extract_sentences(text):
            lower = sentence.lower()
            if any(kw in lower for kw in self._FUNCTIONAL_KEYWORDS):
                h = hashlib.md5(sentence.encode()).hexdigest()
                if h not in seen:
                    seen.add(h)
                    reqs.append(sentence[:200])
        return reqs[:50]

    def _extract_non_functional_requirements(self, text: str) -> list:
        reqs = []
        seen = set()
        for sentence in self._extract_sentences(text):
            lower = sentence.lower()
            if any(kw in lower for kw in self._NON_FUNCTIONAL_KEYWORDS):
                h = hashlib.md5(sentence.encode()).hexdigest()
                if h not in seen:
                    seen.add(h)
                    reqs.append(sentence[:200])
        return reqs[:30]

    def _extract_features(self, text: str) -> list:
        features = []
        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("•", "-", "*", "·")) and len(stripped) > 5:
                feature = stripped.lstrip("•-*· ").strip()
                if feature and len(feature) > 5:
                    features.append(feature[:150])
        return list(dict.fromkeys(features))[:80]

    def _detect_modules(self, text: str) -> list:
        lower = text.lower()
        detected = []
        for module, keywords in self._MODULE_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                detected.append(module)
        return detected

    def _extract_technologies(self, text: str) -> list:
        lower = text.lower()
        return [t for t in self._TECHNOLOGY_KEYWORDS if t in lower]

    def _extract_by_keywords(self, text: str, keywords: list) -> list:
        reqs = []
        seen = set()
        for sentence in self._extract_sentences(text):
            lower = sentence.lower()
            if any(kw in lower for kw in keywords):
                h = hashlib.md5(sentence.encode()).hexdigest()
                if h not in seen:
                    seen.add(h)
                    reqs.append(sentence[:200])
        return reqs[:20]

    def _extract_section_titles(self, text: str) -> list:
        titles = []
        for line in text.splitlines():
            s = line.strip()
            if (
                s.isupper() and len(s) > 4
                or re.match(r'^(PART|SECTION|CHAPTER)\s+\d+', s, re.I)
                or re.match(r'^#{1,3}\s+\S', s)
            ):
                titles.append(s[:100])
        return list(dict.fromkeys(titles))[:30]

    def _estimate_complexity(self, spec: dict) -> str:
        score = 0
        score += min(len(spec.get("functional_requirements", [])), 20)
        score += min(len(spec.get("modules", [])) * 3, 30)
        score += min(len(spec.get("features", [])) // 5, 20)
        score += len(spec.get("technologies", [])) * 2
        score += len(spec.get("ai_requirements", [])) * 2
        if score < 20:
            return "LOW"
        if score < 50:
            return "MEDIUM"
        if score < 80:
            return "HIGH"
        return "ENTERPRISE"

    def _estimate_phases(self, spec: dict) -> int:
        modules = len(spec.get("modules", []))
        if modules <= 3:
            return 3
        if modules <= 8:
            return 6
        if modules <= 15:
            return 12
        return 20

    # ------------------------------------------------------------------ #
    # Main parse                                                           #
    # ------------------------------------------------------------------ #

    def parse(self, text: str) -> dict:
        """
        Parse a goal string or full vision document.
        Returns a structured specification dictionary.
        """
        is_vision = self._is_vision_document(text)

        if is_vision:
            spec = {
                "document_type":              "VISION_DOCUMENT",
                "parsed_at":                  datetime.utcnow().isoformat(),
                "document_length_chars":      len(text),
                "document_length_lines":      text.count("\n"),
                "section_titles":             self._extract_section_titles(text),
                "functional_requirements":    self._extract_functional_requirements(text),
                "non_functional_requirements":self._extract_non_functional_requirements(text),
                "features":                   self._extract_features(text),
                "modules":                    self._detect_modules(text),
                "technologies":               self._extract_technologies(text),
                "security_requirements":      self._extract_by_keywords(text, self._SECURITY_KEYWORDS),
                "infrastructure_requirements":self._extract_by_keywords(text, self._INFRASTRUCTURE_KEYWORDS),
                "business_requirements":      self._extract_by_keywords(text, self._BUSINESS_KEYWORDS),
                "financial_requirements":     self._extract_by_keywords(text, self._FINANCIAL_KEYWORDS),
                "research_requirements":      self._extract_by_keywords(text, ["research", "analyse", "study", "investigate"]),
                "ai_requirements":            self._extract_by_keywords(text, self._AI_KEYWORDS),
                "deployment_requirements":    self._extract_by_keywords(text, self._DEPLOYMENT_KEYWORDS),
            }
        else:
            # Simple goal — generate a minimal spec
            lower = text.lower()
            spec = {
                "document_type":               "SIMPLE_GOAL",
                "parsed_at":                   datetime.utcnow().isoformat(),
                "document_length_chars":       len(text),
                "document_length_lines":       1,
                "section_titles":              [],
                "functional_requirements":     [text],
                "non_functional_requirements": ["Reliable", "Maintainable", "Testable"],
                "features":                    [],
                "modules":                     self._detect_modules(text),
                "technologies":                self._extract_technologies(text),
                "security_requirements":       [],
                "infrastructure_requirements": [],
                "business_requirements":       [],
                "financial_requirements":      [],
                "research_requirements":       [],
                "ai_requirements":             self._extract_by_keywords(text, self._AI_KEYWORDS),
                "deployment_requirements":     [],
            }

        spec["complexity"]      = self._estimate_complexity(spec)
        spec["estimated_phases"] = self._estimate_phases(spec)
        return spec

    # ------------------------------------------------------------------ #
    # Pipeline entry point                                                 #
    # ------------------------------------------------------------------ #

    def process_project_task(self, task_id: str):
        project_key = f"active_project_{task_id}"
        project     = self.memory.read(project_key)

        if project is None:
            print(f"[Vision Parser AI] Project '{task_id}' not found.")
            return

        goal = project.get("goal", "")
        print(f"[Vision Parser AI] Parsing input: {len(goal)} characters")

        # ── NEXUS AI: extract requirements intelligently ─────────── #
        spec = None
        try:
            from core.nexus_ai import NexusAI
            nexus   = NexusAI(self.memory)
            ai_raw  = nexus.generate_requirements(goal, {})
            ai_spec = nexus.parse_json(ai_raw)
            if ai_spec.get("functional_requirements") and ai_spec.get("features"):
                # Merge AI extraction into full spec structure
                base_spec = self.parse(goal)
                base_spec["functional_requirements"]     = ai_spec.get("functional_requirements",     base_spec["functional_requirements"])
                base_spec["non_functional_requirements"] = ai_spec.get("non_functional_requirements", base_spec["non_functional_requirements"])
                base_spec["features"]                    = ai_spec.get("features",                    base_spec["features"])
                base_spec["modules"]                     = ai_spec.get("modules",                     base_spec["modules"])
                base_spec["technologies"]                = ai_spec.get("technologies",                base_spec["technologies"])
                if ai_spec.get("complexity"):
                    base_spec["complexity"]       = ai_spec["complexity"].upper()
                if ai_spec.get("estimated_phases"):
                    base_spec["estimated_phases"] = ai_spec["estimated_phases"]
                spec = base_spec
                print(f"[Vision Parser AI] Provider : {nexus._provider_instance().name()}")
        except Exception as _exc:
            print(f"[Vision Parser AI] AI parsing skipped ({_exc}), using keyword engine.")

        # Fallback: existing keyword/regex parser
        if spec is None:
            spec = self.parse(goal)

        project["vision_spec"]   = spec
        project["status"]        = "VISION_PARSED"

        self.memory.write(project_key, project)

        doc_type = spec["document_type"]
        print(f"[Vision Parser AI] Document Type    : {doc_type}")
        print(f"[Vision Parser AI] Complexity       : {spec['complexity']}")
        print(f"[Vision Parser AI] Sections Found   : {len(spec['section_titles'])}")
        print(f"[Vision Parser AI] Functional Reqs  : {len(spec['functional_requirements'])}")
        print(f"[Vision Parser AI] Modules Detected : {len(spec['modules'])}")
        print(f"[Vision Parser AI] Technologies     : {len(spec['technologies'])}")
        print(f"[Vision Parser AI] Est. Phases      : {spec['estimated_phases']}")
        print(f"[Vision Parser AI] Specification structured.")
