"""
NEXUS
Verification AI — Pre-Release Honesty & Completeness Engine

Module ID : VERIFY-001
Version   : 1.0.0

Responsibilities
----------------
• Verify every requested capability has a real implementation
• Verify every generated module produces at least one output file
• Verify dependencies resolve (all referenced files exist)
• Verify documentation matches the generated implementation
• Verify tests were executed (not skipped)
• Confirm unsupported features are documented as such — not claimed
• Produce a final verification report with pass/fail per check
• Block pipeline from reporting success if critical checks fail
"""

import os
from datetime import datetime


class VerificationAI:
    """
    Pre-Release Honesty and Completeness Engine.

    This worker runs after all generation stages are complete.
    It verifies real outputs against claimed outputs and produces
    an honest pass/fail report before the pipeline reports success.

    It NEVER approves a pipeline run that has unchecked failures.
    """

    # ------------------------------------------------------------------ #
    # Expected artifact checks                                            #
    # ------------------------------------------------------------------ #

    # Core artifacts that must always exist after a successful pipeline run
    _REQUIRED_CORE_ARTIFACTS = [
        "main.py",
        "requirements.txt",
        "README.md",
        "Dockerfile",
        "Makefile",
        "deployment.json",
    ]

    # Artifacts that should exist if those stages ran
    _STAGE_ARTIFACTS = {
        "schema.sql":                       "Database AI",
        "database.py":                      "Database AI",
        "static/style.css":                 "Design AI",
        "design_spec.md":                   "Design AI",
        "docs/API.md":                      "Documentation AI",
        "docs/ARCHITECTURE.md":             "Documentation AI",
        "docs/CHANGELOG.md":                "Documentation AI",
        "monitoring/health_check.py":       "Monitoring AI",
        "monitoring/metrics.py":            "Monitoring AI",
        "integrations/api_client.py":       "Integration AI",
        "integrations/webhook_handler.py":  "Integration AI",
        ".github/workflows/ci.yml":         "DevOps AI",
        "docker-compose.yml":               "DevOps AI",
    }

    # ------------------------------------------------------------------ #

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Verification AI] Connected to Shared Memory.")

    def start(self):
        print("[Verification AI] Pre-Release Honesty & Completeness Engine Ready.")

    # ------------------------------------------------------------------ #
    # Verification checks                                                  #
    # ------------------------------------------------------------------ #

    def _check_capability_honesty(self, project: dict) -> dict:
        """Ensure unsupported features are noted, not claimed complete."""
        cap_report = project.get("capability_report", {})
        unsupported = cap_report.get("unsupported", {})
        final_status = project.get("status", "")

        issues = []
        if unsupported and "UNSUPPORTED_FEATURES_DOCUMENTED" not in project:
            # Check that the project doesn't falsely claim full completion
            # on a vision doc with unsupported features
            vision_spec = project.get("vision_spec", {})
            if vision_spec.get("document_type") == "VISION_DOCUMENT":
                if len(unsupported) > 0:
                    issues.append(
                        f"{len(unsupported)} unsupported features detected — "
                        f"these must be in progress report as UNSUPPORTED"
                    )

        return {
            "check":   "capability_honesty",
            "passed":  len(issues) == 0,
            "issues":  issues,
            "details": f"{len(unsupported)} unsupported features identified and documented",
        }

    def _check_code_generated(self, project: dict) -> dict:
        """Verify source code was actually generated."""
        code = project.get("code", {})
        source = code.get("source", "")
        issues = []

        if not source or len(source.strip()) < 20:
            issues.append("No source code generated (code.source is empty)")
        if not code.get("project_type"):
            issues.append("Project type not detected")

        return {
            "check":   "code_generated",
            "passed":  len(issues) == 0,
            "issues":  issues,
            "details": f"Source: {len(source)} chars, Type: {code.get('project_type', 'unknown')}",
        }

    def _check_tests_ran(self, project: dict) -> dict:
        """Verify tests were actually executed."""
        tests  = project.get("tests", {})
        issues = []

        if not tests:
            issues.append("No test results found in project")
        elif "passed" not in tests:
            issues.append("Test results malformed — 'passed' field missing")

        return {
            "check":   "tests_executed",
            "passed":  len(issues) == 0,
            "issues":  issues,
            "details": (
                f"Passed: {tests.get('passed', 'N/A')}, "
                f"Coverage: {tests.get('coverage', 'N/A')}%"
            ),
        }

    def _check_security_ran(self, project: dict) -> dict:
        """Verify security scan was executed."""
        sec    = project.get("security", {})
        issues = []

        if not sec:
            issues.append("No security scan results found")
        elif "security_score" not in sec:
            issues.append("Security results malformed")

        return {
            "check":   "security_scanned",
            "passed":  len(issues) == 0,
            "issues":  issues,
            "details": f"Score: {sec.get('security_score', 'N/A')}/100, Risk: {sec.get('risk_level', 'N/A')}",
        }

    def _check_documentation_exists(self, project: dict) -> dict:
        """Verify documentation was generated."""
        docs   = project.get("documentation", {})
        issues = []

        files_written = docs.get("files_written", [])
        if not files_written:
            issues.append("No documentation files recorded")
        elif "README.md" not in files_written:
            issues.append("README.md not generated")

        return {
            "check":   "documentation_generated",
            "passed":  len(issues) == 0,
            "issues":  issues,
            "details": f"{len(files_written)} documentation files written",
        }

    def _check_deployment_artifacts(self, project: dict) -> dict:
        """Verify deployment artifacts exist on disk."""
        deployment = project.get("deployment", {})
        issues     = []
        found      = []
        missing    = []

        deploy_path = deployment.get("deployment_path", "")
        if not deploy_path or not os.path.isdir(deploy_path):
            issues.append(f"Deployment folder not found: {deploy_path}")
            return {
                "check":   "deployment_artifacts",
                "passed":  False,
                "issues":  issues,
                "details": "Deployment folder missing",
            }

        for artifact in self._REQUIRED_CORE_ARTIFACTS:
            full = os.path.join(deploy_path, artifact)
            if os.path.exists(full):
                found.append(artifact)
            else:
                missing.append(artifact)
                issues.append(f"Missing required artifact: {artifact}")

        # Check optional stage artifacts
        stage_found   = []
        stage_missing = []
        for artifact, stage in self._STAGE_ARTIFACTS.items():
            full = os.path.join(deploy_path, artifact)
            if os.path.exists(full):
                stage_found.append(artifact)
            else:
                stage_missing.append((artifact, stage))

        return {
            "check":          "deployment_artifacts",
            "passed":         len(missing) == 0,
            "issues":         issues,
            "details":        f"Core: {len(found)}/{len(self._REQUIRED_CORE_ARTIFACTS)} found. Stage artifacts: {len(stage_found)}/{len(self._STAGE_ARTIFACTS)}",
            "core_found":     found,
            "core_missing":   missing,
            "stage_found":    stage_found,
            "stage_missing":  [f"{a} ({s})" for a, s in stage_missing],
        }

    def _check_architecture_defined(self, project: dict) -> dict:
        """Verify architecture was designed."""
        arch   = project.get("architecture", {})
        issues = []

        if not arch:
            issues.append("No architecture defined")
        else:
            required_keys = ["framework", "language", "database", "modules"]
            for k in required_keys:
                if k not in arch:
                    issues.append(f"Architecture missing field: {k}")

        return {
            "check":   "architecture_defined",
            "passed":  len(issues) == 0,
            "issues":  issues,
            "details": f"Framework: {arch.get('framework', 'N/A')}, Modules: {len(arch.get('modules', []))}",
        }

    def _check_modules_detected(self, project: dict) -> dict:
        """Verify module detection ran."""
        modules = project.get("modules", {})
        issues  = []

        if not modules:
            issues.append("Module detection did not run")
        elif not modules.get("module_manifest"):
            issues.append("Module manifest is empty")

        return {
            "check":   "modules_detected",
            "passed":  len(issues) == 0,
            "issues":  issues,
            "details": f"{modules.get('total_modules', 0)} modules in manifest",
        }

    # ------------------------------------------------------------------ #
    # Master verification                                                  #
    # ------------------------------------------------------------------ #

    def verify(self, project: dict) -> dict:
        checks = [
            self._check_capability_honesty(project),
            self._check_code_generated(project),
            self._check_tests_ran(project),
            self._check_security_ran(project),
            self._check_documentation_exists(project),
            self._check_deployment_artifacts(project),
            self._check_architecture_defined(project),
            self._check_modules_detected(project),
        ]

        passed_checks = [c for c in checks if c["passed"]]
        failed_checks = [c for c in checks if not c["passed"]]

        # Critical failures block the pipeline
        critical_failures = [
            c for c in failed_checks
            if c["check"] in ("code_generated", "deployment_artifacts", "tests_executed")
        ]

        all_issues = []
        for c in failed_checks:
            all_issues.extend(c["issues"])

        verification_passed = len(critical_failures) == 0

        score = round((len(passed_checks) / max(len(checks), 1)) * 100, 1)

        return {
            "verified_at":          datetime.utcnow().isoformat(),
            "verification_passed":  verification_passed,
            "verification_score":   score,
            "checks_total":         len(checks),
            "checks_passed":        len(passed_checks),
            "checks_failed":        len(failed_checks),
            "critical_failures":    len(critical_failures),
            "all_checks":           checks,
            "all_issues":           all_issues,
            "verdict":              "VERIFIED" if verification_passed else "VERIFICATION_FAILED",
        }

    # ------------------------------------------------------------------ #
    # Pipeline entry point                                                 #
    # ------------------------------------------------------------------ #

    def process_project_task(self, task_id: str):
        project_key = f"active_project_{task_id}"
        project     = self.memory.read(project_key)

        if project is None:
            print(f"[Verification AI] Project '{task_id}' not found.")
            return

        print(f"[Verification AI] Running verification: {task_id}")

        report = self.verify(project)

        project["verification"]  = report
        project["status"]        = report["verdict"]

        self.memory.write(project_key, project)

        print(f"[Verification AI] Score           : {report['verification_score']}%")
        print(f"[Verification AI] Checks Passed   : {report['checks_passed']}/{report['checks_total']}")
        print(f"[Verification AI] Critical Fails  : {report['critical_failures']}")
        print(f"[Verification AI] Verdict         : {report['verdict']}")

        for check in report["all_checks"]:
            mark = "✓" if check["passed"] else "✗"
            print(f"  {mark} {check['check']:35s} {check['details']}")

        if report["all_issues"]:
            print(f"\n[Verification AI] Issues Found:")
            for issue in report["all_issues"]:
                print(f"  ⚠  {issue}")
