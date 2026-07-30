"""
NEXUS
Progress Tracker AI — Build Completion & Gap Reporting Engine

Module ID : PROGRESS-001
Version   : 1.0.0

Responsibilities
----------------
• Calculate overall pipeline completion percentage
• Calculate per-module completion percentages
• List remaining work for each module
• Report known limitations honestly
• Identify risks and provide recommendations
• Define next development priorities
• Distinguish: Implemented | Planned | Partial | Unsupported
"""

from datetime import datetime


class ProgressTrackerAI:
    """
    Build Completion and Gap Reporting Engine.

    Aggregates signals from all pipeline stages and produces
    an honest, comprehensive progress report.
    """

    # ------------------------------------------------------------------ #
    # Stage completion weights                                             #
    # ------------------------------------------------------------------ #

    _STAGE_WEIGHTS = {
        "vision_spec":          ("Vision Parsing",          3),
        "capability_report":    ("Capability Assessment",   5),
        "research":             ("Research Intelligence",   4),
        "modules":              ("Module Detection",        5),
        "plan":                 ("Project Planning",        5),
        "architecture":         ("System Architecture",     8),
        "database":             ("Database Schema",         5),
        "code":                 ("Source Code Generation",  15),
        "design":               ("UI/UX Design",            4),
        "review":               ("Code Review",             6),
        "tests":                ("Runtime Testing",         8),
        "security":             ("Security Analysis",       8),
        "performance":          ("Performance Profiling",   5),
        "documentation":        ("Technical Documentation", 6),
        "monitoring":           ("Observability Setup",     4),
        "integration":          ("Integration Layer",       4),
        "devops":               ("DevOps & Infrastructure", 5),
        "deployment":           ("Deployment Packaging",    5),
        "verification":         ("Verification",            5),
    }  # Weights sum to 110; normalize to 100

    # ------------------------------------------------------------------ #

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Progress Tracker AI] Connected to Shared Memory.")

    def start(self):
        print("[Progress Tracker AI] Build Completion & Gap Reporting Engine Ready.")

    # ------------------------------------------------------------------ #
    # Progress calculation                                                 #
    # ------------------------------------------------------------------ #

    def _stage_completion(self, project: dict, key: str) -> float:
        """Return 0.0–1.0 for how complete a stage appears to be."""
        data = project.get(key)
        if data is None:
            return 0.0

        # Fine-grained checks per stage
        if key == "code":
            source = data.get("source", "")
            return 1.0 if len(source) > 50 else 0.3

        if key == "tests":
            return 1.0 if data.get("passed") else 0.5

        if key == "review":
            return 1.0 if data.get("approved") else 0.6

        if key == "security":
            return 1.0 if data.get("approved") else 0.7

        if key == "verification":
            return 1.0 if data.get("verification_passed") else 0.4

        if key == "documentation":
            files = data.get("files_written", [])
            return min(len(files) / 5.0, 1.0)

        if key == "architecture":
            return 1.0 if data.get("modules") else 0.5

        if key == "modules":
            return 1.0 if data.get("module_manifest") else 0.3

        if key == "capability_report":
            return 1.0 if "feasibility_score" in data else 0.0

        if key == "vision_spec":
            return 1.0 if data.get("document_type") else 0.0

        # Generic: if the key exists and is non-empty, it ran
        if isinstance(data, dict) and data:
            return 1.0
        return 0.5

    def calculate_progress(self, project: dict) -> dict:
        stage_results = {}
        total_weight  = 0
        weighted_done = 0.0

        for key, (label, weight) in self._STAGE_WEIGHTS.items():
            completion = self._stage_completion(project, key)
            stage_results[key] = {
                "label":       label,
                "weight":      weight,
                "completion":  round(completion * 100, 1),
                "status":      self._completion_to_status(completion),
            }
            total_weight  += weight
            weighted_done += completion * weight

        # Pipeline Execution: did the builder stages run?
        pipeline_execution_pct = round((weighted_done / total_weight) * 100, 1)

        # Vision Coverage: what fraction of requested capabilities can be built?
        # Comes from Capability Assessor — this is the honest buildability metric.
        cap_report      = project.get("capability_report", {})
        vision_coverage = cap_report.get("feasibility_score", None)  # set by ASSESS-001

        return stage_results, pipeline_execution_pct, vision_coverage

    def _completion_to_status(self, pct: float) -> str:
        if pct >= 1.0:
            return "COMPLETE"
        if pct >= 0.5:
            return "PARTIAL"
        if pct > 0.0:
            return "STARTED"
        return "NOT_STARTED"

    def _build_remaining_work(self, stage_results: dict, project: dict) -> list:
        remaining = []
        for key, info in stage_results.items():
            if info["status"] != "COMPLETE":
                remaining.append({
                    "stage":      info["label"],
                    "completion": info["completion"],
                    "status":     info["status"],
                })
        return remaining

    def _build_limitations(self, project: dict) -> list:
        cap_report   = project.get("capability_report", {})
        unsupported  = cap_report.get("unsupported", {})
        partially    = cap_report.get("partially_supported", {})
        limitations  = []

        for cap, desc in unsupported.items():
            limitations.append({
                "category":    "UNSUPPORTED",
                "capability":  cap,
                "description": desc,
                "status":      "Not buildable in current version",
            })

        for cap, info in partially.items():
            limitations.append({
                "category":    "PARTIALLY_SUPPORTED",
                "capability":  cap,
                "description": info["description"],
                "completion":  info["completion_pct"],
                "status":      f"~{info['completion_pct']}% implemented",
            })

        return limitations

    def _build_recommendations(self, project: dict, overall_pct: float) -> list:
        recs = []
        cap_report = project.get("capability_report", {})
        unsup_count = len(cap_report.get("unsupported", {}))

        if overall_pct < 60:
            recs.append("Pipeline completion is below 60% — review failed stages before deployment.")
        if unsup_count > 5:
            recs.append(f"{unsup_count} features are unsupported — consider breaking the vision into smaller phases.")
        if not project.get("tests", {}).get("passed"):
            recs.append("Runtime tests failed — fix code issues before marking project complete.")
        if not project.get("security", {}).get("approved"):
            recs.append("Security scan not fully approved — review findings before release.")
        if not project.get("verification", {}).get("verification_passed"):
            recs.append("Verification check did not pass — resolve critical issues listed above.")

        # Next priorities
        modules_data = project.get("modules", {})
        unsup_vision = modules_data.get("unsupported_vision_modules", [])
        if unsup_vision:
            recs.append(
                f"Next development priority: implement builders for: "
                f"{', '.join(unsup_vision[:5])}"
            )

        if not recs:
            recs.append("All pipeline stages completed successfully. Project is ready for handover.")

        return recs

    def _classify_features(self, project: dict) -> dict:
        cap_report   = project.get("capability_report", {})
        verification = project.get("verification", {})

        verification_passed = verification.get("verification_passed", False)

        return {
            "implemented":  list(cap_report.get("fully_supported", {}).keys()) if verification_passed else [],
            "planned":      list(cap_report.get("unsupported", {}).keys()),
            "partial":      list(cap_report.get("partially_supported", {}).keys()),
            "unsupported":  list(cap_report.get("unsupported", {}).keys()),
        }

    # ------------------------------------------------------------------ #
    # Pipeline entry point                                                 #
    # ------------------------------------------------------------------ #

    def process_project_task(self, task_id: str):
        project_key = f"active_project_{task_id}"
        project     = self.memory.read(project_key)

        if project is None:
            print(f"[Progress Tracker AI] Project '{task_id}' not found.")
            return

        print(f"[Progress Tracker AI] Calculating progress: {task_id}")

        stage_results, pipeline_execution_pct, vision_coverage_pct = self.calculate_progress(project)
        remaining       = self._build_remaining_work(stage_results, project)
        limitations     = self._build_limitations(project)
        recommendations = self._build_recommendations(project, pipeline_execution_pct)
        feature_map     = self._classify_features(project)

        report = {
            "tracked_at":             datetime.utcnow().isoformat(),
            # ── Unambiguous metrics ──────────────────────────────────────
            # pipeline_execution_pct : did each builder stage run?
            #   100% = all 19 pipeline stages completed.
            #   Says nothing about whether the requested features are built.
            "pipeline_execution_pct": pipeline_execution_pct,
            # vision_coverage_pct : of the features requested in the goal/vision,
            #   what fraction can actually be built by NEXUS right now?
            #   Comes directly from Capability Assessor (ASSESS-001).
            "vision_coverage_pct":    vision_coverage_pct,
            # ── Legacy key kept for backward compat ─────────────────────
            "overall_completion_pct": pipeline_execution_pct,
            # ── Stage details ────────────────────────────────────────────
            "stage_results":          stage_results,
            "remaining_work":         remaining,
            "known_limitations":      limitations,
            "recommendations":        recommendations,
            "feature_classification": feature_map,
            "implemented_count":      len(feature_map["implemented"]),
            "planned_count":          len(feature_map["planned"]),
            "partial_count":          len(feature_map["partial"]),
            "unsupported_count":      len(feature_map["unsupported"]),
        }

        project["progress_report"] = report
        project["status"]          = "PROGRESS_TRACKED"

        self.memory.write(project_key, project)

        stages_done = sum(1 for s in stage_results.values() if s['status'] == 'COMPLETE')
        print(f"[Progress Tracker AI] Pipeline Execution : {pipeline_execution_pct}%  "
              f"(stages completed: {stages_done}/{len(stage_results)})")
        if vision_coverage_pct is not None:
            print(f"[Progress Tracker AI] Vision Coverage    : {vision_coverage_pct}%  "
                  f"(requested capabilities buildable now)")
        print(f"[Progress Tracker AI] Limitations        : {len(limitations)}")
        print(f"[Progress Tracker AI] Recommendations    : {len(recommendations)}")
        print(f"\n[Progress Tracker AI] Per-Stage Breakdown:")
        for key, info in stage_results.items():
            bar_filled = int(info["completion"] / 10)
            bar        = "█" * bar_filled + "░" * (10 - bar_filled)
            print(f"  {info['label']:35s} [{bar}] {info['completion']:5.1f}% — {info['status']}")
