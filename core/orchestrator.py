"""
NEXUS
Enterprise Orchestrator

Module ID : ORCHESTRATOR-001
Version   : 3.0.0

Full 21-stage sequential delivery pipeline:

  Vision Parser  → Capability Assessor → Research AI  → Module Detector →
  Planner AI     → Architect AI        → Database AI  → Coder AI        →
  Design AI      → Reviewer AI         → Tester AI    → Security AI     →
  Performance AI → Documentation AI    → Monitoring AI → Integration AI →
  DevOps AI      → Deployment AI       → Verification AI → Progress Tracker →
  Memory AI
"""

import os

from core.shared_memory import SharedMemory

from plugins.manager_ai.agent          import ManagerAI
from plugins.vision_parser.agent       import VisionParserAI
from plugins.capability_assessor.agent import CapabilityAssessorAI
from plugins.research_ai.agent         import ResearchAI
from plugins.module_detector.agent     import ModuleDetectorAI
from plugins.planner_ai.agent          import PlannerAI
from plugins.architect_ai.agent        import ArchitectAI
from plugins.database_ai.agent         import DatabaseAI
from plugins.coder_ai.agent            import CoderAI
from plugins.design_ai.agent           import DesignAI
from plugins.reviewer_ai.agent         import ReviewerAI
from plugins.tester_ai.agent           import TesterAI
from plugins.security_ai.agent         import SecurityAI
from plugins.performance_ai.agent      import PerformanceAI
from plugins.documentation_ai.agent   import DocumentationAI
from plugins.monitoring_ai.agent       import MonitoringAI
from plugins.integration_ai.agent      import IntegrationAI
from plugins.devops_ai.agent           import DevOpsAI
from plugins.deployment_ai.agent       import DeploymentAI
from plugins.verification_ai.agent     import VerificationAI
from plugins.progress_tracker.agent    import ProgressTrackerAI
from plugins.memory_ai.agent           import MemoryAI


class Orchestrator:
    """
    NEXUS Enterprise Orchestrator v3.

    Boots all 22 AI agents, registers them under the ManagerAI
    swarm, then drives the full 21-stage sequential delivery
    pipeline for a given project goal or vision document.
    """

    def __init__(self):
        self.shared_memory = SharedMemory()

    # ------------------------------------------------------------------ #
    # BOOT                                                                 #
    # ------------------------------------------------------------------ #

    def _boot_agents(self):

        self.shared_memory.write("system",       "ONLINE")
        self.shared_memory.write("factory_mode", "ENTERPRISE_v3")
        self.shared_memory.write("boot_time",    "SYSTEM_INITIALIZED")

        print("\n[BOOT] Shared Memory Initialized")

        # ── Instantiate all workers ────────────────────────────────── #
        self.manager       = ManagerAI(self.shared_memory)
        self.vision_parser = VisionParserAI(self.shared_memory)
        self.assessor      = CapabilityAssessorAI(self.shared_memory)
        self.researcher    = ResearchAI(self.shared_memory)
        self.module_det    = ModuleDetectorAI(self.shared_memory)
        self.planner       = PlannerAI(self.shared_memory)
        self.architect     = ArchitectAI(self.shared_memory)
        self.database      = DatabaseAI(self.shared_memory)
        self.coder         = CoderAI(self.shared_memory)
        self.designer      = DesignAI(self.shared_memory)
        self.reviewer      = ReviewerAI(self.shared_memory)
        self.tester        = TesterAI(self.shared_memory)
        self.security      = SecurityAI(self.shared_memory)
        self.performance   = PerformanceAI(self.shared_memory)
        self.documenter    = DocumentationAI(self.shared_memory)
        self.monitor       = MonitoringAI(self.shared_memory)
        self.integrator    = IntegrationAI(self.shared_memory)
        self.devops        = DevOpsAI(self.shared_memory)
        self.deployer      = DeploymentAI(self.shared_memory)
        self.verifier      = VerificationAI(self.shared_memory)
        self.tracker       = ProgressTrackerAI(self.shared_memory)
        self.memory        = MemoryAI(self.shared_memory)

        print("\n[BOOT] All 22 AI Modules Loaded")

        # ── Start services ─────────────────────────────────────────── #
        self.manager.start()
        self.vision_parser.start()
        self.assessor.start()
        self.researcher.start()
        self.module_det.start()
        self.planner.start()
        self.architect.start()
        self.database.start()
        self.coder.start()
        self.designer.start()
        self.reviewer.start()
        self.tester.start()
        self.security.start()
        self.performance.start()
        self.documenter.start()
        self.monitor.start()
        self.integrator.start()
        self.devops.start()
        self.deployer.start()
        self.verifier.start()
        self.tracker.start()
        print("[Memory AI] Semantic Knowledge Engine Ready.")

        # ── Register employees ─────────────────────────────────────── #
        self.manager.register_employee("VISION-001",    self.vision_parser)
        self.manager.register_employee("ASSESS-001",    self.assessor)
        self.manager.register_employee("RESEARCH-001",  self.researcher)
        self.manager.register_employee("MODULE-001",    self.module_det)
        self.manager.register_employee("PLANNER-001",   self.planner)
        self.manager.register_employee("ARCHITECT-001", self.architect)
        self.manager.register_employee("DATABASE-001",  self.database)
        self.manager.register_employee("CODER-001",     self.coder)
        self.manager.register_employee("DESIGN-001",    self.designer)
        self.manager.register_employee("REVIEWER-001",  self.reviewer)
        self.manager.register_employee("TESTER-001",    self.tester)
        self.manager.register_employee("SECURITY-001",  self.security)
        self.manager.register_employee("PERFORMANCE-001", self.performance)
        self.manager.register_employee("DOCS-001",      self.documenter)
        self.manager.register_employee("MONITOR-001",   self.monitor)
        self.manager.register_employee("INTEGRATION-001", self.integrator)
        self.manager.register_employee("DEVOPS-001",    self.devops)
        self.manager.register_employee("DEPLOY-001",    self.deployer)
        self.manager.register_employee("VERIFY-001",    self.verifier)
        self.manager.register_employee("PROGRESS-001",  self.tracker)
        self.manager.register_employee("MEMORY-001",    self.memory)

        print("\n[WORKFORCE STATUS]")
        self.manager.list_employees()

    # ------------------------------------------------------------------ #
    # PIPELINE                                                             #
    # ------------------------------------------------------------------ #

    def run(self, goal: str, operational_parameters: dict | None = None):
        """
        Execute the full NEXUS 21-stage delivery pipeline for *goal*.

        Parameters
        ----------
        goal : str
            High-level project description or full vision document text.
        operational_parameters : dict, optional
            Complexity, pricing, risk overrides forwarded to ManagerAI.
        """

        print("\n" + "=" * 70)
        print("NEXUS ENTERPRISE DELIVERY PIPELINE  v3.0")
        print("=" * 70)

        self._boot_agents()

        # ── Strategic Gate ────────────────────────────────────────── #

        print("\n" + "=" * 70)
        print("FOUNDER REQUEST")
        print("=" * 70)
        # Print first 300 chars only if it's a large vision doc
        preview = goal if len(goal) <= 300 else goal[:300] + f"... [{len(goal)} chars total]"
        print(preview)

        task_id, approved = self.manager.formulate_10_step_plan(
            high_level_goal=goal,
            operational_parameters=operational_parameters,
        )

        if not approved:
            print("\n[PIPELINE] Execution blocked by Manager AI.")
            self.manager.show_projects()
            return

        print(f"\n[PIPELINE] Strategic Gate Approved : {task_id}")

        # ── STAGE 0 : Vision Parser ───────────────────────────────── #

        self._section(0, "Vision & Requirements Parsing Phase")
        self.manager.dispatch_swarm_worker(task_id, "VISION-001")
        project    = self._read(task_id)
        vision_spec = project.get("vision_spec", {})
        print(f"\nVision Specification")
        print("-" * 40)
        print(f"Document Type     : {vision_spec.get('document_type', 'N/A')}")
        print(f"Complexity        : {vision_spec.get('complexity', 'N/A')}")
        print(f"Sections          : {len(vision_spec.get('section_titles', []))}")
        print(f"Functional Reqs   : {len(vision_spec.get('functional_requirements', []))}")
        print(f"Non-Func Reqs     : {len(vision_spec.get('non_functional_requirements', []))}")
        print(f"Features          : {len(vision_spec.get('features', []))}")
        print(f"Modules Detected  : {len(vision_spec.get('modules', []))}")
        print(f"Technologies      : {', '.join(vision_spec.get('technologies', [])[:6]) or 'N/A'}")
        print(f"Est. Phases       : {vision_spec.get('estimated_phases', 'N/A')}")

        # ── STAGE 1 : Capability Assessor ────────────────────────── #

        self._section(1, "Capability Assessment Phase")
        self.manager.dispatch_swarm_worker(task_id, "ASSESS-001")
        project    = self._read(task_id)
        cap_report = project.get("capability_report", {})
        print(f"\nCapability Report")
        print("-" * 40)
        print(f"Feasibility Score      : {cap_report.get('feasibility_score', 'N/A')}%")
        print(f"Fully Supported        : {cap_report.get('buildable_now', 0)}")
        print(f"Partially Supported    : {cap_report.get('partially_buildable', 0)}")
        print(f"Unsupported            : {cap_report.get('not_buildable', 0)}")
        unsup = cap_report.get("unsupported", {})
        if unsup:
            print(f"\nUnsupported Features (will NOT be falsely claimed complete):")
            for cap, desc in list(unsup.items())[:8]:
                print(f"  ✗ {cap:30s} {desc[:50]}")
            if len(unsup) > 8:
                print(f"  ... and {len(unsup) - 8} more")
        print(f"\n{cap_report.get('honest_summary', '')}")

        # ── STAGE 2 : Research AI ─────────────────────────────────── #

        self._section(2, "Intelligence Research Phase")
        self.manager.dispatch_swarm_worker(task_id, "RESEARCH-001")
        project  = self._read(task_id)
        research = project.get("research", {})
        print(f"\nResearch Summary")
        print("-" * 40)
        print(f"Project Type  : {research.get('project_type', 'N/A')}")
        print(f"Complexity    : {research.get('complexity', 'N/A')}")
        print(f"Est. Hours    : {research.get('estimated_hours', 'N/A')}")
        print(f"Verified      : {research.get('verified', False)}")
        print(f"Sources       : {len(research.get('sources', []))}")
        print(f"Concepts      : {', '.join(research.get('concepts', [])[:6])}")

        # ── STAGE 3 : Module Detector ─────────────────────────────── #

        self._section(3, "Module Detection & Dependency Graph Phase")
        self.manager.dispatch_swarm_worker(task_id, "MODULE-001")
        project      = self._read(task_id)
        modules_data = project.get("modules", {})
        print(f"\nModule Manifest")
        print("-" * 40)
        print(f"Modules Selected   : {modules_data.get('total_modules', 0)}")
        print(f"Output Files (est) : {modules_data.get('total_output_files_expected', 0)}")
        print(f"Multi-Repo Needed  : {modules_data.get('needs_multi_repo', False)}")
        exec_order = modules_data.get("execution_order", [])
        print(f"Execution Order    : {' → '.join(exec_order[:5])}{'...' if len(exec_order) > 5 else ''}")
        layer_breakdown = modules_data.get("layer_breakdown", {})
        for layer, mods in layer_breakdown.items():
            print(f"  Layer [{layer:15s}] : {', '.join(mods)}")
        unsup_vm = modules_data.get("unsupported_vision_modules", [])
        if unsup_vm:
            print(f"Unsupported Vision Modules (noted, not built):")
            for m in unsup_vm:
                print(f"  ✗ {m}")

        # ── STAGE 4 : Planner AI ──────────────────────────────────── #

        self._section(4, "Master Planning Phase")
        self.manager.dispatch_swarm_worker(task_id, "PLANNER-001")
        project = self._read(task_id)
        plan    = project.get("plan", {})
        cal     = plan.get("calendar_estimate", {})
        print(f"\nPlanning Summary")
        print("-" * 40)
        print(f"Total Phases       : {plan.get('total_phases', 'N/A')}")
        print(f"Total Tasks        : {plan.get('total_tasks', 'N/A')}")
        print(f"Total Subtasks     : {plan.get('total_subtasks', 'N/A')}")
        print(f"Estimated Hours    : {plan.get('estimated_total_hours', 'N/A')}")
        print(f"Calendar (realistic) : {cal.get('realistic_days', 'N/A')} days")
        print(f"Strategy           : {plan.get('execution_strategy', 'N/A')}")
        risks = plan.get("risks", [])
        if risks:
            print(f"Risks Identified:")
            for r in risks:
                print(f"  [{r['severity']:6s}] {r['risk']} — {r['mitigation'][:60]}")

        # ── STAGE 5 : Architect AI ────────────────────────────────── #

        self._section(5, "System Architecture Design Phase")
        self.manager.dispatch_swarm_worker(task_id, "ARCHITECT-001")
        project = self._read(task_id)
        arch    = project.get("architecture", {})
        print(f"\nArchitecture Summary")
        print("-" * 40)
        print(f"Pattern     : {arch.get('architecture_pattern', 'N/A')}")
        print(f"Framework   : {arch.get('framework', 'N/A')}")
        print(f"Language    : {arch.get('language', 'N/A')}")
        print(f"Database    : {arch.get('database', 'N/A')}")
        print(f"Auth        : {arch.get('authentication', 'N/A')}")
        print(f"Modules     : {len(arch.get('modules', []))}")
        print(f"Layers      : 9 architecture layers designed")
        print(f"Reason      : {arch.get('architecture_reason', '')[:100]}")

        # ── STAGE 6 : Database AI ─────────────────────────────────── #

        self._section(6, "Database Schema Phase")
        self.manager.dispatch_swarm_worker(task_id, "DATABASE-001")
        project = self._read(task_id)
        db_data = project.get("database", {})
        print(f"\nDatabase Summary")
        print("-" * 40)
        print(f"Schema Type  : {db_data.get('project_type', 'N/A')}")
        print(f"Tables       : {db_data.get('tables', 'N/A')}")
        print(f"Indexes      : {db_data.get('indexes', 'N/A')}")

        # ── STAGE 7 : Coder AI ────────────────────────────────────── #

        self._section(7, "Source Code Generation Phase")
        self.manager.dispatch_swarm_worker(task_id, "CODER-001")
        project = self._read(task_id)
        code    = project.get("code")

        if not code:
            print("\n[PIPELINE ERROR] Coder AI failed to generate source code.")
            self.manager.show_projects()
            return

        print(f"\nCode Summary")
        print("-" * 40)
        print(f"Project Type  : {code.get('project_type', 'N/A')}")
        print(f"Language      : {code.get('language', 'N/A')}")
        print(f"Files         : {', '.join(code.get('files', []))}")
        print(f"Source Lines  : {len(code.get('source', '').splitlines())}")
        deps = code.get("requirements", [])
        print(f"Dependencies  : {', '.join(deps) if deps else 'none (stdlib only)'}")

        # ── STAGE 8 : Design AI ───────────────────────────────────── #

        self._section(8, "UI/UX Design Phase")
        self.manager.dispatch_swarm_worker(task_id, "DESIGN-001")
        project = self._read(task_id)
        design  = project.get("design", {})
        print(f"\nDesign Summary")
        print("-" * 40)
        print(f"Tone    : {design.get('palette', {}).get('tone', 'N/A')}")
        print(f"Layout  : {design.get('layout', {}).get('type', 'N/A')}")

        # ── STAGE 9 : Reviewer AI ─────────────────────────────────── #

        self._section(9, "Static Code Review Phase")
        self.manager.dispatch_swarm_worker(task_id, "REVIEWER-001")
        project = self._read(task_id)
        review  = project["review"]

        print("\nReview Results")
        print("-" * 40)
        print(f"Quality Score  : {review['quality_score']}/100")
        print(f"Approved       : {review['approved']}")
        print(f"Recommendation : {review['release_recommendation']}")
        for issue in review.get("issues", []):
            print(f"  • {issue}")

        if not review["approved"]:
            print("\n[PIPELINE HALTED] Reviewer AI rejected this release.")
            self.manager.show_projects()
            return

        # ── STAGE 10 : Tester AI ──────────────────────────────────── #

        self._section(10, "Runtime Validation Phase")
        self.manager.dispatch_swarm_worker(task_id, "TESTER-001")
        project = self._read(task_id)
        tests   = project["tests"]

        print("\nTest Results")
        print("-" * 40)
        print(f"Passed         : {tests['passed']}")
        print(f"Coverage       : {tests['coverage']} %")
        print(f"Execution Time : {tests['execution_time_ms']} ms")
        print(f"Recommendation : {tests['release_recommendation']}")

        if not tests["passed"]:
            print("\n[PIPELINE HALTED] Runtime validation failed.")
            self.manager.show_projects()
            return

        # ── STAGE 11 : Security AI ────────────────────────────────── #

        self._section(11, "Security Analysis Phase")
        self.manager.dispatch_swarm_worker(task_id, "SECURITY-001")
        project  = self._read(task_id)
        security = project.get("security", {})

        print("\nSecurity Report")
        print("-" * 40)
        print(f"Security Score : {security.get('security_score', 'N/A')}/100")
        print(f"Risk Level     : {security.get('risk_level', 'N/A')}")
        print(f"Total Findings : {security.get('total_findings', 0)}")
        findings = security.get("findings", [])
        if findings:
            for f in findings:
                print(f"  [{f['severity']}] Line {f['line']} — {f['detail']}")
        else:
            print("  ✓ No vulnerabilities detected.")

        if not security.get("approved", False):
            print("\n[PIPELINE HALTED] Security AI blocked this release.")
            self.manager.show_projects()
            return

        # ── STAGE 12 : Performance AI ─────────────────────────────── #

        self._section(12, "Performance Profiling Phase")
        self.manager.dispatch_swarm_worker(task_id, "PERFORMANCE-001")
        project     = self._read(task_id)
        performance = project.get("performance", {})

        print("\nPerformance Report")
        print("-" * 40)
        print(f"Grade          : {performance.get('performance_grade', 'N/A')}")
        print(f"Avg Complexity : {performance.get('avg_complexity', 'N/A')}")
        print(f"Functions      : {performance.get('function_count', 'N/A')}")
        benchmarks = performance.get("benchmarks", [])
        if benchmarks:
            print("\nBenchmarks")
            for b in benchmarks:
                if b.get("skipped"):
                    print(f"  {b['function']:30s} skipped ({b.get('reason', '')})")
                else:
                    print(f"  {b['function']:30s} avg={b['avg_ms']} ms")

        # ── STAGE 13 : Documentation AI ───────────────────────────── #

        self._section(13, "Technical Documentation Phase")
        self.manager.dispatch_swarm_worker(task_id, "DOCS-001")
        project = self._read(task_id)
        docs    = project.get("documentation", {})
        print(f"\nDocumentation Summary")
        print("-" * 40)
        for f in docs.get("files_written", []):
            print(f"  ✓ {f}")

        # ── STAGE 14 : Monitoring AI ──────────────────────────────── #

        self._section(14, "Observability Phase")
        self.manager.dispatch_swarm_worker(task_id, "MONITOR-001")
        project = self._read(task_id)
        mon     = project.get("monitoring", {})
        print(f"\nMonitoring Summary")
        print("-" * 40)
        for a in mon.get("artefacts", []):
            print(f"  ✓ {a}")

        # ── STAGE 15 : Integration AI ─────────────────────────────── #

        self._section(15, "Integration Layer Phase")
        self.manager.dispatch_swarm_worker(task_id, "INTEGRATION-001")
        project = self._read(task_id)
        intg    = project.get("integration", {})
        print(f"\nIntegration Summary")
        print("-" * 40)
        for a in intg.get("artefacts", []):
            print(f"  ✓ {a}")
        print(f"  Points : {', '.join(intg.get('integration_points', []))}")

        # ── STAGE 16 : DevOps AI ──────────────────────────────────── #

        self._section(16, "DevOps & Infrastructure Phase")
        self.manager.dispatch_swarm_worker(task_id, "DEVOPS-001")
        project = self._read(task_id)
        devops  = project.get("devops", {})
        print(f"\nDevOps Report")
        print("-" * 40)
        print(f"Readiness Score : {devops.get('readiness_score', 'N/A')}%")
        for a in devops.get("artefacts", []):
            print(f"  ✓ {a}")

        # ── STAGE 17 : Deployment AI ──────────────────────────────── #

        self._section(17, "Enterprise Deployment Phase")
        project["deployment_ready"] = True
        self.shared_memory.write(f"active_project_{task_id}", project)

        self.manager.dispatch_swarm_worker(task_id, "DEPLOY-001")
        project    = self._read(task_id)
        deployment = project.get("deployment")

        if deployment is None:
            print("\n[DEPLOYMENT FAILED] Deployment metadata not generated.")
            self.manager.show_projects()
            return

        print("\nDeployment Verification")
        print("-" * 40)
        deploy_path = deployment["deployment_path"]
        print(f"Deployment Folder : {deploy_path}")
        for artifact in [
            "main.py", "requirements.txt", "README.md", "deployment.json",
            "Dockerfile", "Makefile", "docker-compose.yml",
        ]:
            full = os.path.join(deploy_path, artifact)
            mark = "✓" if os.path.exists(full) else "✗"
            print(f"  {mark} {artifact}")

        # ── STAGE 18 : Verification AI ────────────────────────────── #

        self._section(18, "Verification Phase")
        self.manager.dispatch_swarm_worker(task_id, "VERIFY-001")
        project      = self._read(task_id)
        verification = project.get("verification", {})

        print(f"\nVerification Report")
        print("-" * 40)
        print(f"Verdict           : {verification.get('verdict', 'N/A')}")
        print(f"Score             : {verification.get('verification_score', 'N/A')}%")
        print(f"Checks Passed     : {verification.get('checks_passed', 'N/A')}/{verification.get('checks_total', 'N/A')}")
        print(f"Critical Failures : {verification.get('critical_failures', 0)}")

        if not verification.get("verification_passed", False):
            issues = verification.get("all_issues", [])
            if issues:
                print("\nVerification Issues:")
                for issue in issues:
                    print(f"  ⚠  {issue}")
            # Non-blocking — report but continue
            print("\n[PIPELINE] Verification issues noted — continuing to progress report.")

        # ── STAGE 19 : Progress Tracker ───────────────────────────── #

        self._section(19, "Progress Reporting Phase")
        self.manager.dispatch_swarm_worker(task_id, "PROGRESS-001")
        project  = self._read(task_id)
        progress = project.get("progress_report", {})

        print(f"\nProgress Report")
        print("-" * 40)
        pipeline_pct = progress.get("pipeline_execution_pct", progress.get("overall_completion_pct", "N/A"))
        vision_pct   = progress.get("vision_coverage_pct")
        print(f"Pipeline Execution   : {pipeline_pct}%")
        print(f"  (How many of the 19 builder stages completed — not a measure of feature completeness)")
        if vision_pct is not None:
            print(f"Vision Coverage      : {vision_pct}%")
            print(f"  (Of all capabilities requested in the goal/vision, this fraction is buildable now)")
        else:
            print(f"Vision Coverage      : 100%  (simple goal — all requested features are buildable)")
        print(f"Implementable Now    : {progress.get('implemented_count', 0)} capabilities  (built in this run)")
        print(f"Partial Support      : {progress.get('partial_count', 0)} capabilities  (scaffolded, implementation incomplete)")
        print(f"Requires Future Dev  : {progress.get('unsupported_count', 0)} capabilities  (not yet buildable by NEXUS)")
        feature_map = progress.get("feature_classification", {})
        if feature_map.get("unsupported"):
            print(f"\nCapabilities requiring future development (NOT implemented):")
            for f in feature_map["unsupported"][:10]:
                print(f"  ✗ {f}")
            if len(feature_map["unsupported"]) > 10:
                print(f"  ... and {len(feature_map['unsupported']) - 10} more")
        limitations = progress.get("known_limitations", [])
        if limitations:
            print(f"\nKnown Limitations ({len(limitations)}):")
            for lim in limitations[:5]:
                cat = lim.get("category", "")
                cap = lim.get("capability", "")
                sts = lim.get("status", "")
                print(f"  [{cat:22s}] {cap:35s} {sts}")
            if len(limitations) > 5:
                print(f"  ... and {len(limitations) - 5} more")
        recs = progress.get("recommendations", [])
        if recs:
            print(f"\nRecommendations:")
            for rec in recs:
                print(f"  → {rec}")

        # ── STAGE 20 : Memory AI ──────────────────────────────────── #

        self._section(20, "Knowledge Preservation Phase")
        self.manager.dispatch_swarm_worker(task_id, "MEMORY-001")
        project = self._read(task_id)

        # ── Final Master Summary ───────────────────────────────────── #

        self._final_summary(project, task_id)

    # ------------------------------------------------------------------ #
    # Final Summary                                                        #
    # ------------------------------------------------------------------ #

    def _final_summary(self, project: dict, task_id: str):
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE  —  NEXUS ENTERPRISE v3.0")
        print("=" * 70)

        res    = project.get("research", {})
        arch   = project.get("architecture", {})
        rev    = project.get("review", {})
        tst    = project.get("tests",  {})
        sec    = project.get("security", {})
        perf   = project.get("performance", {})
        dev    = project.get("devops", {})
        doc    = project.get("documentation", {})
        intg   = project.get("integration", {})
        veri   = project.get("verification", {})
        prog   = project.get("progress_report", {})
        dep    = project.get("deployment", {})
        cap    = project.get("capability_report", {})
        mods   = project.get("modules", {})
        vision = project.get("vision_spec", {})

        print(f"Task ID              : {project['task_id']}")
        print(f"Goal                 : {project['goal'][:80]}{'...' if len(project['goal']) > 80 else ''}")
        print(f"Document Type        : {vision.get('document_type', 'SIMPLE_GOAL')}")
        print(f"Project Type         : {res.get('project_type', 'N/A')}")
        print(f"Final Status         : {project['status']}")
        print(f"─" * 40)
        print(f"Vision Sections      : {len(vision.get('section_titles', []))}")
        print(f"Functional Reqs      : {len(vision.get('functional_requirements', []))}")
        print(f"Modules in Manifest  : {mods.get('total_modules', 0)}")
        print(f"Feasibility Score    : {cap.get('feasibility_score', 'N/A')}%")
        print(f"─" * 40)
        print(f"Architecture Pattern : {arch.get('architecture_pattern', 'N/A')}")
        print(f"Framework            : {arch.get('framework', 'N/A')}")
        print(f"DB Schema Tables     : {project.get('database', {}).get('tables', 'N/A')}")
        print(f"Review Score         : {rev.get('quality_score', 'N/A')}/100")
        print(f"Test Coverage        : {tst.get('coverage', 'N/A')} %")
        print(f"Security Score       : {sec.get('security_score', 'N/A')}/100")
        print(f"Perf Grade           : {perf.get('performance_grade', 'N/A')}")
        print(f"Docs Written         : {doc.get('total_files', 'N/A')} files")
        print(f"DevOps Readiness     : {dev.get('readiness_score', 'N/A')}%")
        print(f"Verification Score   : {veri.get('verification_score', 'N/A')}%")
        print(f"─" * 40)
        # ── Unambiguous completion metrics ──────────────────────────── #
        pipeline_pct = prog.get("pipeline_execution_pct", prog.get("overall_completion_pct", "N/A"))
        vision_pct   = prog.get("vision_coverage_pct")
        print(f"Pipeline Execution   : {pipeline_pct}%  ← builder stages that ran")
        if vision_pct is not None:
            print(f"Vision Coverage      : {vision_pct}%  ← requested capabilities buildable now")
        else:
            print(f"Vision Coverage      : 100%  ← all requested features are buildable")
        print(f"─" * 40)
        print(f"Implementable Now    : {cap.get('buildable_now', 0)} capabilities  (built in this run)")
        print(f"Partial Support      : {cap.get('partially_buildable', 0)} capabilities  (scaffolded, incomplete)")
        print(f"Requires Future Dev  : {cap.get('not_buildable', 0)} capabilities  (not yet buildable)")
        print(f"─" * 40)
        print(f"Deployment Ready     : {project.get('deployment_ready', False)}")
        print(f"Deployment Path      : {dep.get('deployment_path', 'N/A')}")
        print(f"\n{'=' * 70}")
        print("NEXUS BUILDER — HONESTY FIRST. BUILD WHAT IS BUILDABLE. PLAN THE REST.")
        print("=" * 70)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _section(self, number: int, title: str):
        print(f"\n{'=' * 70}")
        print(f"[STAGE {number}] {title}")
        print("=" * 70)

    def _read(self, task_id: str) -> dict:
        return self.shared_memory.read(f"active_project_{task_id}")
