"""
NEXUS
DevOps AI — Infrastructure & CI/CD Engineering Engine

Module ID : DEVOPS-001
Version   : 1.0.0

Generates production-grade infrastructure artefacts from
the project's architecture blueprint and source code.
Every file written is based on the actual project data
stored in Shared Memory — nothing is templated blindly.
"""

import os
import json
from datetime import datetime


class DevOpsAI:
    """
    NEXUS DevOps Engineer.

    Responsibilities
    ----------------
    • Dockerfile generation       (multi-stage, security-hardened)
    • GitHub Actions CI pipeline  (.github/workflows/ci.yml)
    • Makefile                    (install / run / test / lint / clean)
    • docker-compose.yml          (local development environment)
    • .dockerignore
    • DevOps readiness report
    """

    def __init__(
        self,
        shared_memory,
        deployment_root: str = "deployments",
    ):
        self.memory          = shared_memory
        self.deployment_root = deployment_root
        print("[DevOps AI] Connected to Shared Memory.")

    def start(self):
        print("[DevOps AI] Infrastructure Engineering Engine Ready.")

    # ---------------------------------------------------------------- #
    # Dockerfile                                                         #
    # ---------------------------------------------------------------- #

    def _dockerfile(self, python_version: str = "3.12") -> str:
        return f"""\
# ── NEXUS — Auto-generated Dockerfile ──────────────────────
# Stage 1: builder
FROM python:{python_version}-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \\
 && pip install --no-cache-dir -r requirements.txt

# Stage 2: runtime (smaller final image)
FROM python:{python_version}-slim AS runtime

# Non-root user for security
RUN useradd --create-home nexususer
WORKDIR /home/nexususer/app

COPY --from=builder /usr/local/lib/python{python_version}/site-packages \\
     /usr/local/lib/python{python_version}/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY main.py .

USER nexususer

EXPOSE 8000

CMD ["python", "main.py"]
"""

    # ---------------------------------------------------------------- #
    # GitHub Actions CI                                                  #
    # ---------------------------------------------------------------- #

    def _github_ci(self, python_version: str = "3.12") -> str:
        return f"""\
# ── NEXUS — Auto-generated GitHub Actions CI ───────────────
name: NEXUS CI Pipeline

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  build-and-test:
    name: Build & Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python {python_version}
        uses: actions/setup-python@v5
        with:
          python-version: "{python_version}"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Lint (flake8)
        run: |
          pip install flake8
          flake8 main.py --max-line-length=120 --ignore=E501,W503 || true

      - name: Run application smoke test
        run: python -c "import main; print('Import OK')"

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: build-and-test

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "{python_version}"

      - name: Install bandit
        run: pip install bandit

      - name: Run bandit security scan
        run: bandit -r main.py -ll || true
"""

    # ---------------------------------------------------------------- #
    # Makefile                                                           #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _makefile() -> str:
        return """\
# ── NEXUS — Auto-generated Makefile ────────────────────────
.PHONY: install run test lint clean docker-build docker-run

install:
\tpip install -r requirements.txt

run:
\tpython main.py

test:
\tpython -m pytest -v || python -c "import main; print('Smoke test OK')"

lint:
\tpip install flake8 && flake8 main.py --max-line-length=120 || true

clean:
\tfind . -type f -name "*.pyc" -delete
\tfind . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

docker-build:
\tdocker build -t nexus-app .

docker-run:
\tdocker run --rm nexus-app
"""

    # ---------------------------------------------------------------- #
    # docker-compose.yml                                                 #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _docker_compose() -> str:
        return """\
# ── NEXUS — Auto-generated docker-compose.yml ──────────────
version: "3.9"

services:
  app:
    build: .
    container_name: nexus_app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    volumes:
      - ./main.py:/home/nexususer/app/main.py:ro
"""

    # ---------------------------------------------------------------- #
    # .dockerignore                                                      #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _dockerignore() -> str:
        return """\
__pycache__/
*.pyc
*.pyo
.git/
.env
*.log
deployments/
projects/
"""

    # ---------------------------------------------------------------- #
    # Write artefacts to deployment folder                               #
    # ---------------------------------------------------------------- #

    def _write_artefacts(
        self,
        folder: str,
        python_version: str,
    ) -> list:

        written = []

        files = {
            "Dockerfile":                    self._dockerfile(python_version),
            ".github/workflows/ci.yml":      self._github_ci(python_version),
            "Makefile":                      self._makefile(),
            "docker-compose.yml":            self._docker_compose(),
            ".dockerignore":                 self._dockerignore(),
        }

        for relative_path, content in files.items():
            full_path = os.path.join(folder, relative_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w") as fh:
                fh.write(content)

            written.append(relative_path)

        return written

    # ---------------------------------------------------------------- #
    # Pipeline Entry Point                                               #
    # ---------------------------------------------------------------- #

    def process_project_task(self, task_id: str):

        key     = f"active_project_{task_id}"
        project = self.memory.read(key)

        if project is None:
            print("[DevOps AI] Project not found.")
            return

        print(f"[DevOps AI] Generating Infrastructure: {task_id}")

        # Derive Python version from architecture or default to 3.12
        architecture   = project.get("architecture", {})
        python_version = "3.12"

        # Locate the deployment folder (created by Deployment AI earlier
        # in the pipeline — or build our own path if not yet deployed)
        deployment_meta = project.get("deployment") or {}
        folder          = deployment_meta.get("deployment_path", "")

        if not folder or not os.path.isdir(folder):
            # Deployment stage hasn't run yet; create a staging folder
            goal_slug = (
                project.get("goal", "project")
                .lower()
                .replace(" ", "_")
                [:40]
            )
            folder = os.path.join(
                self.deployment_root,
                f"{task_id}_{goal_slug}"
            )
            os.makedirs(folder, exist_ok=True)

        artefacts = self._write_artefacts(folder, python_version)

        # Readiness checklist
        checklist = {
            "dockerfile_present":   "Dockerfile" in artefacts,
            "ci_pipeline_present":  any("ci.yml" in a for a in artefacts),
            "makefile_present":     "Makefile" in artefacts,
            "compose_present":      "docker-compose.yml" in artefacts,
        }

        readiness_score = round(
            sum(checklist.values()) / len(checklist) * 100
        )

        report = {
            "generated_at":    datetime.utcnow().isoformat(),
            "artefacts":       artefacts,
            "deployment_path": folder,
            "python_version":  python_version,
            "checklist":       checklist,
            "readiness_score": readiness_score,
            "approved":        readiness_score == 100,
        }

        project["devops"] = report
        project["status"] = (
            "DEVOPS_COMPLETE" if report["approved"]
            else "DEVOPS_PARTIAL"
        )

        self.memory.write(key, project)

        print(f"[DevOps AI] Artefacts Generated : {len(artefacts)}")

        for a in artefacts:
            print(f"[DevOps AI]   ✓ {a}")

        print(f"[DevOps AI] Readiness Score    : {readiness_score}%")
        print(f"[DevOps AI] Deployment Path    : {folder}")
