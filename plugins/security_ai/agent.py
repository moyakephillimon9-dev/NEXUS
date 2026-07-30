"""
NEXUS
Security AI — Vulnerability Analysis Engine

Module ID : SECURITY-001
Version   : 1.0.0

Performs real static security analysis using Python's AST
module and regex-based pattern matching.  Every finding
is derived from the actual source code — nothing is faked.
"""

import ast
import re
from datetime import datetime


# ------------------------------------------------------------------ #
# Severity weights (deducted from 100)                                #
# ------------------------------------------------------------------ #

_SEVERITY = {
    "CRITICAL": 30,
    "HIGH":     20,
    "MEDIUM":   10,
    "LOW":       5,
    "INFO":      0,
}

# Regex patterns for secret detection
_SECRET_PATTERNS = [
    (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']',   "Hardcoded password detected.",          "CRITICAL"),
    (r'(?i)(api_key|apikey|api_secret)\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded API key detected.",       "CRITICAL"),
    (r'(?i)(secret|token)\s*=\s*["\'][^"\']{3,}["\']',          "Hardcoded secret/token detected.",      "HIGH"),
    (r'(?i)(private_key|privatekey)\s*=\s*["\'][^"\']{3,}["\']',"Hardcoded private key detected.",       "CRITICAL"),
]


class SecurityAI:
    """
    NEXUS Security Analyst.

    Performs genuine AST-level and pattern-based security
    analysis on every piece of generated source code before
    it is allowed to reach the deployment stage.

    Responsibilities
    ----------------
    • Dangerous function detection  (eval / exec / os.system)
    • Shell-injection detection     (subprocess shell=True)
    • Hardcoded-secret detection    (regex)
    • Insecure-deserialisation scan (pickle)
    • Bare-except detection
    • SQL-injection heuristics
    • Scoring + release gate
    """

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Security AI] Connected to Shared Memory.")

    def start(self):
        print("[Security AI] Vulnerability Analysis Engine Ready.")

    # ---------------------------------------------------------------- #
    # Core Analysis                                                      #
    # ---------------------------------------------------------------- #

    def analyze_source_code(self, source: str) -> dict:
        """
        Run all security checks against *source* and return a
        structured security report.
        """

        if not source:
            return self._empty_report("Source code missing.")

        findings = []

        # ---- 1. AST parse ------------------------------------------ #

        try:
            tree = ast.parse(source)
        except SyntaxError as err:
            return self._empty_report(
                f"Syntax error — cannot analyse: {err}"
            )

        # ---- 2. AST walk ------------------------------------------- #

        for node in ast.walk(tree):

            # eval()
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "eval"
            ):
                findings.append({
                    "severity": "CRITICAL",
                    "rule":     "DANGEROUS_EVAL",
                    "detail":   "Use of eval() allows arbitrary code execution.",
                    "line":     getattr(node, "lineno", "?"),
                })

            # exec()
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "exec"
            ):
                findings.append({
                    "severity": "HIGH",
                    "rule":     "DANGEROUS_EXEC",
                    "detail":   "Use of exec() allows dynamic code execution.",
                    "line":     getattr(node, "lineno", "?"),
                })

            # os.system()
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "system"
            ):
                findings.append({
                    "severity": "HIGH",
                    "rule":     "OS_SYSTEM",
                    "detail":   "os.system() is vulnerable to shell injection.",
                    "line":     getattr(node, "lineno", "?"),
                })

            # subprocess with shell=True
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if (
                        kw.arg == "shell"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value is True
                    ):
                        findings.append({
                            "severity": "HIGH",
                            "rule":     "SUBPROCESS_SHELL_TRUE",
                            "detail":   "subprocess called with shell=True enables shell injection.",
                            "line":     getattr(node, "lineno", "?"),
                        })

            # pickle.loads / pickle.load
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("loads", "load")
            ):
                # Check if the object is 'pickle'
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "pickle"
                ):
                    findings.append({
                        "severity": "HIGH",
                        "rule":     "INSECURE_DESERIALISATION",
                        "detail":   "pickle.load/loads is unsafe with untrusted data.",
                        "line":     getattr(node, "lineno", "?"),
                    })

            # Bare except (ExceptHandler with no type)
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append({
                    "severity": "LOW",
                    "rule":     "BARE_EXCEPT",
                    "detail":   "Bare 'except:' swallows all exceptions including KeyboardInterrupt.",
                    "line":     getattr(node, "lineno", "?"),
                })

            # SQL injection heuristic — string formatting in execute()
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "execute"
            ):
                for arg in node.args:
                    if isinstance(arg, (ast.JoinedStr, ast.BinOp, ast.Mod)):
                        findings.append({
                            "severity": "CRITICAL",
                            "rule":     "SQL_INJECTION",
                            "detail":   "Possible SQL injection via string formatting in execute().",
                            "line":     getattr(node, "lineno", "?"),
                        })

        # ---- 3. Regex secret scan ----------------------------------- #

        for pattern, message, severity in _SECRET_PATTERNS:
            for match in re.finditer(pattern, source):
                line_no = source[: match.start()].count("\n") + 1
                findings.append({
                    "severity": severity,
                    "rule":     "HARDCODED_SECRET",
                    "detail":   message,
                    "line":     line_no,
                })

        # ---- 4. Score ---------------------------------------------- #

        deductions = sum(
            _SEVERITY[f["severity"]] for f in findings
        )
        security_score = max(0, 100 - deductions)

        # ---- 5. Risk level ----------------------------------------- #

        critical_count = sum(
            1 for f in findings if f["severity"] == "CRITICAL"
        )
        high_count = sum(
            1 for f in findings if f["severity"] == "HIGH"
        )

        if critical_count > 0:
            risk_level = "CRITICAL"
        elif high_count > 0:
            risk_level = "HIGH"
        elif security_score >= 80:
            risk_level = "LOW"
        elif security_score >= 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        approved = (
            security_score >= 70
            and critical_count == 0
        )

        return {
            "analysed_at":      datetime.utcnow().isoformat(),
            "security_score":   security_score,
            "risk_level":       risk_level,
            "approved":         approved,
            "total_findings":   len(findings),
            "critical":         critical_count,
            "high":             high_count,
            "findings":         findings,
            "recommendation":   "APPROVED" if approved else "SECURITY_REMEDIATION_REQUIRED",
        }

    # ---------------------------------------------------------------- #
    # Pipeline Entry Point                                               #
    # ---------------------------------------------------------------- #

    def process_project_task(self, task_id: str):

        key     = f"active_project_{task_id}"
        project = self.memory.read(key)

        if project is None:
            print("[Security AI] Project not found.")
            return

        print(f"[Security AI] Scanning: {task_id}")

        source = project.get("code", {}).get("source", "")
        report = self.analyze_source_code(source)

        project["security"] = report

        if report["approved"]:
            project["status"] = "SECURITY_APPROVED"
            print("[Security AI] Security scan passed.")
        else:
            project["status"] = "SECURITY_REMEDIATION_REQUIRED"
            print("[Security AI] Security issues detected.")

        self.memory.write(key, project)

        print(f"[Security AI] Score      : {report['security_score']}/100")
        print(f"[Security AI] Risk Level : {report['risk_level']}")
        print(f"[Security AI] Findings   : {report['total_findings']}")
        print(f"[Security AI] Verdict    : {report['recommendation']}")

    # ---------------------------------------------------------------- #
    # Helpers                                                            #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _empty_report(reason: str) -> dict:
        return {
            "analysed_at":    datetime.utcnow().isoformat(),
            "security_score": 0,
            "risk_level":     "UNKNOWN",
            "approved":       False,
            "total_findings": 0,
            "critical":       0,
            "high":           0,
            "findings":       [],
            "recommendation": "SECURITY_REMEDIATION_REQUIRED",
            "error":          reason,
        }
