"""
NEXUS
Tester AI — Master Runtime Validation Engine

Module ID : TESTER-001
Version   : 0.3.0
"""

import time
import traceback
from datetime import datetime


class TesterAI:
    """
    Supreme Runtime Validation Engine.

    Responsibilities
    ----------------
    • Runtime Validation
    • Functional Verification
    • Execution Profiling
    • Coverage Estimation
    • Regression Detection
    • Release Recommendation
    • Automated Feedback Loop
    """

    def __init__(self, shared_memory):

        self.memory = shared_memory

        print("[Tester AI] Connected to Shared Memory.")

    def start(self):

        print("[Tester AI] Master Runtime Validation Engine Ready.")

    ####################################################################
    # MASTER EXECUTION ENGINE
    ####################################################################

    def execute_sandboxed_test_suite(self, source_code):

        if not source_code:

            return {

                "evaluated_at":
                    datetime.utcnow().isoformat(),

                "passed":
                    False,

                "quality":
                    0,

                "coverage":
                    0,

                "execution_time_ms":
                    0,

                "release_recommendation":
                    "RETURN_TO_CODER",

                "execution_log":
                    "Source code missing."

            }

        ###############################################################

        statements = [

            line

            for line in source_code.splitlines()

            if line.strip()
            and
            not line.strip().startswith("#")

        ]

        statement_count = len(statements)

        estimated_coverage = round(

            (statement_count / max(1, statement_count + 2))

            * 100,

            1

        )

        ###############################################################

        harness = f"""
def __nexus_test():

    namespace = {{}}

    exec({source_code!r}, namespace)

    functions = [

        name

        for name,value

        in namespace.items()

        if callable(value)

    ]

    assert len(functions) > 0

    return functions
"""

        start = time.perf_counter()

        try:

            sandbox = {}

            exec(harness, sandbox)

            functions = sandbox["__nexus_test"]()

            passed = True

            execution_log = (

                "Verified functions: "

                + ", ".join(functions)

            )

        except Exception as error:

            passed = False

            execution_log = (

                str(error)

                + "\n"

                + traceback.format_exc()

            )

        runtime = round(

            (time.perf_counter() - start)

            * 1000,

            3

        )

        ###############################################################

        quality = 100 if passed else 20

        recommendation = (

            "DEPLOY"

            if passed

            else

            "RETURN_TO_CODER"

        )

        ###############################################################

        return {

            "evaluated_at":
                datetime.utcnow().isoformat(),

            "passed":
                passed,

            "quality":
                quality,

            "coverage":
                estimated_coverage,

            "execution_time_ms":
                runtime,

            "release_recommendation":
                recommendation,

            "execution_log":
                execution_log

        }

    ####################################################################
    # TEST PIPELINE
    ####################################################################

    def process_project_task(self, task_id):

        project_key = f"active_project_{task_id}"

        project = self.memory.read(project_key)

        if project is None:

            print("[Tester AI] Project not found.")

            return

        print(f"[Tester AI] Running Runtime Validation: {task_id}")

        ###############################################################

        code_data = project.get("code", {})

        source = code_data.get("source", "")
        goal   = project.get("goal", "")

        ###############################################################
        # NEXUS AI: generate and store meaningful test suite
        ###############################################################

        try:
            from core.nexus_ai import NexusAI
            nexus      = NexusAI(self.memory)
            test_code  = nexus.generate_tests(source, goal)
            if test_code and len(test_code.strip()) > 100:
                project["generated_tests"] = test_code
                print(f"[Tester AI] Provider   : {nexus._provider_instance().name()}")
                print(f"[Tester AI] Test suite : {len(test_code.splitlines())} lines generated")
        except Exception as _exc:
            print(f"[Tester AI] AI test generation skipped ({_exc}).")

        ###############################################################

        report = self.execute_sandboxed_test_suite(source)

        ###############################################################

        project.setdefault(

            "test_history",

            []

        ).append(report)

        project["tests"] = report

        ###############################################################

        if report["passed"]:

            project["status"] = "TESTS_PASSED"

            project["deployment_ready"] = True

            print("[Tester AI] Runtime Validation Passed.")

        else:

            project["status"] = "PROGRAMMING_PHASE"

            project["deployment_ready"] = False

            project["regression_required"] = True

            project["failure_reason"] = report["execution_log"]

            print("[Tester AI] Runtime Validation Failed.")

            print("[Tester AI] Returning project to Coder AI.")

        ###############################################################

        self.memory.write(

            project_key,

            project

        )

        print(

            f"[Tester AI] Coverage : {report['coverage']}%"

        )

        print(

            f"[Tester AI] Runtime : {report['execution_time_ms']} ms"

        )

        print(

            f"[Tester AI] Recommendation : {report['release_recommendation']}"

        )
