"""
NEXUS
Module Detector AI — Architecture Module & Dependency Graph Engine

Module ID : MODULE-001
Version   : 1.0.0

Responsibilities
----------------
• Identify all required modules from the vision specification
• Define each module's purpose, interfaces, and dependencies
• Generate a dependency graph (execution order, shared libs, APIs)
• Detect whether a project requires multi-repository structure
• Produce a module manifest for all downstream workers
"""

from datetime import datetime


class ModuleDetectorAI:
    """
    Architecture Module and Dependency Graph Engine.

    Identifies modules from vision specs and builds a dependency
    graph that drives the architecture and planning phases.
    """

    # ------------------------------------------------------------------ #
    # Module catalogue                                                     #
    # ------------------------------------------------------------------ #

    MODULE_CATALOGUE = {
        "core_engine": {
            "description":   "Central application bootstrap and entry point",
            "interfaces":    ["start()", "run()", "shutdown()"],
            "dependencies":  [],
            "output_files":  ["main.py", "__init__.py"],
            "priority":      1,
            "layer":         "foundation",
        },
        "config_manager": {
            "description":   "Application configuration and environment management",
            "interfaces":    ["load()", "get(key)", "set(key, value)"],
            "dependencies":  ["core_engine"],
            "output_files":  ["config.py", "config.json"],
            "priority":      2,
            "layer":         "foundation",
        },
        "shared_memory": {
            "description":   "In-process shared state bus between modules",
            "interfaces":    ["read(key)", "write(key, value)", "delete(key)"],
            "dependencies":  ["config_manager"],
            "output_files":  ["shared_memory.py"],
            "priority":      3,
            "layer":         "foundation",
        },
        "data_layer": {
            "description":   "Database access layer — schema, queries, migrations",
            "interfaces":    ["connect()", "query(sql)", "execute(sql)", "close()"],
            "dependencies":  ["config_manager"],
            "output_files":  ["schema.sql", "database.py"],
            "priority":      4,
            "layer":         "data",
        },
        "api_layer": {
            "description":   "REST API endpoints, routing, request/response handling",
            "interfaces":    ["GET /", "POST /", "PUT /", "DELETE /"],
            "dependencies":  ["data_layer", "auth_module", "security_module"],
            "output_files":  ["api/routes.py", "api/models.py"],
            "priority":      5,
            "layer":         "service",
        },
        "auth_module": {
            "description":   "Authentication and authorisation (JWT tokens, session)",
            "interfaces":    ["login()", "logout()", "verify_token()", "refresh()"],
            "dependencies":  ["data_layer", "security_module"],
            "output_files":  ["auth/auth.py", "auth/tokens.py"],
            "priority":      5,
            "layer":         "service",
        },
        "security_module": {
            "description":   "Encryption, input validation, secret management",
            "interfaces":    ["encrypt(data)", "decrypt(data)", "validate_input(data)"],
            "dependencies":  ["config_manager"],
            "output_files":  ["security/security.py", "security/validators.py"],
            "priority":      4,
            "layer":         "service",
        },
        "business_logic": {
            "description":   "Core domain business rules and workflows",
            "interfaces":    ["process(request)", "validate(entity)", "execute(action)"],
            "dependencies":  ["data_layer", "security_module"],
            "output_files":  ["business/logic.py", "business/rules.py"],
            "priority":      6,
            "layer":         "domain",
        },
        "knowledge_store": {
            "description":   "Persistent knowledge base, facts, and concepts",
            "interfaces":    ["store(entry)", "retrieve(query)", "search(terms)"],
            "dependencies":  ["data_layer"],
            "output_files":  ["knowledge/store.py", "knowledge/database.json"],
            "priority":      5,
            "layer":         "intelligence",
        },
        "memory_manager": {
            "description":   "Long-term and working memory management",
            "interfaces":    ["remember(key, value)", "recall(key)", "forget(key)"],
            "dependencies":  ["knowledge_store"],
            "output_files":  ["memory/manager.py", "memory/database.json"],
            "priority":      6,
            "layer":         "intelligence",
        },
        "research_engine": {
            "description":   "Pattern library consultation and concept extraction",
            "interfaces":    ["research(topic)", "retrieve_patterns()", "learn(data)"],
            "dependencies":  ["knowledge_store", "memory_manager"],
            "output_files":  ["research/engine.py", "research/knowledge_base.json"],
            "priority":      6,
            "layer":         "intelligence",
        },
        "ai_reasoning": {
            "description":   "Decision pipeline: analysis, assessment, recommendation",
            "interfaces":    ["analyse(context)", "recommend(options)", "decide(inputs)"],
            "dependencies":  ["research_engine", "memory_manager"],
            "output_files":  ["ai/reasoning.py", "ai/pipeline.py"],
            "priority":      7,
            "layer":         "intelligence",
        },
        "monitoring_module": {
            "description":   "Health checks, metrics collection, structured logging",
            "interfaces":    ["health_check()", "record_metric(name, value)", "log(level, msg)"],
            "dependencies":  ["config_manager"],
            "output_files":  ["monitoring/health_check.py", "monitoring/metrics.py"],
            "priority":      5,
            "layer":         "observability",
        },
        "integration_layer": {
            "description":   "External API client, webhook receiver, connector config",
            "interfaces":    ["call_api(endpoint, data)", "handle_webhook(payload)", "connect(service)"],
            "dependencies":  ["security_module", "config_manager"],
            "output_files":  ["integrations/api_client.py", "integrations/webhook_handler.py"],
            "priority":      7,
            "layer":         "integration",
        },
        "testing_framework": {
            "description":   "Unit, integration, and system test suite",
            "interfaces":    ["run_unit_tests()", "run_integration_tests()", "generate_report()"],
            "dependencies":  ["core_engine"],
            "output_files":  ["tests/unit/", "tests/integration/", "tests/run_tests.py"],
            "priority":      8,
            "layer":         "quality",
        },
        "documentation_system": {
            "description":   "Auto-generated documentation from code and specs",
            "interfaces":    ["generate_readme()", "generate_api_docs()", "generate_changelog()"],
            "dependencies":  ["core_engine"],
            "output_files":  ["README.md", "docs/"],
            "priority":      9,
            "layer":         "documentation",
        },
        "devops_pipeline": {
            "description":   "Dockerfile, CI/CD, Makefile, deployment packaging",
            "interfaces":    ["build()", "test()", "deploy()", "release()"],
            "dependencies":  ["testing_framework"],
            "output_files":  ["Dockerfile", ".github/workflows/", "Makefile"],
            "priority":      10,
            "layer":         "infrastructure",
        },
    }

    # Maps detected vision modules to catalogue entries
    _VISION_TO_CATALOGUE = {
        "ai_core":          ["ai_reasoning", "research_engine"],
        "memory":           ["memory_manager"],
        "knowledge_graph":  ["knowledge_store"],
        "security":         ["security_module"],
        "authentication":   ["auth_module"],
        "finance":          ["business_logic", "data_layer"],
        "business":         ["business_logic", "data_layer"],
        "research":         ["research_engine"],
        "creative_studio":  ["integration_layer"],
        "marketing":        ["integration_layer", "business_logic"],
        "analytics":        ["ai_reasoning"],
        "monitoring":       ["monitoring_module"],
        "deployment":       ["devops_pipeline"],
        "documentation":    ["documentation_system"],
        "testing":          ["testing_framework"],
        "api_layer":        ["api_layer"],
        "automation":       ["devops_pipeline", "business_logic"],
        "data_management":  ["data_layer"],
        "prediction":       ["ai_reasoning"],
        "mobile":           [],  # unsupported — no catalogue entry
        "desktop":          ["core_engine"],
        "web":              ["api_layer"],
    }

    # Modules always included regardless of vision spec
    _ALWAYS_INCLUDE = [
        "core_engine", "config_manager", "shared_memory",
        "data_layer", "monitoring_module", "documentation_system",
        "testing_framework", "devops_pipeline",
    ]

    # ------------------------------------------------------------------ #

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Module Detector AI] Connected to Shared Memory.")

    def start(self):
        print("[Module Detector AI] Architecture Module & Dependency Graph Engine Ready.")

    # ------------------------------------------------------------------ #
    # Detection                                                            #
    # ------------------------------------------------------------------ #

    def detect_modules(self, vision_spec: dict) -> dict:
        vision_modules = vision_spec.get("modules", [])

        # Resolve vision modules → catalogue modules
        selected = set(self._ALWAYS_INCLUDE)
        unsupported_vision_modules = []

        for vm in vision_modules:
            catalogue_entries = self._VISION_TO_CATALOGUE.get(vm, [])
            if catalogue_entries:
                selected.update(catalogue_entries)
            else:
                # No catalogue entry — module not yet buildable
                unsupported_vision_modules.append(vm)

        # Build module manifest
        manifest = {}
        for name in selected:
            if name in self.MODULE_CATALOGUE:
                manifest[name] = dict(self.MODULE_CATALOGUE[name])
                manifest[name]["status"] = "INCLUDED"

        # Build dependency graph
        dep_graph = self._build_dependency_graph(manifest)

        # Execution order (topological sort)
        execution_order = self._topological_sort(manifest)

        # Detect multi-repo need
        layers = {m["layer"] for m in manifest.values()}
        needs_multi_repo = len(layers) >= 5 and len(manifest) >= 10

        return {
            "detected_at":                  datetime.utcnow().isoformat(),
            "vision_modules_requested":     vision_modules,
            "catalogue_modules_selected":   list(selected),
            "unsupported_vision_modules":   unsupported_vision_modules,
            "module_manifest":              manifest,
            "dependency_graph":             dep_graph,
            "execution_order":              execution_order,
            "layer_breakdown":              self._layer_breakdown(manifest),
            "total_modules":                len(manifest),
            "total_output_files_expected":  self._count_output_files(manifest),
            "needs_multi_repo":             needs_multi_repo,
            "multi_repo_strategy":          self._multi_repo_strategy(manifest) if needs_multi_repo else None,
        }

    def _build_dependency_graph(self, manifest: dict) -> dict:
        graph = {}
        for name, meta in manifest.items():
            deps = [d for d in meta.get("dependencies", []) if d in manifest]
            graph[name] = {
                "depends_on":  deps,
                "required_by": [],
                "layer":       meta["layer"],
                "priority":    meta["priority"],
            }
        # Fill required_by
        for name, info in graph.items():
            for dep in info["depends_on"]:
                if dep in graph:
                    graph[dep]["required_by"].append(name)
        return graph

    def _topological_sort(self, manifest: dict) -> list:
        """Return modules in build order (dependencies first)."""
        visited  = set()
        order    = []

        def visit(name):
            if name in visited:
                return
            visited.add(name)
            for dep in manifest.get(name, {}).get("dependencies", []):
                if dep in manifest:
                    visit(dep)
            order.append(name)

        # Sort by priority first so equal-depth nodes are stable
        for name in sorted(manifest, key=lambda n: manifest[n].get("priority", 99)):
            visit(name)

        return order

    def _layer_breakdown(self, manifest: dict) -> dict:
        layers = {}
        for name, meta in manifest.items():
            layer = meta.get("layer", "unknown")
            layers.setdefault(layer, []).append(name)
        return layers

    def _count_output_files(self, manifest: dict) -> int:
        count = 0
        for meta in manifest.values():
            count += len(meta.get("output_files", []))
        return count

    def _multi_repo_strategy(self, manifest: dict) -> dict:
        layers = self._layer_breakdown(manifest)
        repos  = {}
        if "foundation" in layers:
            repos["nexus-core"]          = layers["foundation"]
        if "intelligence" in layers:
            repos["nexus-intelligence"]  = layers["intelligence"]
        if "service" in layers or "domain" in layers:
            repos["nexus-services"]      = layers.get("service", []) + layers.get("domain", [])
        if "observability" in layers or "integration" in layers:
            repos["nexus-platform"]      = layers.get("observability", []) + layers.get("integration", [])
        if "quality" in layers or "infrastructure" in layers or "documentation" in layers:
            repos["nexus-devops"]        = (
                layers.get("quality", []) +
                layers.get("infrastructure", []) +
                layers.get("documentation", [])
            )
        return {"repositories": repos, "dependency_tracking": "nexus-core must be built first"}

    # ------------------------------------------------------------------ #
    # Pipeline entry point                                                 #
    # ------------------------------------------------------------------ #

    def process_project_task(self, task_id: str):
        project_key = f"active_project_{task_id}"
        project     = self.memory.read(project_key)

        if project is None:
            print(f"[Module Detector AI] Project '{task_id}' not found.")
            return

        vision_spec = project.get("vision_spec", {})
        print(f"[Module Detector AI] Detecting modules for: {task_id}")

        module_data = self.detect_modules(vision_spec)

        project["modules"]  = module_data
        project["status"]   = "MODULES_DETECTED"

        self.memory.write(project_key, project)

        print(f"[Module Detector AI] Catalogue Modules  : {module_data['total_modules']}")
        print(f"[Module Detector AI] Execution Order    : {' → '.join(module_data['execution_order'][:6])}...")
        print(f"[Module Detector AI] Output Files (est) : {module_data['total_output_files_expected']}")
        print(f"[Module Detector AI] Multi-Repo Needed  : {module_data['needs_multi_repo']}")
        if module_data["unsupported_vision_modules"]:
            print(f"[Module Detector AI] Unsupported Vision Modules (will be noted):")
            for m in module_data["unsupported_vision_modules"]:
                print(f"  ✗ {m}")
        print(f"[Module Detector AI] Dependency graph built.")
