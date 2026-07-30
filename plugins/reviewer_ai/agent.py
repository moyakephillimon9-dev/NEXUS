"""
NEXUS
Reviewer AI — Failure Prevention Engine

Module ID : REVIEWER-001
Version   : 0.3.0
"""

import ast
from datetime import datetime


class ReviewerAI:
    """
    Supreme Quality Assurance Engine.

    Responsibilities
    ----------------
    • Static Code Analysis
    • Security Inspection
    • Technical Debt Assessment
    • Maintainability Analysis
    • Release Approval
    • Failure Prevention
    """

    def __init__(self, shared_memory):

        self.memory = shared_memory

        print("[Reviewer AI] Connected to Shared Memory.")

    def start(self):

        print("[Reviewer AI] Master Review Engine Ready.")

    ####################################################################
    # MASTER STATIC ANALYSIS ENGINE
    ####################################################################

    def analyze_source_code(self, code):

        if not code:

            return {

                "quality_score":0,

                "approved":False,

                "technical_debt":100,

                "release_recommendation":"REJECT",

                "issues":[
                    "Source code missing."
                ]
            }

        issues = []

        deductions = 0

        function_count = 0

        line_count = len(code.splitlines())

        ###########################################################
        # Compile Validation
        ###########################################################

        try:

            tree = ast.parse(code)

        except SyntaxError as error:

            return {

                "quality_score":0,

                "approved":False,

                "technical_debt":100,

                "release_recommendation":"REJECT",

                "issues":[
                    f"Syntax Error Line {error.lineno}: {error.msg}"
                ]
            }

        ###########################################################
        # AST Security Inspection
        ###########################################################

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):

                function_count += 1

            if isinstance(node, ast.Call):

                ###################################################
                # eval()
                ###################################################

                if isinstance(node.func, ast.Name):

                    if node.func.id == "eval":

                        issues.append(
                            "Dangerous use of eval()."
                        )

                        deductions += 40

                ###################################################
                # os.system()
                ###################################################

                if isinstance(node.func, ast.Attribute):

                    if node.func.attr == "system":

                        issues.append(
                            "Dangerous os.system() execution."
                        )

                        deductions += 30

        ###########################################################
        # Maintainability
        ###########################################################

        if function_count == 0:

            issues.append(
                "No modular functions detected."
            )

            deductions += 15

        if line_count > 300:

            issues.append(
                "Large source file (>300 lines)."
            )

            deductions += 10

        ###########################################################
        # Technical Debt
        ###########################################################

        technical_debt = deductions

        quality_score = max(0, 100 - deductions)

        ###########################################################
        # Release Gate
        ###########################################################

        approved = (

            quality_score >= 70

            and

            not any(

                "Dangerous" in issue

                for issue in issues

            )

        )

        if approved:

            recommendation = "APPROVE"

        elif quality_score >= 50:

            recommendation = "REVIEW_REQUIRED"

        else:

            recommendation = "REJECT"

        ###########################################################
        # Final Audit
        ###########################################################

        return {

            "review_time":
                datetime.utcnow().isoformat(),

            "quality_score":
                quality_score,

            "technical_debt":
                technical_debt,

            "approved":
                approved,

            "release_recommendation":
                recommendation,

            "functions_detected":
                function_count,

            "line_count":
                line_count,

            "issues":
                issues if issues else [

                    "Static analysis passed.",

                    "No security issues detected.",

                    "Architecture acceptable."

                ]

        }

    ####################################################################
    # REVIEW PIPELINE
    ####################################################################

    def process_project_task(self, task_id):

        project_key = f"active_project_{task_id}"

        project = self.memory.read(project_key)

        if project is None:

            print("[Reviewer AI] Project not found.")

            return

        print(f"[Reviewer AI] Reviewing {task_id}")

        ###########################################################
        # Retrieve source code
        ###########################################################

        code_data = project.get("code", {})

        source = code_data.get("source", "")

        ###########################################################
        # NEXUS AI: intelligent code review
        ###########################################################

        audit = None
        try:
            from core.nexus_ai import NexusAI
            nexus    = NexusAI(self.memory)
            ptype    = project.get("project_type", "generic")
            ai_raw   = nexus.generate_review(source, ptype)
            ai_rev   = nexus.parse_json(ai_raw)
            if isinstance(ai_rev.get("quality_score"), (int, float)):
                audit = {
                    "quality_score":          int(ai_rev["quality_score"]),
                    "approved":               bool(ai_rev.get("approved", ai_rev["quality_score"] >= 70)),
                    "technical_debt":         int(ai_rev.get("technical_debt", 100 - ai_rev["quality_score"])),
                    "release_recommendation": ai_rev.get("release_recommendation", "APPROVED"),
                    "issues":                 ai_rev.get("issues", []),
                    "strengths":              ai_rev.get("strengths", []),
                    "reviewed_at":            __import__("datetime").datetime.utcnow().isoformat(),
                }
                print(f"[Reviewer AI] Provider   : {nexus._provider_instance().name()}")
        except Exception as _exc:
            print(f"[Reviewer AI] AI review skipped ({_exc}), using static analysis.")

        ###########################################################
        # Fallback: existing static analysis
        ###########################################################

        if not audit:
            audit = self.analyze_source_code(source)

        project["review"] = audit

        if audit["approved"]:

            project["status"] = "REVIEW_APPROVED"

        else:

            project["status"] = "REVIEW_REJECTED"

        self.memory.write(project_key, project)

        print(f"[Reviewer AI] Quality Score : {audit['quality_score']}/100")

        print(f"[Reviewer AI] Recommendation : {audit['release_recommendation']}")

        print(f"[Reviewer AI] Status Updated -> {project['status']}")
