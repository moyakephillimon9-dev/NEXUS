"""
NEXUS
Deployment AI — Enterprise Release Engineering Engine

Module ID : DEPLOY-001
Version   : 1.0.0
"""

import os
import json
import hashlib
from datetime import datetime


class DeploymentAI:
    """
    Enterprise Deployment Engine

    Responsibilities
    ----------------
    • Verify deployment readiness
    • Build production package
    • Generate release manifest
    • Archive completed project
    • Maintain deployment history
    • Support rollback metadata
    """

    def __init__(
        self,
        shared_memory,
        deployment_root="deployments",
        project_vault="projects"
    ):
        self.memory = shared_memory
        self.deployment_root = deployment_root
        self.project_vault = project_vault

        os.makedirs(self.deployment_root, exist_ok=True)
        os.makedirs(self.project_vault, exist_ok=True)

        print("[Deployment AI] Connected to Shared Memory.")

    def start(self):
        print("[Deployment AI] Enterprise Release Engine Ready.")

    ##############################################################
    # INTERNAL UTILITIES
    ##############################################################

    def _checksum(self, text: str):
        return hashlib.sha256(text.encode()).hexdigest()

    def _sanitize_name(self, text: str, max_len: int = 50) -> str:
        # Use only the first line — vision documents can be thousands of chars
        first_line = text.strip().splitlines()[0] if text.strip() else "project"
        slug = (
            first_line.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )
        # Strip non-alphanumeric/underscore chars and enforce max length
        import re as _re
        slug = _re.sub(r"[^\w]", "", slug)
        return slug[:max_len] if slug else "project"

    ##############################################################
    # RELEASE GATE
    ##############################################################

    def verify_release_gate(self, project):

        review = project.get("review")
        tests = project.get("tests")

        if review is None:
            return False, "Reviewer AI has not approved the project."

        if tests is None:
            return False, "Tester AI has not validated the project."

        if not review.get("approved", False):
            return False, "Code review rejected."

        if not tests.get("passed", False):
            return False, "Runtime tests failed."

        return True, "Release Gate Passed"

    ##############################################################
    # ARTIFACT BUILD
    ##############################################################

    def generate_release_artifacts(self, task_id, project):

        goal = self._sanitize_name(project["goal"])

        folder = os.path.join(
            self.deployment_root,
            f"{task_id}_{goal}"
        )

        os.makedirs(folder, exist_ok=True)

        code = project.get("code", {})

        if isinstance(code, dict):
            source = code.get("source", "")
        else:
            source = str(code)

        ##########################################

        # ── Inject NEXUS branding footer ──────────────────────────────
        project_type = (
            project.get("project_type")
            or project.get("research", {}).get("project_type", "")
            or project.get("architecture", {}).get("project_type", "")
            or ""
        ).lower()

        _BRANDING = {
            "game"        : "# 🎮 Powered by NEXUS — nexus.ai",
            "web_app"     : "# 🌐 Created with NEXUS — nexus.ai",
            "rest_api"    : "# 🔌 Created with NEXUS — nexus.ai",
            "chat_app"    : "# 💬 Created with NEXUS — nexus.ai",
            "ai_system"   : "# 🤖 Built with NEXUS AI — nexus.ai",
            "desktop_gui" : "# 🖥  Crafted with NEXUS — nexus.ai",
            "data_analyzer": "# 📊 Powered by NEXUS — nexus.ai",
            "todo_app"    : "# ✅ Made with NEXUS — nexus.ai",
            "calculator"  : "# 🔢 Made with NEXUS — nexus.ai",
            "inventory"   : "# 📦 Built with NEXUS — nexus.ai",
            "scheduler"   : "# 📅 Built with NEXUS — nexus.ai",
            "file_manager": "# 📁 Built with NEXUS — nexus.ai",
        }
        branding_line = _BRANDING.get(project_type, "# ⚡ Built with NEXUS — nexus.ai")
        branded_source = source.rstrip() + f"\n\n\n{branding_line}\n"

        with open(os.path.join(folder, "main.py"), "w") as f:
            f.write(branded_source)

        ##########################################

        # Use requirements detected by Coder AI for this project type
        requirements = code.get("requirements", []) if isinstance(code, dict) else []

        with open(os.path.join(folder, "requirements.txt"), "w") as f:
            f.write("\n".join(requirements) if requirements else "# No external dependencies\n")

        ##########################################

        architecture = project.get("architecture", {})

        readme = f"""# {project['goal']}

Generated by NEXUS Deployment AI

Task ID:
{task_id}

Framework:
{architecture.get("framework","Unknown")}

Language:
{architecture.get("language","Python")}

Database:
{architecture.get("database","Unknown")}

Deployment Time:
{datetime.utcnow().isoformat()}

Run

pip install -r requirements.txt

python main.py
"""

        with open(os.path.join(folder, "README.md"), "w") as f:
            f.write(readme)

        return folder

    ##############################################################
    # RELEASE MANIFEST
    ##############################################################

    def create_manifest(self, folder, task_id, project):

        code = project["code"]["source"]

        manifest = {
            "task_id": task_id,
            "goal": project["goal"],
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "checksum": self._checksum(code),
            "architecture": project.get("architecture"),
            "review": project.get("review"),
            "tests": project.get("tests")
        }

        with open(
            os.path.join(folder, "deployment.json"),
            "w"
        ) as f:
            json.dump(manifest, f, indent=4)

        return manifest

    ##############################################################
    # ARCHIVE PROJECT
    ##############################################################

    def archive_project(self, task_id, project):

        archive = os.path.join(
            self.project_vault,
            f"{task_id}.json"
        )

        with open(archive, "w") as f:
            json.dump(project, f, indent=4)

        return archive

    ##############################################################
    # DEPLOY
    ##############################################################

    def deploy(self, task_id, project):

        folder = self.generate_release_artifacts(
            task_id,
            project
        )

        manifest = self.create_manifest(
            folder,
            task_id,
            project
        )

        archive = self.archive_project(
            task_id,
            project
        )

        project["deployment"] = {
            "status": "DEPLOYED",
            "deployment_time": datetime.utcnow().isoformat(),
            "deployment_path": folder,
            "archive": archive,
            "manifest": manifest
        }

        project["deployment_ready"] = True
        project["deployment_complete"] = True
        project["status"] = "DEPLOYED"

        return folder

    ##############################################################
    # ROLLBACK
    ##############################################################

    def rollback(self, task_id):

        archive = os.path.join(
            self.project_vault,
            f"{task_id}.json"
        )

        if not os.path.exists(archive):
            print("[Deployment AI] Rollback archive not found.")
            return

        with open(archive) as f:
            project = json.load(f)

        self.memory.write(
            f"active_project_{task_id}",
            project
        )

        print(f"[Deployment AI] Rollback complete -> {task_id}")

    ##############################################################
    # MAIN ENTRY
    ##############################################################

    def process_project_task(self, task_id):

        key = f"active_project_{task_id}"

        project = self.memory.read(key)

        if project is None:
            print("[Deployment AI] Project not found.")
            return

        approved, reason = self.verify_release_gate(project)

        if not approved:
            print(f"[Deployment AI] RELEASE BLOCKED -> {reason}")
            return

        print("[Deployment AI] Release Gate Passed.")
        print("[Deployment AI] Building production package...")

        folder = self.deploy(task_id, project)

        self.memory.write(key, project)

        print("[Deployment AI] Deployment Successful.")
        print(f"[Deployment AI] Package -> {folder}")
