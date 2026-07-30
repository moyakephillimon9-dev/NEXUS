"""
NEXUS
Manager AI — Master Strategic Advisor Core

Module ID : MANAGER-001
Version   : 0.3.1
"""

import uuid
from datetime import datetime
from plugins.planner_ai.agent import PlannerAI


class ManagerAI:
    """
    Supreme Coordinator of the NEXUS AI Engineering Company.

    Responsibilities
    ----------------
    • Founder Advisory
    • Strategic Planning
    • Adversarial Risk Analysis
    • AI Employee Management
    • Task Orchestration
    • Resource Allocation
    • Project Governance
    """

    def __init__(self, shared_memory):
        self.memory = shared_memory
        self.employee_registry = {}

        print("[Manager AI] Connected to Shared Memory.")

    def start(self):
        print("[Manager AI] Swarm Control Online.")
        print("[Manager AI] Strategic Advisory Engine Active.")

    def register_employee(self, employee_id, agent_instance):

        employee_id = employee_id.upper()

        self.employee_registry[employee_id] = agent_instance

        print(f"[Manager AI] Registered Employee: {employee_id}")

    def list_employees(self):

        print("\nRegistered Employees")

        if not self.employee_registry:
            print("No employees registered.")
            return

        for employee in self.employee_registry:
            print(f"✓ {employee}")

    ####################################################################
    # MASTER STRATEGIC ADVISORY ENGINE
    ####################################################################

    def evaluate_strategic_feasibility(
        self,
        high_level_goal,
        operational_parameters=None
    ):

        params = operational_parameters or {}

        complexity = params.get("complexity_index", 50)

        target_price = params.get("target_price", 0)

        estimated_cac = params.get("estimated_cac", 0)

        tracks_user_data = params.get(
            "requires_personal_data",
            False
        )

        public_exposure = params.get(
            "public_internet_exposure",
            False
        )

        high_concurrency = params.get(
            "high_concurrency",
            False
        )

        database_sharding = params.get(
            "database_sharding",
            False
        )

        critiques = []

        ####################################################
        # Adversarial Analysis
        ####################################################

        if target_price > 0 and target_price <= estimated_cac:

            critiques.append(
                "Pricing model is unsustainable."
            )

        if complexity >= 80:

            critiques.append(
                "System complexity exceeds recommended threshold."
            )

        if tracks_user_data:

            critiques.append(
                "Privacy compliance required (POPIA/GDPR)."
            )

        ####################################################
        # Risk Matrix
        ####################################################

        risk_matrix = {

            "Technical":
                round(complexity * 1.1, 1),

            "Financial":
                15 if target_price > estimated_cac else 85,

            "Legal":
                75 if tracks_user_data else 15,

            "Security":
                65 if public_exposure else 20,

            "Maintenance":
                round((complexity + 20) / 1.5, 1),

            "Scalability":
                70 if (
                    high_concurrency
                    and
                    not database_sharding
                ) else 20,

            "Marketing":
                40,

            "Competition":
                50
        }

        average_risk = sum(
            risk_matrix.values()
        ) / len(risk_matrix)

        health_score = round(
            100 - average_risk,
            1
        )

        ####################################################
        # Verdict
        ####################################################

        if health_score >= 75:

            verdict = "BUILD_IMMEDIATELY"

        elif health_score >= 55:

            verdict = "IMPROVE_IDEA_FIRST"

        else:

            verdict = "CANCEL_PROJECT"

        return {

            "health_score":
                health_score,

            "verdict":
                verdict,

            "execution_allowed":
                verdict != "CANCEL_PROJECT",

            "recommended_next_action":
                "ARCHITECT_AI"
                if verdict == "BUILD_IMMEDIATELY"
                else "FOUNDER_REVIEW",

            "adversarial_critiques":
                critiques,

            "risk_breakdown":
                risk_matrix
        }

    ####################################################################
    # Founder Briefing
    ####################################################################

    def founder_briefing(self, audit):

        print("\n========== STRATEGIC BRIEF ==========")

        print(
            f"Health Score : {audit['health_score']}/100"
        )

        print(
            f"Verdict      : {audit['verdict']}"
        )

        print(
            f"Next Action  : {audit['recommended_next_action']}"
        )

        if audit["adversarial_critiques"]:

            print("\nCritical Findings")

            for finding in audit["adversarial_critiques"]:

                print(f"- {finding}")

        else:

            print("\nNo major strategic concerns detected.")

        print("=====================================")

    ####################################################################
    # Project Creation
    ####################################################################

    def formulate_10_step_plan(
        self,
        high_level_goal,
        operational_parameters=None
    ):

        task_id = f"TSK-{str(uuid.uuid4())[:6].upper()}"

        audit = self.evaluate_strategic_feasibility(
            high_level_goal,
            operational_parameters
        )

        self.founder_briefing(audit)

        task_payload = {

            "task_id":
                task_id,

            "goal":
                high_level_goal,

            "created_at":
                datetime.utcnow().isoformat(),

            "status":
                f"GATE_VERIFICATION_{audit['verdict']}",

            "execution_allowed":
                audit["execution_allowed"],

            "project_health_score":
                audit["health_score"],

            "strategic_audit":
                audit,

            "assigned_worker":
                None,

            "architecture":
                None,

            "code":
                None,

            "review":
                None,

            "tests":
                None,

            "deployment":
                None,

            "milestones":[
                "1. Market Assessment",
                "2. Risk Analysis",
                "3. Architecture",
                "4. Planning",
                "5. Resource Allocation",
                "6. Development",
                "7. Review",
                "8. Testing",
                "9. Deployment",
                "10. Completion"
            ]
        }

        self.memory.write(
            f"active_project_{task_id}",
            task_payload
        )

        print(
            f"\n[Manager AI] Project Created: {task_id}"
        )

        return task_id, audit["execution_allowed"]

    ####################################################################
    # Swarm Dispatch
    ####################################################################

    def dispatch_swarm_worker(
        self,
        task_id,
        worker_id
    ):

        worker_id = worker_id.upper()

        project_key = f"active_project_{task_id}"

        project = self.memory.read(project_key)

        if project is None:

            print("[Manager AI] Project not found.")
            return

        if not project["execution_allowed"]:

            print(
                f"[Manager AI] Execution Blocked for {task_id}"
            )
            return

        if worker_id not in self.employee_registry:

            print(
                f"[Manager AI] Employee '{worker_id}' not registered."
            )
            return

        project["assigned_worker"] = worker_id
        project["status"] = "RESOURCE_ALLOCATED"

        self.memory.write(
            project_key,
            project
        )

        print(
            f"[Manager AI] Dispatching {worker_id}"
        )

        self.employee_registry[
            worker_id
        ].process_project_task(task_id)

    ####################################################################
    # Project Viewer
    ####################################################################

    def show_projects(self):

        print("\nCurrent Project Workspace")

        self.memory.print_memory()
