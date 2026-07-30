"""
NEXUS
Planner AI — Master Project Planning Engine

Module ID : PLANNER-001
Version   : 3.0.0

Responsibilities
----------------
• Divide projects into Phases → Milestones → Tasks → Subtasks
• Estimate development effort (person-hours) per task
• Estimate calendar time (days/weeks) per phase
• Assess risk per phase
• Define dependencies between phases and tasks
• Assign priority scores
• Support simple goals AND large vision documents equally
• Incorporate Research AI complexity and Module Detector module count
"""

from datetime import datetime


class PlannerAI:
    """
    Master Project Planning Engine.

    Generates a fully phased execution plan with milestones,
    tasks, subtasks, effort estimates, risks, and dependencies.
    """

    # ------------------------------------------------------------------ #
    # Phase templates                                                      #
    # ------------------------------------------------------------------ #

    # Core 21-stage pipeline phases — always included
    _PIPELINE_PHASES = [
        {
            "phase":        0,
            "name":         "Vision & Requirements",
            "worker":       "VISION-001 + ASSESS-001",
            "milestone":    "Structured specification and capability gap report produced",
            "tasks": [
                {"task": "Parse vision document or goal",          "subtasks": ["Detect document type", "Extract requirements", "Structure specification"], "effort_h": 0.1},
                {"task": "Assess builder capabilities",            "subtasks": ["Classify features", "Identify gaps", "Calculate feasibility score"],       "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     1,
            "depends_on":   [],
        },
        {
            "phase":        1,
            "name":         "Intelligence Research",
            "worker":       "RESEARCH-001",
            "milestone":    "Project type confirmed, knowledge base consulted, patterns retrieved",
            "tasks": [
                {"task": "Analyse goal semantics",                 "subtasks": ["Extract concepts", "Classify project type", "Detect complexity"],          "effort_h": 0.2},
                {"task": "Consult knowledge base",                 "subtasks": ["Check existing patterns", "Retrieve relevant research"],                    "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     2,
            "depends_on":   [0],
        },
        {
            "phase":        2,
            "name":         "Module Detection & Dependency Graph",
            "worker":       "MODULE-001",
            "milestone":    "All required modules identified, dependency order confirmed",
            "tasks": [
                {"task": "Detect required modules",                "subtasks": ["Map vision modules to catalogue", "Identify unsupported modules"],          "effort_h": 0.2},
                {"task": "Build dependency graph",                 "subtasks": ["Map inter-module dependencies", "Compute execution order"],                 "effort_h": 0.1},
                {"task": "Assess multi-repo need",                 "subtasks": ["Count layers", "Define repository split if needed"],                       "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     3,
            "depends_on":   [0, 1],
        },
        {
            "phase":        3,
            "name":         "System Architecture Design",
            "worker":       "ARCHITECT-001",
            "milestone":    "Nine-layer architecture designed with full reasoning",
            "tasks": [
                {"task": "Define overall architecture pattern",    "subtasks": ["Select framework", "Choose language", "Choose database"],                   "effort_h": 0.5},
                {"task": "Design module architecture",             "subtasks": ["Map module layers", "Define interfaces"],                                   "effort_h": 0.3},
                {"task": "Design security architecture",           "subtasks": ["Threat model", "Auth strategy", "Data protection"],                        "effort_h": 0.3},
                {"task": "Design deployment architecture",         "subtasks": ["Environment plan", "CI/CD strategy", "Scaling plan"],                      "effort_h": 0.2},
                {"task": "Design API architecture",                "subtasks": ["Endpoint strategy", "Versioning", "Contract definitions"],                  "effort_h": 0.3},
            ],
            "risk":         "MEDIUM",
            "priority":     4,
            "depends_on":   [1, 2],
        },
        {
            "phase":        4,
            "name":         "Database Schema Design",
            "worker":       "DATABASE-001",
            "milestone":    "SQL schema and Python data access layer generated",
            "tasks": [
                {"task": "Design entity-relationship model",       "subtasks": ["Identify entities", "Define relationships", "Plan indexes"],                "effort_h": 0.5},
                {"task": "Generate DDL schema",                    "subtasks": ["Write CREATE TABLE statements", "Add foreign keys", "Add indexes"],         "effort_h": 0.3},
                {"task": "Generate data access layer",             "subtasks": ["Write Python sqlite3 helper", "Add CRUD operations"],                      "effort_h": 0.3},
            ],
            "risk":         "LOW",
            "priority":     5,
            "depends_on":   [3],
        },
        {
            "phase":        5,
            "name":         "Source Code Generation",
            "worker":       "CODER-001",
            "milestone":    "Complete, runnable source code generated for detected project type",
            "tasks": [
                {"task": "Select project template",                "subtasks": ["Detect type from goal/research", "Load template"],                          "effort_h": 0.1},
                {"task": "Generate application code",              "subtasks": ["Populate template", "Wire dependencies", "Add error handling"],             "effort_h": 1.0},
                {"task": "Generate requirements file",             "subtasks": ["List project dependencies", "Pin versions"],                                "effort_h": 0.1},
            ],
            "risk":         "MEDIUM",
            "priority":     6,
            "depends_on":   [3, 4],
        },
        {
            "phase":        6,
            "name":         "UI/UX Design",
            "worker":       "DESIGN-001",
            "milestone":    "Colour palette, layout spec, and production CSS generated",
            "tasks": [
                {"task": "Define colour palette",                  "subtasks": ["Primary/secondary/accent colours", "Dark/light mode strategy"],             "effort_h": 0.2},
                {"task": "Define layout specification",            "subtasks": ["Navigation structure", "Grid system", "Responsive breakpoints"],            "effort_h": 0.2},
                {"task": "Generate production CSS",                "subtasks": ["Variables", "Utility classes", "Component styles"],                         "effort_h": 0.3},
            ],
            "risk":         "LOW",
            "priority":     6,
            "depends_on":   [3],
        },
        {
            "phase":        7,
            "name":         "Static Code Review",
            "worker":       "REVIEWER-001",
            "milestone":    "Code quality gate passed, quality score ≥ 70",
            "tasks": [
                {"task": "AST static analysis",                    "subtasks": ["Parse source tree", "Check naming", "Check structure"],                     "effort_h": 0.2},
                {"task": "Quality scoring",                        "subtasks": ["Calculate score", "List issues", "Make approval decision"],                 "effort_h": 0.1},
            ],
            "risk":         "MEDIUM",
            "priority":     7,
            "depends_on":   [5],
        },
        {
            "phase":        8,
            "name":         "Runtime Validation & Testing",
            "worker":       "TESTER-001",
            "milestone":    "Code executes in sandbox without errors; test suite generated",
            "tasks": [
                {"task": "Sandboxed runtime execution",            "subtasks": ["Execute in isolated namespace", "Verify callable functions"],               "effort_h": 0.2},
                {"task": "Generate test files",                    "subtasks": ["Unit tests per function", "Integration test outline"],                      "effort_h": 0.5},
                {"task": "Coverage estimation",                    "subtasks": ["Count statements", "Estimate coverage %"],                                  "effort_h": 0.1},
            ],
            "risk":         "HIGH",
            "priority":     8,
            "depends_on":   [7],
        },
        {
            "phase":        9,
            "name":         "Security Analysis",
            "worker":       "SECURITY-001",
            "milestone":    "Security scan passed, risk level LOW or MEDIUM",
            "tasks": [
                {"task": "Vulnerability scanning",                 "subtasks": ["Check hardcoded secrets", "Check SQL injection", "Check eval/exec"],        "effort_h": 0.2},
                {"task": "Security scoring",                       "subtasks": ["Calculate score", "Classify risk level", "Approve/block"],                  "effort_h": 0.1},
            ],
            "risk":         "HIGH",
            "priority":     9,
            "depends_on":   [8],
        },
        {
            "phase":        10,
            "name":         "Performance Profiling",
            "worker":       "PERFORMANCE-001",
            "milestone":    "Performance grade B or better, bottlenecks documented",
            "tasks": [
                {"task": "Benchmark all functions",                "subtasks": ["Time each callable", "Skip stdin-blocked functions"],                       "effort_h": 0.2},
                {"task": "Cyclomatic complexity analysis",         "subtasks": ["Count branches", "Flag high-complexity functions"],                         "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     10,
            "depends_on":   [9],
        },
        {
            "phase":        11,
            "name":         "Technical Documentation",
            "worker":       "DOCS-001",
            "milestone":    "README, API docs, Architecture docs, CHANGELOG, CONTRIBUTING generated",
            "tasks": [
                {"task": "Generate README.md",                     "subtasks": ["Overview", "Installation", "Usage", "API reference"],                      "effort_h": 0.3},
                {"task": "Generate API documentation",             "subtasks": ["Endpoint docs", "Request/response examples"],                               "effort_h": 0.3},
                {"task": "Generate architecture documentation",    "subtasks": ["Module diagram", "Decision log", "Trade-offs"],                             "effort_h": 0.3},
                {"task": "Generate CHANGELOG and CONTRIBUTING",    "subtasks": ["Version history format", "Contribution guidelines"],                        "effort_h": 0.2},
            ],
            "risk":         "LOW",
            "priority":     11,
            "depends_on":   [5, 9],
        },
        {
            "phase":        12,
            "name":         "Observability Setup",
            "worker":       "MONITOR-001",
            "milestone":    "Health check, metrics, logger, and alerts configured",
            "tasks": [
                {"task": "Health check endpoint",                  "subtasks": ["Status check", "Dependency check", "Response format"],                     "effort_h": 0.2},
                {"task": "Metrics collection config",              "subtasks": ["Counter definitions", "Gauge definitions", "Histogram definitions"],        "effort_h": 0.2},
                {"task": "Structured logger config",               "subtasks": ["Log levels", "JSON format", "Rotation policy"],                            "effort_h": 0.1},
                {"task": "Alerts configuration",                   "subtasks": ["Threshold definitions", "Notification channels"],                           "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     12,
            "depends_on":   [5],
        },
        {
            "phase":        13,
            "name":         "Integration Layer",
            "worker":       "INTEGRATION-001",
            "milestone":    "API client, webhook handler, and integration config generated",
            "tasks": [
                {"task": "Generate API client",                    "subtasks": ["HTTP client with retries", "Auth headers", "Error handling"],               "effort_h": 0.3},
                {"task": "Generate webhook handler",               "subtasks": ["HMAC verification", "Payload routing", "Response format"],                  "effort_h": 0.3},
                {"task": "Generate integration config",            "subtasks": ["Service endpoints", "Auth tokens placeholders", "Timeout config"],          "effort_h": 0.1},
            ],
            "risk":         "MEDIUM",
            "priority":     13,
            "depends_on":   [9],
        },
        {
            "phase":        14,
            "name":         "DevOps & Infrastructure",
            "worker":       "DEVOPS-001",
            "milestone":    "Dockerfile, CI/CD pipeline, and Makefile generated",
            "tasks": [
                {"task": "Generate Dockerfile",                    "subtasks": ["Base image", "Dependency install", "Entry point"],                          "effort_h": 0.3},
                {"task": "Generate CI/CD pipeline",                "subtasks": ["Test stage", "Build stage", "Deploy stage"],                                "effort_h": 0.3},
                {"task": "Generate Makefile",                      "subtasks": ["Build target", "Test target", "Run target", "Clean target"],                "effort_h": 0.2},
            ],
            "risk":         "LOW",
            "priority":     14,
            "depends_on":   [8, 11],
        },
        {
            "phase":        15,
            "name":         "Deployment Packaging",
            "worker":       "DEPLOY-001",
            "milestone":    "Release archive, requirements.txt, deployment.json written to deployment folder",
            "tasks": [
                {"task": "Package release artifacts",              "subtasks": ["Copy source", "Write requirements.txt", "Write deployment.json"],           "effort_h": 0.2},
                {"task": "Generate release archive",               "subtasks": ["Create .tar.gz", "Verify contents"],                                       "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     15,
            "depends_on":   [14],
        },
        {
            "phase":        16,
            "name":         "Verification",
            "worker":       "VERIFY-001",
            "milestone":    "All checks pass; pipeline verified honest",
            "tasks": [
                {"task": "Verify capabilities vs claims",          "subtasks": ["Check unsupported features documented", "Check no false successes"],        "effort_h": 0.1},
                {"task": "Verify all artifacts exist on disk",     "subtasks": ["Check core files", "Check stage files"],                                   "effort_h": 0.1},
                {"task": "Verify tests ran",                       "subtasks": ["Check test results", "Check coverage"],                                    "effort_h": 0.1},
                {"task": "Verify architecture completeness",       "subtasks": ["Check all 9 layers present", "Check module manifest"],                     "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     16,
            "depends_on":   [15],
        },
        {
            "phase":        17,
            "name":         "Progress Reporting",
            "worker":       "PROGRESS-001",
            "milestone":    "Honest completion report with feature classification delivered",
            "tasks": [
                {"task": "Calculate stage completion percentages", "subtasks": ["Weight each stage", "Sum weighted completion"],                             "effort_h": 0.1},
                {"task": "Classify all features",                  "subtasks": ["Implemented", "Planned", "Partial", "Unsupported"],                        "effort_h": 0.1},
                {"task": "Generate recommendations",               "subtasks": ["Risk assessment", "Next priorities"],                                      "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     17,
            "depends_on":   [16],
        },
        {
            "phase":        18,
            "name":         "Knowledge Preservation",
            "worker":       "MEMORY-001",
            "milestone":    "Project outcome stored in persistent knowledge graph",
            "tasks": [
                {"task": "Extract project patterns",               "subtasks": ["Technology patterns", "Quality patterns", "Risk patterns"],                 "effort_h": 0.1},
                {"task": "Update knowledge graph",                 "subtasks": ["Store project record", "Link related concepts"],                            "effort_h": 0.1},
            ],
            "risk":         "LOW",
            "priority":     18,
            "depends_on":   [17],
        },
    ]

    # ------------------------------------------------------------------ #

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Planner AI] Connected to Shared Memory.")

    def start(self):
        print("[Planner AI] Master Project Planning Engine Ready.")

    # ------------------------------------------------------------------ #
    # Planning                                                             #
    # ------------------------------------------------------------------ #

    def _estimate_hours(self, research: dict, modules_data: dict, vision_spec: dict) -> float:
        base_hours = sum(
            task["effort_h"]
            for phase in self._PIPELINE_PHASES
            for task in phase["tasks"]
        )

        # Adjust for complexity from research
        complexity = research.get("complexity", vision_spec.get("complexity", "MEDIUM"))
        multiplier = {"LOW": 0.8, "MEDIUM": 1.0, "HIGH": 1.5, "ENTERPRISE": 2.5}.get(complexity, 1.0)

        # Adjust for module count
        module_count = modules_data.get("total_modules", 3)
        module_multiplier = 1.0 + (module_count / 20)

        return round(base_hours * multiplier * module_multiplier, 1)

    def _estimate_calendar_days(self, total_hours: float) -> dict:
        """Estimate calendar time at 4 productive hours/day for a solo developer."""
        days = total_hours / 4
        return {
            "optimistic_days":  round(days * 0.7, 1),
            "realistic_days":   round(days, 1),
            "conservative_days":round(days * 1.5, 1),
        }

    def _build_risk_summary(self, vision_spec: dict, cap_report: dict) -> list:
        risks = []
        unsupported = cap_report.get("unsupported", {})
        if unsupported:
            risks.append({
                "risk":        "Unsupported features",
                "severity":    "HIGH",
                "description": f"{len(unsupported)} requested capabilities cannot be built yet",
                "mitigation":  "Document as planned features; deliver what is buildable first",
            })
        complexity = vision_spec.get("complexity", "MEDIUM")
        if complexity in ("HIGH", "ENTERPRISE"):
            risks.append({
                "risk":        "High complexity",
                "severity":    "MEDIUM",
                "description": f"Project complexity rated {complexity}",
                "mitigation":  "Deliver incrementally phase by phase; validate each milestone",
            })
        risks.append({
            "risk":        "Scope creep",
            "severity":    "MEDIUM",
            "description": "Vision documents often expand during implementation",
            "mitigation":  "Freeze scope at vision parse stage; new requirements go in next version",
        })
        return risks

    def process_project_task(self, task_id: str):
        project_key = f"active_project_{task_id}"
        project     = self.memory.read(project_key)

        if project is None:
            print(f"[Planner AI] Project '{task_id}' not found.")
            return

        research    = project.get("research",   {})
        modules_data = project.get("modules",   {})
        vision_spec  = project.get("vision_spec", {})
        cap_report   = project.get("capability_report", {})

        print(f"[Planner AI] Building execution plan: {task_id}")

        total_hours    = self._estimate_hours(research, modules_data, vision_spec)
        calendar       = self._estimate_calendar_days(total_hours)
        risks          = self._build_risk_summary(vision_spec, cap_report)
        goal           = project.get("goal", "")
        project_type   = research.get("project_type", "generic")
        complexity     = research.get("complexity", vision_spec.get("complexity", "MEDIUM"))
        features       = vision_spec.get("features", []) or vision_spec.get("functional_requirements", [])

        # ── NEXUS AI: generate goal-specific plan ───────────────── #
        ai_phases = None
        try:
            from core.nexus_ai import NexusAI
            nexus    = NexusAI(self.memory)
            ai_raw   = nexus.generate_plan(goal, project_type, features, complexity)
            ai_plan  = nexus.parse_json(ai_raw)
            if ai_plan.get("phases") and len(ai_plan["phases"]) >= 3:
                ai_phases    = ai_plan["phases"]
                total_hours  = ai_plan.get("estimated_total_hours", total_hours)
                calendar     = ai_plan.get("calendar_estimate",     calendar)
                risks        = ai_plan.get("risks",                 risks) or risks
                print(f"[Planner AI] Provider   : {nexus._provider_instance().name()}")
        except Exception as _exc:
            print(f"[Planner AI] AI planning skipped ({_exc}), using template.")

        phases     = ai_phases or self._PIPELINE_PHASES
        use_ai     = ai_phases is not None

        plan = {
            "generated_at":            datetime.utcnow().isoformat(),
            "total_phases":            len(phases),
            "phases":                  phases,
            "estimated_total_hours":   total_hours,
            "calendar_estimate":       calendar,
            "execution_strategy":      "SEQUENTIAL_WITH_GATES",
            "complexity":              complexity,
            "risks":                   risks,
            "total_tasks":             sum(len(p.get("tasks", [])) for p in phases),
            "total_subtasks":          sum(
                                           len(st)
                                           for p in (self._PIPELINE_PHASES if not use_ai else [])
                                           for t in p.get("tasks", [])
                                           for st in [t.get("subtasks", [])]
                                       ),
        }

        project["plan"]   = plan
        project["status"] = "PROJECT_PLANNED"

        self.memory.write(project_key, project)

        print(f"[Planner AI] Phases        : {plan['total_phases']}")
        print(f"[Planner AI] Tasks         : {plan['total_tasks']}")
        print(f"[Planner AI] Subtasks      : {plan['total_subtasks']}")
        print(f"[Planner AI] Est. Hours    : {total_hours}")
        print(f"[Planner AI] Calendar      : {calendar['realistic_days']} days (realistic)")
        print(f"[Planner AI] Risks         : {len(risks)}")
        print(f"[Planner AI] Strategy      : {plan['execution_strategy']}")
