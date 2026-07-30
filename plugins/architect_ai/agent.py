"""
NEXUS
Architect AI — Comprehensive Systems Design Engine

Module ID : ARCHITECT-001
Version   : 2.0.0

Responsibilities
----------------
• Generate overall software architecture
• Generate module architecture (each module's structure)
• Generate service architecture (service boundaries and communication)
• Generate API architecture (endpoints, versioning, contracts)
• Generate database architecture (schema strategy, indexing)
• Generate event architecture (async events, queues)
• Generate security architecture (threat model, layers)
• Generate deployment architecture (environments, scaling)
• Generate communication architecture (sync vs async, protocols)
• Explain every architectural decision with reasoning
"""

from datetime import datetime


class ArchitectAI:
    """
    Comprehensive Systems Design Engine.

    Generates nine architecture layers before any code is written.
    Every decision includes a 'reason' field explaining why it was made.
    """

    # ------------------------------------------------------------------ #
    # Architecture templates per project type                              #
    # ------------------------------------------------------------------ #

    _ARCH_PROFILES = {
        "rest_api": {
            "framework":   "FastAPI",
            "language":    "Python 3.11+",
            "api_style":   "REST with OpenAPI",
            "database":    "SQLite (dev) → PostgreSQL (prod)",
            "auth":        "JWT Bearer tokens",
            "deployment":  "Docker + CI/CD",
            "pattern":     "Layered (Router → Service → Repository)",
            "reason":      "FastAPI provides automatic OpenAPI docs, async support, and type safety via Pydantic — optimal for REST APIs requiring documentation and validation.",
        },
        "web_app": {
            "framework":   "Flask",
            "language":    "Python 3.11+",
            "api_style":   "Server-side rendering + REST endpoints",
            "database":    "SQLite",
            "auth":        "Session-based",
            "deployment":  "Gunicorn + Docker",
            "pattern":     "MVC (Blueprint → Template → Model)",
            "reason":      "Flask's minimal footprint and Jinja2 templating suit web apps where server-side rendering is preferred over a separate SPA frontend.",
        },
        "todo_app": {
            "framework":   "Python stdlib",
            "language":    "Python 3.11+",
            "api_style":   "CLI / local storage",
            "database":    "SQLite (JSON fallback)",
            "auth":        "None (single-user)",
            "deployment":  "Local executable",
            "pattern":     "Simple MVC (REPL → Logic → Storage)",
            "reason":      "A todo app requires minimal dependencies. Stdlib keeps it portable and fast with zero installation friction.",
        },
        "ai_system": {
            "framework":   "Python stdlib (numpy-free KNN/LinReg)",
            "language":    "Python 3.11+",
            "api_style":   "CLI training and inference",
            "database":    "JSON model store",
            "auth":        "None",
            "deployment":  "Local executable",
            "pattern":     "Pipeline (Data → Train → Predict → Evaluate)",
            "reason":      "Stdlib-only AI keeps the system portable without requiring scientific stack installation. Suitable for lightweight classification and regression tasks.",
        },
        "desktop_gui": {
            "framework":   "tkinter",
            "language":    "Python 3.11+",
            "api_style":   "Event-driven GUI",
            "database":    "SQLite",
            "auth":        "None (single-user)",
            "deployment":  "Standalone executable",
            "pattern":     "MVP (View → Presenter → Model)",
            "reason":      "tkinter ships with Python — zero additional dependencies for a desktop GUI.",
        },
        "generic": {
            "framework":   "Python stdlib",
            "language":    "Python 3.11+",
            "api_style":   "CLI",
            "database":    "SQLite",
            "auth":        "None",
            "deployment":  "Local executable",
            "pattern":     "Modular Plugin Architecture",
            "reason":      "General-purpose modular design for projects where the type cannot be determined from the goal.",
        },
    }

    _DEFAULT_PROFILE = "generic"

    # ------------------------------------------------------------------ #
    # Module architecture templates                                        #
    # ------------------------------------------------------------------ #

    def _build_module_architecture(self, modules_data: dict, project_type: str) -> dict:
        manifest = modules_data.get("module_manifest", {})
        if not manifest:
            # Default minimal modules for simple projects
            manifest = {
                "core_engine":    {"layer": "foundation", "priority": 1},
                "config_manager": {"layer": "foundation", "priority": 2},
                "data_layer":     {"layer": "data",       "priority": 3},
            }

        return {
            "total_modules": len(manifest),
            "modules":       list(manifest.keys()),
            "layers":        self._group_by_layer(manifest),
            "entry_point":   "main.py",
            "reason":        (
                f"Modules are organized into layers so higher layers depend only "
                f"on lower layers — foundation first, then data, services, domain, "
                f"intelligence, and finally observability and infrastructure."
            ),
        }

    def _group_by_layer(self, manifest: dict) -> dict:
        layers = {}
        for name, meta in manifest.items():
            layer = meta.get("layer", "unknown")
            layers.setdefault(layer, []).append(name)
        return layers

    # ------------------------------------------------------------------ #
    # Individual architecture layers                                       #
    # ------------------------------------------------------------------ #

    def _service_architecture(self, profile: dict, project_type: str) -> dict:
        return {
            "pattern":          profile["pattern"],
            "service_boundary": "Single process (monolith) — can be split to microservices when traffic demands",
            "communication":    "In-process function calls; async via queue for background jobs",
            "error_handling":   "Structured exceptions with logging; all errors surfaced explicitly",
            "reason":           (
                "Starting monolithic reduces operational complexity. Clear service boundaries "
                "allow extraction to microservices later without full rewrite."
            ),
        }

    def _api_architecture(self, profile: dict, project_type: str) -> dict:
        is_api = project_type in ("rest_api", "web_app")
        return {
            "style":        profile["api_style"],
            "versioning":   "/api/v1/ prefix" if is_api else "N/A",
            "contracts":    "Pydantic models for request/response validation" if is_api else "N/A",
            "rate_limiting":"Header-based (X-RateLimit-*)" if is_api else "N/A",
            "documentation":"Auto-generated via FastAPI /docs" if project_type == "rest_api" else "Markdown",
            "reason":       (
                "API versioning protects consumers from breaking changes. "
                "Pydantic contracts enforce type safety at the boundary."
            ) if is_api else "No external API surface for this project type.",
        }

    def _database_architecture(self, profile: dict, project_type: str) -> dict:
        return {
            "engine":        profile["database"],
            "strategy":      "Repository pattern — business logic never queries DB directly",
            "migrations":    "Schema versioned via migration scripts",
            "indexing":      "Primary keys + foreign keys + query-specific indexes",
            "backup":        "Automated JSON export on every write for SQLite projects",
            "reason":        (
                "Repository pattern isolates DB-specific code so the storage engine "
                "can be swapped (SQLite → PostgreSQL) without touching business logic."
            ),
        }

    def _event_architecture(self, project_type: str) -> dict:
        uses_events = project_type in ("rest_api", "ai_system", "chat_app")
        return {
            "enabled":   uses_events,
            "pattern":   "In-process event bus (publish/subscribe)" if uses_events else "N/A",
            "events":    ["project.created", "task.completed", "error.raised"] if uses_events else [],
            "async":     "asyncio for I/O-bound; threading for CPU-bound" if uses_events else "N/A",
            "reason":    (
                "Event-driven design decouples producers from consumers, "
                "enabling future addition of listeners without modifying existing code."
            ) if uses_events else "Synchronous pipeline sufficient for this project type.",
        }

    def _security_architecture(self, profile: dict) -> dict:
        return {
            "authentication":    profile["auth"],
            "authorisation":     "Role-based access control (RBAC) when multi-user",
            "data_protection":   "Sensitive fields hashed (bcrypt); secrets via environment variables",
            "input_validation":  "All user input validated before processing (whitelist approach)",
            "audit_trail":       "All mutations logged with timestamp, actor, and before/after state",
            "threat_model":      [
                "SQL injection → parameterised queries",
                "XSS → output encoding",
                "Secret leakage → env vars, never hardcoded",
                "Dependency vulnerabilities → automated scanning",
            ],
            "reason":            (
                "Security-first architecture prevents retrofitting security as an afterthought. "
                "Each layer defends independently so a single failure does not compromise the system."
            ),
        }

    def _deployment_architecture(self, profile: dict) -> dict:
        return {
            "containerisation": "Docker (single Dockerfile)",
            "ci_cd":            "GitHub Actions — test → lint → build → deploy",
            "environments":     ["development", "staging", "production"],
            "scaling":          "Horizontal scaling behind load balancer when containerised",
            "rollback":         "Git tag per release; Docker image per version",
            "infrastructure":   profile["deployment"],
            "reason":           (
                "Docker ensures environment parity between dev and prod. "
                "Tagged releases enable instant rollback without downtime."
            ),
        }

    def _communication_architecture(self, project_type: str) -> dict:
        return {
            "internal":       "Direct function calls (synchronous)",
            "external":       "HTTP REST (JSON) for API projects; N/A otherwise",
            "async_tasks":    "asyncio event loop for I/O concurrency",
            "serialisation":  "JSON (human-readable, language-agnostic)",
            "protocols":      ["HTTP/1.1", "HTTPS", "WebSocket (if chat)"] if project_type in ("rest_api", "chat_app") else ["N/A"],
            "reason":         (
                "JSON serialisation maximises interoperability. "
                "Synchronous internal calls keep the codebase simple until async is genuinely needed."
            ),
        }

    # ------------------------------------------------------------------ #
    # Master architecture generator                                        #
    # ------------------------------------------------------------------ #

    def generate_architecture(self, project: dict) -> dict:
        research    = project.get("research", {})
        modules_data = project.get("modules", {})
        vision_spec  = project.get("vision_spec", {})

        project_type = (
            project.get("project_type")
            or research.get("project_type", "generic")
        )

        profile = self._ARCH_PROFILES.get(project_type, self._ARCH_PROFILES[self._DEFAULT_PROFILE])

        # Determine detected modules list
        detected_modules = []
        if modules_data.get("module_manifest"):
            detected_modules = list(modules_data["module_manifest"].keys())
        elif vision_spec.get("modules"):
            detected_modules = vision_spec["modules"]

        arch = {
            "generated_at":             datetime.utcnow().isoformat(),
            "project_type":             project_type,
            "framework":                profile["framework"],
            "language":                 profile["language"],
            "database":                 profile["database"],
            "authentication":           profile["auth"],
            "api_style":                profile["api_style"],
            "deployment":               profile["deployment"],
            "architecture_pattern":     profile["pattern"],
            "architecture_reason":      profile["reason"],
            "modules":                  detected_modules,

            # Nine architecture layers
            "module_architecture":      self._build_module_architecture(modules_data, project_type),
            "service_architecture":     self._service_architecture(profile, project_type),
            "api_architecture":         self._api_architecture(profile, project_type),
            "database_architecture":    self._database_architecture(profile, project_type),
            "event_architecture":       self._event_architecture(project_type),
            "security_architecture":    self._security_architecture(profile),
            "deployment_architecture":  self._deployment_architecture(profile),
            "communication_architecture": self._communication_architecture(project_type),

            # Guiding principles
            "principles": [
                "Separation of concerns — each module has one responsibility",
                "Dependency inversion — high-level modules do not depend on low-level details",
                "Open/closed principle — extend via new modules, not by modifying existing ones",
                "Fail-fast — invalid state raises an explicit error immediately",
                "Transparency — every decision is logged with reasoning",
                "Security-first — security is a layer, not an afterthought",
            ],
        }

        return arch

    # ------------------------------------------------------------------ #

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Architect AI] Connected to Shared Memory.")

    def start(self):
        print("[Architect AI] Comprehensive Systems Design Engine Ready.")

    def process_project_task(self, task_id: str):
        project_key = f"active_project_{task_id}"
        project     = self.memory.read(project_key)

        if project is None:
            print(f"[Architect AI] Project '{task_id}' not found.")
            return

        print(f"[Architect AI] Designing architecture: {task_id}")

        architecture = self.generate_architecture(project)

        # ── NEXUS AI: enrich architecture with AI reasoning ──────── #
        try:
            from core.nexus_ai import NexusAI
            nexus    = NexusAI(self.memory)
            goal     = project.get("goal", "")
            ptype    = architecture.get("project_type", "generic")
            modules  = architecture.get("modules", [])
            ai_raw   = nexus.generate_architecture(goal, ptype, modules)
            ai_arch  = nexus.parse_json(ai_raw)
            if ai_arch.get("architecture_pattern"):
                # Merge AI output into the rule-based architecture
                for key_field in ("architecture_pattern", "architecture_reason",
                                  "framework", "database", "authentication",
                                  "api_style", "layers"):
                    if ai_arch.get(key_field):
                        architecture[key_field] = ai_arch[key_field]
                print(f"[Architect AI] Provider : {nexus._provider_instance().name()}")
        except Exception as _exc:
            print(f"[Architect AI] AI enrichment skipped ({_exc}), using profile.")

        project["architecture"] = architecture
        project["status"]       = "SOFTWARE_ARCHITECTURE_DESIGN"

        self.memory.write(project_key, project)

        print(f"[Architect AI] Pattern    : {architecture['architecture_pattern']}")
        print(f"[Architect AI] Framework  : {architecture['framework']}")
        print(f"[Architect AI] Language   : {architecture['language']}")
        print(f"[Architect AI] Database   : {architecture['database']}")
        print(f"[Architect AI] Modules    : {len(architecture['modules'])}")
        print(f"[Architect AI] Auth       : {architecture['authentication']}")
        print(f"[Architect AI] Layers     : 9 architecture layers generated")
        print(f"[Architect AI] Reason     : {architecture['architecture_reason'][:100]}...")
