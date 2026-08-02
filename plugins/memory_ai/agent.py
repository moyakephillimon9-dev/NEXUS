"""
NEXUS
Memory AI — Autonomous Semantic Graph Engine

Module ID : MEMORY-001
Version   : 6.0.0 (Enterprise Master Edition)

PART 1
Core Engine Initialization
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import shutil
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
)

# ==========================================================
# Ultra Performance Event Loop
# ==========================================================

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

# ==========================================================
# Enterprise Logger
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("NEXUS-MEMORY")

# ==========================================================
# Engine Constants
# ==========================================================

ENGINE_NAME = "NEXUS MEMORY ENGINE"

ENGINE_VERSION = "6.0.0"

DATABASE_FILE = "memory/database.json"

BACKUP_FOLDER = "memory/backups"

MAX_BACKUPS = 20

CACHE_VERSION = 2

AUTO_SAVE_INTERVAL = 300

MAINTENANCE_INTERVAL = 86400

# ==========================================================
# Shared Memory Interface
# ==========================================================

class SharedMemoryProtocol(Protocol):

    def read(self, key: str) -> Any:
        ...

    def write(self, key: str, value: Any):
        ...

# ==========================================================
# Knowledge Categories
# ==========================================================

class NodeCategory(str, Enum):

    PROJECT = "projects"

    ARCHITECTURE = "architectures"

    LESSON = "lessons"

    TEMPLATE = "templates"

    FAILURE = "failures"

    SUCCESS = "successes"

    SECURITY = "security"

    TEST = "tests"

    REVIEW = "reviews"

    DEPLOYMENT = "deployments"

# ==========================================================
# Learning Types
# ==========================================================

class LessonType(str, Enum):

    SUCCESS = "SUCCESS"

    FAILURE = "FAILURE"

    WARNING = "WARNING"

    OPTIMIZATION = "OPTIMIZATION"

# ==========================================================
# Node Definition
# ==========================================================

@dataclass(slots=True)
class KnowledgeNode:

    id: str

    category: NodeCategory

    title: str

    payload: Dict[str, Any]

    tags: List[str] = field(default_factory=list)

    score: float = 0.0

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

# ==========================================================
# Memory AI
# ==========================================================

class MemoryAI:

    """
    Enterprise Semantic Knowledge Engine

    Responsibilities

        • Persistent Knowledge Database

        • Pattern Learning

        • Architecture Memory

        • Deployment History

        • Failure Analysis

        • Similarity Search

        • Automatic Backup

        • Self-Healing Database

        • Semantic Graph

        • AI Experience Storage
    """

    def __init__(

        self,

        shared_memory: SharedMemoryProtocol,

        database_path: str = DATABASE_FILE

    ):

        self.memory = shared_memory

        self.database_path = Path(database_path)

        self.backup_path = Path(BACKUP_FOLDER)

        self._lock = asyncio.Lock()

        self._maintenance_task = None

        self._autosave_task = None

        self.cache: Dict[str, Any] = {}

        logger.info("Connecting Memory AI...")

        self._bootstrap()

        logger.info("Memory AI Ready.")

    # ======================================================

    def _bootstrap(self):

        """
        Prepare filesystem and cache.
        """

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.backup_path.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.database_path.exists():

            self.cache = {

                "manifest": {

                    "engine": ENGINE_NAME,

                    "version": ENGINE_VERSION,

                    "created": datetime.now(
                        timezone.utc
                    ).isoformat(),

                    "last_sync": None,

                    "cache_version": CACHE_VERSION

                },

                "graph": {

                    category.value: {}

                    for category in NodeCategory

                }

            }

            with open(
                self.database_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.cache,
                    f,
                    indent=4
                )

            logger.info(
                "Created fresh memory database."
            )

        else:

            with open(
                self.database_path,
                "r",
                encoding="utf-8"
            ) as f:

                self.cache = json.load(f)

            logger.info(
                "Database loaded into RAM cache."
            )

    # ==========================================================
    # ENGINE LIFECYCLE
    # ==========================================================

    async def start(self):
        """
        Starts the Memory AI background services.
        """

        logger.info("Starting Memory AI...")

        self._autosave_task = asyncio.create_task(
            self._autosave_loop()
        )

        self._maintenance_task = asyncio.create_task(
            self._maintenance_loop()
        )

        logger.info("Memory AI Online.")

    async def shutdown(self):
        """
        Gracefully stops Memory AI.
        """

        logger.info("Stopping Memory AI...")

        if self._autosave_task:
            self._autosave_task.cancel()

        if self._maintenance_task:
            self._maintenance_task.cancel()

        try:
            await self._atomic_save()

        except Exception as e:
            logger.error(e)

        logger.info("Memory AI Offline.")

    # ==========================================================
    # DATABASE SAVE ENGINE
    # ==========================================================

    async def _atomic_save(self):
        """
        Safely writes database using atomic replacement.
        """

        async with self._lock:

            temp_file = self.database_path.with_suffix(".tmp")

            self.cache["manifest"]["last_sync"] = (
                datetime.now(timezone.utc).isoformat()
            )

            loop = asyncio.get_running_loop()

            await loop.run_in_executor(

                None,

                self._write_json,

                temp_file,

                self.cache

            )

            if self.database_path.exists():

                await loop.run_in_executor(

                    None,

                    self._create_backup

                )

            os.replace(
                temp_file,
                self.database_path
            )

            logger.info("Database committed successfully.")

    # ==========================================================
    # JSON WRITER
    # ==========================================================

    def _write_json(
        self,
        path: Path,
        data: Dict[str, Any]
    ):

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ==========================================================
    # BACKUP CREATION
    # ==========================================================

    def _create_backup(self):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = (
            self.backup_path /
            f"memory_{timestamp}.bak"
        )

        shutil.copy2(
            self.database_path,
            backup_file
        )

        logger.info(
            f"Backup created -> {backup_file.name}"
        )

    # ==========================================================
    # BACKUP ROTATION
    # ==========================================================

    def _rotate_backups(self):
        """
        Keep only the newest MAX_BACKUPS snapshots.
        """

        backups = sorted(
            self.backup_path.glob("*.bak"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for old_backup in backups[MAX_BACKUPS:]:
            try:
                old_backup.unlink()
                logger.info(
                    f"Removed old backup: {old_backup.name}"
                )
            except Exception as e:
                logger.warning(e)

    # ==========================================================
    # DATABASE RECOVERY
    # ==========================================================

    def _recover_database(self):
        """
        Restore latest healthy snapshot.
        """

        backups = sorted(
            self.backup_path.glob("*.bak"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not backups:
            logger.error(
                "Recovery impossible. No backups found."
            )
            return

        newest = backups[0]

        shutil.copy2(
            newest,
            self.database_path
        )

        with open(
            self.database_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.cache = json.load(f)

        logger.info(
            f"Recovered database from {newest.name}"
        )

    # ==========================================================
    # AUTO SAVE LOOP
    # ==========================================================

    async def _autosave_loop(self):
        """
        Saves database every AUTO_SAVE_INTERVAL seconds.
        """

        while True:

            try:

                await asyncio.sleep(
                    AUTO_SAVE_INTERVAL
                )

                await self._atomic_save()

            except asyncio.CancelledError:
                break

            except Exception as e:
                logger.error(e)

    # ==========================================================
    # MAINTENANCE LOOP
    # ==========================================================

    async def _maintenance_loop(self):
        """
        Daily optimization worker.
        """

        while True:

            try:

                await asyncio.sleep(
                    MAINTENANCE_INTERVAL
                )

                self._rotate_backups()

                logger.info(
                    "Maintenance completed."
                )

            except asyncio.CancelledError:
                break

            except Exception as e:
                logger.error(e)

    # ==========================================================
    # PROJECT LEARNING ENGINE
    # ==========================================================

    async def learn_project(
        self,
        task_id: str
    ):
        """
        Learns from a completed project and stores
        semantic knowledge inside the graph.
        """

        key = f"active_project_{task_id}"

        loop = asyncio.get_running_loop()

        project = await loop.run_in_executor(
            None,
            self.memory.read,
            key
        )

        if not project:
            logger.warning(
                f"Project {task_id} not found."
            )
            return

        async with self._lock:

            # --------------------------------------
            # Store Project
            # --------------------------------------

            project_node = KnowledgeNode(

                id=task_id,

                category=NodeCategory.PROJECT,

                title=project.get(
                    "goal",
                    "Unknown"
                ),

                payload=project,

                tags=[
                    project.get(
                        "architecture",
                        {}
                    ).get(
                        "framework",
                        "Unknown"
                    ),
                    project.get(
                        "status",
                        "UNKNOWN"
                    )
                ]

            )

            self.cache["graph"][
                NodeCategory.PROJECT.value
            ][task_id] = {

                "id": project_node.id,

                "title": project_node.title,

                "payload": project_node.payload,

                "tags": project_node.tags,

                "created_at": project_node.created_at

            }

            # --------------------------------------
            # Learn Architecture
            # --------------------------------------

            architecture = project.get(
                "architecture",
                {}
            )

            framework = architecture.get(
                "framework"
            )

            if framework:

                self.cache["graph"][
                    NodeCategory.ARCHITECTURE.value
                ][framework] = architecture

            # --------------------------------------
            # Learn Deployment
            # --------------------------------------

            deployment = project.get(
                "deployment",
                {}
            )

            if deployment:

                self.cache["graph"][
                    NodeCategory.DEPLOYMENT.value
                ][task_id] = deployment

            # --------------------------------------
            # Learn Review
            # --------------------------------------

            review = project.get(
                "review",
                {}
            )

            self.cache["graph"][
                NodeCategory.REVIEW.value
            ][task_id] = review

            # --------------------------------------
            # Learn Tests
            # --------------------------------------

            tests = project.get(
                "tests",
                {}
            )

            self.cache["graph"][
                NodeCategory.TEST.value
            ][task_id] = tests

            await self._atomic_save()

            logger.info(
                f"Learned project {task_id}"
            )

    # ==========================================================
    # SUCCESS / FAILURE LEARNING ENGINE
    # ==========================================================

    async def learn_outcome(
        self,
        task_id: str
    ):
        """
        Learns whether a project succeeded or failed and
        stores reusable experience.
        """

        project = self.cache["graph"][
            NodeCategory.PROJECT.value
        ].get(task_id)

        if project is None:
            return

        payload = project["payload"]

        review = payload.get("review", {})
        tests = payload.get("tests", {})

        approved = review.get("approved", False)
        passed = tests.get("passed", False)

        lesson = {
            "task": task_id,
            "goal": payload.get("goal"),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

        if approved and passed:

            lesson["type"] = LessonType.SUCCESS.value

            lesson["framework"] = payload.get(
                "architecture",
                {}
            ).get(
                "framework"
            )

            lesson["coverage"] = tests.get(
                "coverage",
                0
            )

            lesson["quality_score"] = review.get(
                "quality_score",
                0
            )

            self.cache["graph"][
                NodeCategory.SUCCESS.value
            ][task_id] = lesson

        else:

            lesson["type"] = LessonType.FAILURE.value

            lesson["issues"] = review.get(
                "issues",
                []
            )

            lesson["execution_log"] = tests.get(
                "execution_log",
                ""
            )

            self.cache["graph"][
                NodeCategory.FAILURE.value
            ][task_id] = lesson

        await self._atomic_save()

    # ==========================================================
    # TEMPLATE EXTRACTION ENGINE
    # ==========================================================

    async def extract_template(
        self,
        task_id: str
    ):
        """
        Creates reusable templates from successful projects.
        """

        success = self.cache["graph"][
            NodeCategory.SUCCESS.value
        ].get(task_id)

        if success is None:
            return

        project = self.cache["graph"][
            NodeCategory.PROJECT.value
        ][task_id]["payload"]

        template_id = str(uuid.uuid4())

        template = {

            "id": template_id,

            "source_task": task_id,

            "goal": project.get("goal"),

            "architecture": project.get(
                "architecture"
            ),

            "review": project.get(
                "review"
            ),

            "tests": project.get(
                "tests"
            ),

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat()

        }

        self.cache["graph"][
            NodeCategory.TEMPLATE.value
        ][template_id] = template

        await self._atomic_save()

        logger.info(
            f"Template created from {task_id}"
        )

    # ==========================================================
    # SEMANTIC SEARCH ENGINE
    # ==========================================================

    async def search(
        self,
        keyword: str,
        category: Optional[NodeCategory] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph using keywords.
        """

        keyword = keyword.lower()

        results = []

        async with self._lock:

            if category:

                buckets = {
                    category.value:
                    self.cache["graph"].get(category.value, {})
                }

            else:

                buckets = self.cache["graph"]

            for bucket_name, bucket in buckets.items():

                for node_id, node in bucket.items():

                    text = json.dumps(node).lower()

                    if keyword in text:

                        results.append({

                            "category": bucket_name,

                            "id": node_id,

                            "score": text.count(keyword),

                            "node": node

                        })

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results

    # ==========================================================
    # SIMILAR PROJECT ENGINE
    # ==========================================================

    async def find_similar_projects(
        self,
        framework: str
    ) -> List[Dict[str, Any]]:
        """
        Finds projects using the same framework.
        """

        framework = framework.lower()

        matches = []

        projects = self.cache["graph"][
            NodeCategory.PROJECT.value
        ]

        async with self._lock:

            for task_id, node in projects.items():

                payload = node["payload"]

                architecture = payload.get(
                    "architecture",
                    {}
                )

                if architecture.get(
                    "framework",
                    ""
                ).lower() == framework:

                    matches.append({

                        "task_id": task_id,

                        "goal": payload.get("goal"),

                        "status": payload.get("status"),

                        "review_score": payload.get(
                            "review",
                            {}
                        ).get(
                            "quality_score",
                            0
                        ),

                        "coverage": payload.get(
                            "tests",
                            {}
                        ).get(
                            "coverage",
                            0
                        )

                    })

        matches.sort(

            key=lambda x: (
                x["review_score"],
                x["coverage"]
            ),

            reverse=True

        )

        return matches

    # ==========================================================
    # TEMPLATE RETRIEVAL
    # ==========================================================

    async def get_templates(
        self
    ) -> List[Dict[str, Any]]:
        """
        Returns all reusable templates.
        """

        async with self._lock:

            return list(

                self.cache["graph"][
                    NodeCategory.TEMPLATE.value
                ].values()

            )

    # ==========================================================
    # KNOWLEDGE GRAPH SUMMARY
    # ==========================================================

    async def graph_summary(self) -> Dict[str, int]:
        """
        Returns graph statistics.
        """

        async with self._lock:

            summary = {}

            for category in NodeCategory:

                summary[category.value] = len(

                    self.cache["graph"].get(
                        category.value,
                        {}
                    )

                )

            return summary

    # ==========================================================
    # AI RECOMMENDATION ENGINE
    # ==========================================================

    async def recommend_for_project(
        self,
        goal: str,
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates intelligent recommendations from everything
        Memory AI has learned.
        """

        recommendation = {
            "goal": goal,
            "recommended_framework": None,
            "recommended_templates": [],
            "best_practices": [],
            "similar_projects": [],
            "estimated_success_score": 0.0
        }

        async with self._lock:

            # --------------------------------------------------
            # Similar Successful Projects
            # --------------------------------------------------

            success_nodes = self.cache["graph"][
                NodeCategory.SUCCESS.value
            ]

            for task_id in success_nodes:

                project = self.cache["graph"][
                    NodeCategory.PROJECT.value
                ].get(task_id)

                if not project:
                    continue

                payload = project["payload"]

                if goal.lower() in payload.get(
                    "goal",
                    ""
                ).lower():

                    recommendation[
                        "similar_projects"
                    ].append({

                        "task_id": task_id,

                        "goal": payload.get("goal"),

                        "framework": payload.get(
                            "architecture",
                            {}
                        ).get(
                            "framework"
                        ),

                        "review_score": payload.get(
                            "review",
                            {}
                        ).get(
                            "quality_score",
                            0
                        ),

                        "coverage": payload.get(
                            "tests",
                            {}
                        ).get(
                            "coverage",
                            0
                        )

                    })

            # --------------------------------------------------
            # Framework Recommendation
            # --------------------------------------------------

            if framework:

                recommendation[
                    "recommended_framework"
                ] = framework

            elif recommendation["similar_projects"]:

                recommendation[
                    "recommended_framework"
                ] = recommendation[
                    "similar_projects"
                ][0]["framework"]

            # --------------------------------------------------
            # Template Recommendation
            # --------------------------------------------------

            templates = self.cache["graph"][
                NodeCategory.TEMPLATE.value
            ]

            for template in templates.values():

                if goal.lower() in template.get(
                    "goal",
                    ""
                ).lower():

                    recommendation[
                        "recommended_templates"
                    ].append(template["id"])

            # --------------------------------------------------
            # Best Practices
            # --------------------------------------------------

            recommendation["best_practices"] = [

                "Run Reviewer AI before deployment.",

                "Maintain minimum 90% test coverage.",

                "Reuse successful architecture patterns.",

                "Always generate deployment manifest.",

                "Archive every completed project.",

                "Create reusable templates.",

                "Record lessons from failures."

            ]

            # --------------------------------------------------
            # Estimated Success Score
            # --------------------------------------------------

            count = len(
                recommendation["similar_projects"]
            )

            if count == 0:

                recommendation[
                    "estimated_success_score"
                ] = 60.0

            elif count < 5:

                recommendation[
                    "estimated_success_score"
                ] = 80.0

            else:

                recommendation[
                    "estimated_success_score"
                ] = 95.0

        return recommendation

    # ==========================================================
    # MEMORY ANALYTICS ENGINE
    # ==========================================================

    async def analytics(self) -> Dict[str, Any]:
        """
        Computes enterprise-wide analytics for the entire
        Nexus Software Factory.
        """

        async with self._lock:

            projects = self.cache["graph"][
                NodeCategory.PROJECT.value
            ]

            total_projects = len(projects)

            deployed = 0
            failed = 0

            framework_usage: Dict[str, int] = {}

            average_review = 0.0
            average_coverage = 0.0

            best_project = None
            highest_score = -1

            for task_id, node in projects.items():

                payload = node["payload"]

                # -----------------------------
                # Deployment statistics
                # -----------------------------

                if payload.get("deployment_complete"):
                    deployed += 1

                if payload.get("status") == "FAILED":
                    failed += 1

                # -----------------------------
                # Framework usage
                # -----------------------------

                framework = payload.get(
                    "architecture",
                    {}
                ).get(
                    "framework",
                    "Unknown"
                )

                framework_usage.setdefault(
                    framework,
                    0
                )

                framework_usage[framework] += 1

                # -----------------------------
                # Review score
                # -----------------------------

                review_score = payload.get(
                    "review",
                    {}
                ).get(
                    "quality_score",
                    0
                )

                average_review += review_score

                # -----------------------------
                # Coverage
                # -----------------------------

                coverage = payload.get(
                    "tests",
                    {}
                ).get(
                    "coverage",
                    0
                )

                average_coverage += coverage

                # -----------------------------
                # Best project
                # -----------------------------

                score = review_score + coverage

                if score > highest_score:

                    highest_score = score

                    best_project = {

                        "task_id": task_id,

                        "goal": payload.get("goal"),

                        "framework": framework,

                        "review_score": review_score,

                        "coverage": coverage

                    }

            # ---------------------------------------
            # Normalize values
            # ---------------------------------------

            if total_projects:

                average_review /= total_projects
                average_coverage /= total_projects

            deployment_rate = (
                deployed / total_projects * 100
                if total_projects else 0
            )

            failure_rate = (
                failed / total_projects * 100
                if total_projects else 0
            )

            return {

                "total_projects": total_projects,

                "deployment_rate": round(
                    deployment_rate,
                    2
                ),

                "failure_rate": round(
                    failure_rate,
                    2
                ),

                "average_review_score": round(
                    average_review,
                    2
                ),

                "average_test_coverage": round(
                    average_coverage,
                    2
                ),

                "framework_usage": framework_usage,

                "best_project": best_project

            }

    # ==========================================================
    # TOP PROJECTS
    # ==========================================================

    async def top_projects(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Returns the highest-performing projects.
        """

        ranking = []

        async with self._lock:

            for task_id, node in self.cache["graph"][
                NodeCategory.PROJECT.value
            ].items():

                payload = node["payload"]

                review = payload.get(
                    "review",
                    {}
                ).get(
                    "quality_score",
                    0
                )

                coverage = payload.get(
                    "tests",
                    {}
                ).get(
                    "coverage",
                    0
                )

                ranking.append({

                    "task_id": task_id,

                    "goal": payload.get("goal"),

                    "framework": payload.get(
                        "architecture",
                        {}
                    ).get("framework"),

                    "score": review + coverage,

                    "review": review,

                    "coverage": coverage

                })

        ranking.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranking[:limit]

    async def _persist_state_to_disk(self) -> None:
        """
        Safe transactional write.

        Stage 1:
            Write temporary file.

        Stage 2:
            Backup previous database.

        Stage 3:
            Atomic replace.
        """

        # NOTE: this method uses self.database_path (same attr as _atomic_save).
        # An older revision used self.db_path which was never assigned → AttributeError.
        tmp_file = self.database_path.with_suffix(".tmp")

        self._state_cache["manifest"]["last_sync"] = (
            datetime.now(timezone.utc).isoformat()
        )

        # Ensure directory exists before writing
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            loop = asyncio.get_running_loop()

            await loop.run_in_executor(
                None,
                self._write_json_worker,
                tmp_file,
                self._state_cache
            )

            if self.database_path.exists():

                backup_name = (
                    f"snapshot_{int(datetime.now().timestamp())}.bak"
                )

                backup_target = self.backup_path / backup_name

                await loop.run_in_executor(
                    None,
                    shutil.copy2,
                    self.database_path,
                    backup_target
                )

            os.replace(tmp_file, self.database_path)

            logger.info("💾 Memory database committed successfully.")

        except Exception as exc:

            logger.critical(
                "Database transaction failed: %s",
                exc
            )

            if tmp_file.exists():
                tmp_file.unlink()

            with open(
                self.database_path,
                "r",
                encoding="utf-8"
            ) as restore:

                self._state_cache = json.load(restore)

            raise IOError(
                "Memory rollback completed successfully."
            ) from exc

    # ==========================================================
    # JSON WRITE WORKER
    # ==========================================================

    @staticmethod
    def _write_json_worker(
        path: Path,
        data: Dict[str, Any]
    ) -> None:
        """
        Low-level JSON serialization worker.
        """

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as outfile:

            json.dump(
                data,
                outfile,
                indent=4,
                ensure_ascii=False
            )

    # ==========================================================
    # BACKUP MAINTENANCE
    # ==========================================================

    def _cleanup_backups(self) -> None:
        """
        Keeps only the newest MAX_BACKUPS backups.
        """

        backups = sorted(

            self.backup_dir.glob("*.bak"),

            key=lambda p: p.stat().st_mtime,

            reverse=True

        )

        for old in backups[MAX_BACKUPS:]:

            try:

                old.unlink()

                logger.info(
                    f"Deleted old backup: {old.name}"
                )

            except Exception as exc:

                logger.warning(exc)

    # ==========================================================
    # BACKGROUND MAINTENANCE
    # ==========================================================

    async def _background_compaction_worker(self):
        """
        Daily optimization cycle.
        """

        while True:

            try:

                await asyncio.sleep(86400)

                self._cleanup_backups()

                self.statistics()

                logger.info(
                    "Memory maintenance cycle complete."
                )

            except asyncio.CancelledError:

                logger.info(
                    "Maintenance worker stopped."
                )

                break

            except Exception as exc:

                logger.exception(exc)

    # ==========================================================
    # MEMORY EXPORT
    # ==========================================================

    async def export_database(
        self,
        destination: str
    ) -> None:
        """
        Export complete knowledge database.
        """

        async with self._lock:

            shutil.copy2(
                self.db_path,
                destination
            )

            logger.info(
                f"Database exported -> {destination}"
            )

    # ==========================================================
    # MEMORY IMPORT
    # ==========================================================

    async def import_database(
        self,
        source: str
    ) -> None:
        """
        Import an external database.
        """

        async with self._lock:

            shutil.copy2(
                source,
                self.db_path
            )

            with open(
                self.db_path,
                "r",
                encoding="utf-8"
            ) as infile:

                self._state_cache = json.load(
                    infile
                )

            logger.info(
                "External knowledge base imported."
            )

    # ==========================================================
    # ENGINE INFORMATION
    # ==========================================================

    def engine_info(self) -> Dict[str, Any]:
        """
        Returns engine metadata.
        """

        return {

            "engine": ENGINE_NAME,

            "version": ENGINE_VERSION,

            "database": str(self.db_path),

            "backups": str(self.backup_dir),

            "cache_version": CACHE_VERSION,

            "categories": [

                category.value

                for category in NodeCategory

            ]

        }

    # ==========================================================
    # SYNCHRONOUS PIPELINE ENTRY POINT
    # ==========================================================

    def _sync_save(self):
        """
        Synchronous atomic save — safe to call outside an event loop.
        Used by process_project_task so the pipeline never needs asyncio.
        """
        temp = self.database_path.with_suffix(".tmp")
        self.cache["manifest"]["last_sync"] = (
            datetime.now(timezone.utc).isoformat()
        )
        self._write_json(temp, self.cache)
        if self.database_path.exists():
            self._create_backup()
        os.replace(temp, self.database_path)

    def process_project_task(self, task_id: str):
        """
        Synchronous entry point called by ManagerAI.dispatch_swarm_worker().

        Learns from the completed project — stores it in the knowledge
        graph, records the outcome as a success or failure lesson, and
        extracts a reusable template from successful builds.
        """

        key     = f"active_project_{task_id}"
        project = self.memory.read(key)

        if project is None:
            print("[Memory AI] Project not found.")
            return

        print(f"[Memory AI] Learning from project: {task_id}")

        graph = self.cache["graph"]

        # ── Store project node ─────────────────────────────────── #

        graph[NodeCategory.PROJECT.value][task_id] = {
            "id":         task_id,
            "title":      project.get("goal", "Unknown"),
            "payload":    project,
            "tags": [
                project.get("architecture", {}).get("framework", "Unknown"),
                project.get("status", "UNKNOWN"),
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # ── Architecture ───────────────────────────────────────── #

        architecture = project.get("architecture") or {}
        framework    = architecture.get("framework")
        if framework:
            graph[NodeCategory.ARCHITECTURE.value][framework] = architecture

        # ── Deployment ─────────────────────────────────────────── #

        deployment = project.get("deployment") or {}
        if deployment:
            graph[NodeCategory.DEPLOYMENT.value][task_id] = deployment

        # ── Review + Tests ─────────────────────────────────────── #

        review = project.get("review") or {}
        tests  = project.get("tests")  or {}

        graph[NodeCategory.REVIEW.value][task_id] = review
        graph[NodeCategory.TEST.value][task_id]   = tests

        # ── Outcome lesson ─────────────────────────────────────── #

        approved = review.get("approved", False)
        passed   = tests.get("passed",   False)

        lesson = {
            "task":      task_id,
            "goal":      project.get("goal"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if approved and passed:
            lesson["type"]          = LessonType.SUCCESS.value
            lesson["framework"]     = framework
            lesson["coverage"]      = tests.get("coverage", 0)
            lesson["quality_score"] = review.get("quality_score", 0)
            graph[NodeCategory.SUCCESS.value][task_id] = lesson

            # Template from successful project
            template_id = str(uuid.uuid4())
            graph[NodeCategory.TEMPLATE.value][template_id] = {
                "id":           template_id,
                "source_task":  task_id,
                "goal":         project.get("goal"),
                "architecture": architecture,
                "review":       review,
                "tests":        tests,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            print(f"[Memory AI] Success lesson recorded. Template extracted.")

        else:
            lesson["type"]          = LessonType.FAILURE.value
            lesson["issues"]        = review.get("issues", [])
            lesson["execution_log"] = tests.get("execution_log", "")
            graph[NodeCategory.FAILURE.value][task_id] = lesson
            print(f"[Memory AI] Failure lesson recorded.")

        # ── Update project status ─────────────────────────────────── #

        project["status"] = "COMPLETED"
        self.memory.write(key, project)

        # ── Persist ────────────────────────────────────────────── #

        self._sync_save()

        total_projects  = len(graph[NodeCategory.PROJECT.value])
        total_successes = len(graph[NodeCategory.SUCCESS.value])
        total_failures  = len(graph[NodeCategory.FAILURE.value])
        total_templates = len(graph[NodeCategory.TEMPLATE.value])

        print(f"[Memory AI] Projects   : {total_projects}")
        print(f"[Memory AI] Successes  : {total_successes}")
        print(f"[Memory AI] Failures   : {total_failures}")
        print(f"[Memory AI] Templates  : {total_templates}")
        print(f"[Memory AI] Database   : {self.database_path}")

