"""
NEXUS
Capability Assessor AI — Honest Feature Classification Engine

Module ID : ASSESS-001
Version   : 1.0.0

Responsibilities
----------------
• Compare every requested feature against actual NEXUS capabilities
• Classify each feature as: FULLY_SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED
• Generate a capability gap report before any code is written
• Never claim unsupported features are complete
• Produce an honest build feasibility score
"""

from datetime import datetime


class CapabilityAssessorAI:
    """
    Honest Feature Classification Engine.

    Compares requested features/modules against NEXUS's real
    capabilities and produces a transparent gap report.

    This engine NEVER claims capability that does not exist.
    """

    # ------------------------------------------------------------------ #
    # Capability registry                                                  #
    # ------------------------------------------------------------------ #

    FULLY_SUPPORTED = {
        "python_cli":            "Python CLI applications",
        "rest_api":              "REST API (FastAPI with endpoints, models, routing)",
        "web_app":               "Web application backend (Flask routes, templates)",
        "todo_app":              "Todo / task management applications",
        "calculator":            "Calculator and computation tools",
        "data_analyzer":         "Data analysis scripts (stdlib only)",
        "text_game":             "Text-based games and interactive fiction",
        "inventory":             "Inventory management systems",
        "file_manager":          "File manager utilities",
        "scheduler":             "Task schedulers and cron-style automation",
        "ai_system_stdlib":      "Lightweight AI (KNN, Linear Regression — stdlib only)",
        "chat_app_sockets":      "Chat application (stdlib sockets)",
        "desktop_gui_tkinter":   "Desktop GUI (tkinter)",
        "sqlite_schema":         "SQL schema generation (SQLite DDL + Python helper)",
        "static_code_analysis":  "Static code analysis (AST, quality gate)",
        "runtime_testing":       "Sandboxed runtime validation",
        "security_scan":         "Vulnerability and secret scanning",
        "performance_profiling": "Benchmarking and cyclomatic complexity analysis",
        "documentation_gen":     "README, API docs, Architecture docs, CHANGELOG",
        "monitoring_config":     "Health check, metrics, logger config, alerts config",
        "devops_artifacts":      "Dockerfile, CI/CD YAML, Makefile",
        "deployment_package":    "Release archive, requirements.txt, deployment.json",
        "integration_config":    "API client, webhook handler, integration config",
        "knowledge_base_json":   "JSON-backed research knowledge base",
        "dependency_graph":      "Module dependency graph generation",
        "progress_reporting":    "Build progress reports with completion percentages",
        "capability_assessment": "Feature classification before code generation",
        "vision_parsing":        "Vision document parsing and requirement extraction",
        "module_detection":      "Automatic module detection from requirements",
    }

    PARTIALLY_SUPPORTED = {
        "web_frontend":          ("CSS and basic HTML generated; no JavaScript framework (React/Vue/Angular)", 40),
        "authentication":        ("JWT referenced in architecture; no login/register code generated",          20),
        "database_advanced":     ("SQLite only; no PostgreSQL/MySQL/MongoDB/Redis support",                    35),
        "testing_framework":     ("Runtime sandbox only; no pytest files, no unit/integration test files",     25),
        "knowledge_management":  ("Basic JSON store; no semantic search, graph traversal, or versioning",      30),
        "api_documentation":     ("Markdown docs generated; no OpenAPI/Swagger interactive spec",              50),
        "security_hardening":    ("Scanning only; no automated patching, WAF, or rate limiting code",          30),
        "monitoring_system":     ("Config files generated; no live metrics collection or alerting runtime",    35),
        "deployment_automation": ("Artifacts generated; no real cloud deploy commands or registry push",       40),
        "architecture_design":   ("Blueprint generated; no UML diagrams, no formal ADRs",                      50),
        "ai_planning":           ("Sequential pipeline; no probabilistic reasoning or confidence scoring",     40),
        "multi_module_projects": ("Single-file templates; no multi-package repo generation",                   35),
    }

    UNSUPPORTED = {
        "android_apps":          "Android applications (Kotlin/Java/Compose)",
        "ios_apps":              "iOS applications (Swift/SwiftUI)",
        "cross_platform_mobile": "Cross-platform mobile (Flutter/React Native)",
        "real_time_business":    "Live business operations dashboard",
        "financial_accounting":  "Financial management / accounting engine",
        "stock_market_intel":    "Stock market screening and portfolio management",
        "forex_trading":         "Forex analysis and trading strategy engine",
        "social_media_mgmt":     "Social media scheduling and management",
        "graphic_design":        "Graphic design (logos, posters, flyers, branding)",
        "image_processing":      "Image enhancement, background removal, upscaling",
        "video_production":      "Video scripting, editing, animation",
        "advertising_engine":    "Advertising campaign creation and management",
        "market_research_live":  "Live market research and competitor scraping",
        "multi_business_os":     "Multi-business workspace management",
        "payment_processing":    "Payment gateway integration (Stripe/PayPal live)",
        "customer_crm":          "CRM / customer relationship management",
        "self_improvement":      "System self-analysis and self-upgrade engine",
        "predictive_analytics":  "Predictive analytics and ML forecasting engine",
        "revenue_intelligence":  "Revenue tracking and intelligence dashboard",
        "email_communications":  "Email system management and campaign delivery",
        "cloud_infrastructure":  "Live cloud deployment (AWS/GCP/Azure provisioning)",
        "kubernetes_orchestr":   "Kubernetes / container orchestration",
        "enterprise_sso":        "Enterprise SSO / OAuth2 / SAML integration",
        "blockchain_web3":       "Blockchain, smart contracts, Web3",
        "iot_robotics":          "IoT, robotics, device management",
        "executive_assistant":   "Proactive executive assistant (continuous monitoring)",
        "nlp_advanced":          "Advanced NLP (LLM-powered reasoning, summarization)",
        "community_management":  "Community moderation and social engagement",
        "seo_engine":            "Live SEO analysis and optimization engine",
    }

    # ------------------------------------------------------------------ #
    # Module → capability mapping                                         #
    # ------------------------------------------------------------------ #

    _MODULE_CAPABILITY_MAP = {
        "ai_core":          ["ai_planning", "nlp_advanced", "predictive_analytics"],
        "memory":           ["knowledge_management", "knowledge_base_json"],
        "knowledge_graph":  ["knowledge_management"],
        "security":         ["security_scan", "security_hardening", "authentication"],
        "authentication":   ["authentication", "enterprise_sso"],
        "finance":          ["financial_accounting", "payment_processing", "revenue_intelligence"],
        "business":         ["multi_business_os", "customer_crm", "real_time_business"],
        "research":         ["knowledge_base_json", "market_research_live"],
        "creative_studio":  ["graphic_design", "image_processing", "video_production"],
        "marketing":        ["advertising_engine", "seo_engine", "social_media_mgmt"],
        "analytics":        ["predictive_analytics", "performance_profiling"],
        "monitoring":       ["monitoring_config", "monitoring_system"],
        "deployment":       ["devops_artifacts", "deployment_package", "cloud_infrastructure"],
        "documentation":    ["documentation_gen"],
        "testing":          ["runtime_testing", "testing_framework"],
        "api_layer":        ["rest_api", "integration_config"],
        "automation":       ["scheduler", "deployment_automation"],
        "data_management":  ["sqlite_schema", "database_advanced"],
        "prediction":       ["predictive_analytics", "ai_system_stdlib"],
        "mobile":           ["android_apps", "ios_apps", "cross_platform_mobile"],
        "desktop":          ["desktop_gui_tkinter"],
        "web":              ["web_app", "web_frontend"],
    }

    # ------------------------------------------------------------------ #

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Capability Assessor AI] Connected to Shared Memory.")

    def start(self):
        print("[Capability Assessor AI] Honest Feature Classification Engine Ready.")

    # ------------------------------------------------------------------ #
    # Assessment logic                                                     #
    # ------------------------------------------------------------------ #

    def assess(self, vision_spec: dict) -> dict:
        """
        Assess what can be built from the vision specification.
        Returns a structured capability report.
        """
        modules   = vision_spec.get("modules", [])
        features  = vision_spec.get("features", [])
        f_reqs    = vision_spec.get("functional_requirements", [])

        # Collect all capability keys relevant to requested modules
        requested_caps = set()
        for module in modules:
            for cap in self._MODULE_CAPABILITY_MAP.get(module, []):
                requested_caps.add(cap)

        # Always include core pipeline capabilities
        core_always = {
            "vision_parsing", "capability_assessment", "module_detection",
            "dependency_graph", "progress_reporting", "documentation_gen",
            "static_code_analysis", "runtime_testing", "security_scan",
            "performance_profiling", "monitoring_config", "devops_artifacts",
            "deployment_package", "integration_config", "knowledge_base_json",
        }
        requested_caps |= core_always

        # Classify
        fully     = {}
        partially = {}
        unsup     = {}

        for cap in requested_caps:
            if cap in self.FULLY_SUPPORTED:
                fully[cap] = self.FULLY_SUPPORTED[cap]
            elif cap in self.PARTIALLY_SUPPORTED:
                desc, pct  = self.PARTIALLY_SUPPORTED[cap]
                partially[cap] = {"description": desc, "completion_pct": pct}
            elif cap in self.UNSUPPORTED:
                unsup[cap] = self.UNSUPPORTED[cap]

        # Scan functional requirements for unsupported patterns
        unsup_from_reqs = self._scan_requirements_for_gaps(f_reqs + features)
        for k, v in unsup_from_reqs.items():
            if k not in fully and k not in partially:
                unsup[k] = v

        # Feasibility score
        total = len(fully) + len(partially) + len(unsup)
        if total == 0:
            total = 1
        partial_weight = sum(
            v["completion_pct"] for v in partially.values()
        ) / (100 * max(len(partially), 1)) * len(partially)

        feasibility_score = round(
            ((len(fully) + partial_weight) / total) * 100, 1
        )

        buildable_now   = len(fully)
        partial_now     = len(partially)
        not_buildable   = len(unsup)

        return {
            "assessed_at":               datetime.utcnow().isoformat(),
            "modules_requested":         modules,
            "fully_supported":           fully,
            "partially_supported":       partially,
            "unsupported":               unsup,
            "total_capabilities_checked":total,
            "buildable_now":             buildable_now,
            "partially_buildable":       partial_now,
            "not_buildable":             not_buildable,
            "feasibility_score":         feasibility_score,
            "honest_summary":            self._build_summary(
                                             fully, partially, unsup, feasibility_score
                                         ),
        }

    def _scan_requirements_for_gaps(self, items: list) -> dict:
        """Scan requirement text for patterns that map to unsupported capabilities."""
        patterns = {
            "android_apps":         ["android", "kotlin"],
            "ios_apps":             ["ios", "swift", "iphone"],
            "cross_platform_mobile":["flutter", "react native"],
            "financial_accounting": ["accounting", "payroll", "ledger"],
            "payment_processing":   ["stripe", "paypal", "payment gateway"],
            "graphic_design":       ["logo design", "poster", "brochure", "flyer"],
            "image_processing":     ["background removal", "upscal", "image enhance"],
            "video_production":     ["video edit", "animation", "reel", "storyboard"],
            "social_media_mgmt":    ["social media schedul", "instagram post", "tweet"],
            "self_improvement":     ["self-improv", "self improv", "analyse own code"],
            "nlp_advanced":         ["llm", "gpt", "large language", "openai api"],
            "cloud_infrastructure": ["aws", "gcp", "azure", "kubernetes"],
            "blockchain_web3":      ["blockchain", "smart contract", "nft", "web3"],
        }
        found = {}
        combined = " ".join(items).lower()
        for cap, keywords in patterns.items():
            if any(kw in combined for kw in keywords):
                if cap in self.UNSUPPORTED:
                    found[cap] = self.UNSUPPORTED[cap]
        return found

    def _build_summary(
        self,
        fully: dict,
        partially: dict,
        unsup: dict,
        score: float,
    ) -> str:
        lines = [
            f"NEXUS can fully implement {len(fully)} capabilities,",
            f"partially implement {len(partially)} capabilities,",
            f"and cannot currently implement {len(unsup)} capabilities.",
            f"Overall build feasibility: {score}%.",
        ]
        if unsup:
            lines.append(
                "Unsupported features will be documented as planned "
                "placeholders — they will NOT be falsely reported as complete."
            )
        return " ".join(lines)

    # ------------------------------------------------------------------ #
    # Pipeline entry point                                                 #
    # ------------------------------------------------------------------ #

    def process_project_task(self, task_id: str):
        project_key = f"active_project_{task_id}"
        project     = self.memory.read(project_key)

        if project is None:
            print(f"[Capability Assessor AI] Project '{task_id}' not found.")
            return

        vision_spec = project.get("vision_spec", {})
        print(f"[Capability Assessor AI] Assessing capabilities for: {task_id}")

        report = self.assess(vision_spec)

        project["capability_report"] = report
        project["status"]            = "CAPABILITY_ASSESSED"

        self.memory.write(project_key, project)

        print(f"[Capability Assessor AI] Fully Supported    : {report['buildable_now']}")
        print(f"[Capability Assessor AI] Partially Supported: {report['partially_buildable']}")
        print(f"[Capability Assessor AI] Unsupported        : {report['not_buildable']}")
        print(f"[Capability Assessor AI] Feasibility Score  : {report['feasibility_score']}%")
        print(f"[Capability Assessor AI] {report['honest_summary']}")
