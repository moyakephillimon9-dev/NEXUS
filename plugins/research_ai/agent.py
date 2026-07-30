"""
NEXUS
Research AI — Permanent Intelligence System

Module ID : RESEARCH-001
Version   : 1.0.0

Researches project topics from multiple internal sources,
verifies findings, and permanently stores verified knowledge
so the same topic is never researched twice unless updates
are required.

Sources consulted
-----------------
1. Internal engineering pattern library (curated knowledge)
2. Memory AI historical database   (past project outcomes)
3. Goal semantic analysis           (concept extraction)
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


# ------------------------------------------------------------------ #
# Constants                                                            #
# ------------------------------------------------------------------ #

KB_FILE      = Path("research/knowledge_base.json")
KB_BACKUP    = Path("research/backups")
ENGINE_NAME  = "NEXUS RESEARCH ENGINE"
ENGINE_VER   = "1.0.0"
MEMORY_DB    = Path("memory/database.json")


# ------------------------------------------------------------------ #
# Internal Engineering Pattern Library                                 #
# ------------------------------------------------------------------ #

_PATTERNS: dict = {
    "calculator": {
        "paradigm":   "Functional",
        "patterns":   ["REPL Loop", "Function-per-operation", "Error Boundaries"],
        "stack":      {"language": "Python", "testing": "unittest", "deps": []},
        "complexity": "LOW",
        "hours":      2,
        "risks":      ["Division by zero", "Input validation"],
        "best_practices": [
            "Separate computation from presentation.",
            "Validate all inputs before processing.",
            "Use Decimal for financial calculations.",
        ],
    },
    "todo_app": {
        "paradigm":   "CRUD",
        "patterns":   ["Repository Pattern", "Command Pattern", "Persistent Storage"],
        "stack":      {"language": "Python", "storage": "JSON/SQLite", "deps": []},
        "complexity": "LOW",
        "hours":      3,
        "risks":      ["Data loss on crash", "Concurrent writes"],
        "best_practices": [
            "Use atomic writes to prevent data corruption.",
            "Assign unique IDs to all tasks.",
            "Support filtering and searching.",
        ],
    },
    "web_app": {
        "paradigm":   "MVC",
        "patterns":   ["Route Handler", "Template Engine", "Middleware Chain"],
        "stack":      {"framework": "Flask", "db": "SQLite", "deps": ["flask"]},
        "complexity": "MEDIUM",
        "hours":      8,
        "risks":      ["XSS", "CSRF", "SQL injection", "Session hijacking"],
        "best_practices": [
            "Sanitise all user inputs.",
            "Use HTTPS in production.",
            "Implement CSRF protection.",
            "Follow the principle of least privilege.",
        ],
    },
    "rest_api": {
        "paradigm":   "REST",
        "patterns":   ["Repository Pattern", "Service Layer", "DTO", "Pagination"],
        "stack":      {"framework": "FastAPI", "db": "PostgreSQL", "deps": ["fastapi", "uvicorn"]},
        "complexity": "MEDIUM",
        "hours":      6,
        "risks":      ["Authentication bypass", "Rate limiting", "Data validation"],
        "best_practices": [
            "Version your API from day one.",
            "Always return consistent error envelopes.",
            "Document every endpoint with OpenAPI.",
            "Implement rate limiting.",
        ],
    },
    "desktop_gui": {
        "paradigm":   "Event-Driven",
        "patterns":   ["Observer", "MVC", "Command"],
        "stack":      {"framework": "tkinter", "deps": []},
        "complexity": "MEDIUM",
        "hours":      6,
        "risks":      ["Thread safety", "Memory leaks", "Platform differences"],
        "best_practices": [
            "Run I/O in background threads.",
            "Keep GUI and business logic separate.",
            "Test on all target platforms.",
        ],
    },
    "data_analyzer": {
        "paradigm":   "Pipeline",
        "patterns":   ["ETL", "Strategy Pattern", "Builder"],
        "stack":      {"language": "Python", "deps": ["pandas", "matplotlib"]},
        "complexity": "MEDIUM",
        "hours":      5,
        "risks":      ["Memory overflow on large files", "Encoding issues"],
        "best_practices": [
            "Validate data types on load.",
            "Handle missing values explicitly.",
            "Log statistics before and after transformations.",
        ],
    },
    "game": {
        "paradigm":   "Game Loop",
        "patterns":   ["State Machine", "Observer", "Entity-Component"],
        "stack":      {"language": "Python", "deps": []},
        "complexity": "MEDIUM",
        "hours":      6,
        "risks":      ["Infinite loops", "Unbalanced difficulty"],
        "best_practices": [
            "Separate game logic from rendering.",
            "Define clear win/lose conditions.",
            "Use a fixed-step game loop.",
        ],
    },
    "chat_app": {
        "paradigm":   "Event-Driven / Actor",
        "patterns":   ["Pub-Sub", "Reactor", "Connection Pool"],
        "stack":      {"language": "Python", "deps": []},
        "complexity": "HIGH",
        "hours":      10,
        "risks":      ["Race conditions", "Message ordering", "DoS"],
        "best_practices": [
            "Validate and sanitise all messages.",
            "Implement rate limiting per connection.",
            "Use non-blocking sockets or asyncio.",
        ],
    },
    "inventory": {
        "paradigm":   "Domain-Driven",
        "patterns":   ["Repository", "Unit of Work", "CQRS"],
        "stack":      {"language": "Python", "db": "SQLite", "deps": []},
        "complexity": "MEDIUM",
        "hours":      8,
        "risks":      ["Concurrent stock updates", "Audit trail gaps"],
        "best_practices": [
            "Never hard-delete records — use soft deletes.",
            "Maintain full audit logs.",
            "Validate stock levels before commits.",
        ],
    },
    "ai_system": {
        "paradigm":   "Pipeline / Agent",
        "patterns":   ["Strategy", "Chain of Responsibility", "Observer"],
        "stack":      {"language": "Python", "deps": ["numpy", "scikit-learn"]},
        "complexity": "HIGH",
        "hours":      12,
        "risks":      ["Data leakage", "Model bias", "Overfitting"],
        "best_practices": [
            "Separate training from inference.",
            "Version datasets and models together.",
            "Always evaluate on a held-out test set.",
        ],
    },
    "scheduler": {
        "paradigm":   "Queue / Worker",
        "patterns":   ["Producer-Consumer", "Cron", "Retry with Backoff"],
        "stack":      {"language": "Python", "deps": []},
        "complexity": "MEDIUM",
        "hours":      5,
        "risks":      ["Job duplication", "Missed schedules", "Resource starvation"],
        "best_practices": [
            "Make jobs idempotent.",
            "Log every job execution.",
            "Implement dead-letter queues for failed jobs.",
        ],
    },
    "file_manager": {
        "paradigm":   "Command",
        "patterns":   ["Command", "Iterator", "Composite"],
        "stack":      {"language": "Python", "deps": []},
        "complexity": "LOW",
        "hours":      3,
        "risks":      ["Accidental overwrites", "Permission errors"],
        "best_practices": [
            "Always confirm before destructive operations.",
            "Show previews before bulk operations.",
            "Maintain an operation log.",
        ],
    },
    "generic": {
        "paradigm":   "Modular",
        "patterns":   ["Facade", "Strategy", "Builder"],
        "stack":      {"language": "Python", "deps": []},
        "complexity": "MEDIUM",
        "hours":      4,
        "risks":      ["Scope creep", "Poor modularity"],
        "best_practices": [
            "Define clear module boundaries.",
            "Write tests before code.",
            "Document public interfaces.",
        ],
    },
}

# Keyword → project type mapping
_TYPE_KEYWORDS: dict = {
    "calculator":   ["calculator", "calc", "arithmetic", "math", "compute"],
    "todo_app":     ["todo", "task", "checklist", "reminder", "planner", "to-do"],
    "web_app":      ["web app", "website", "web application", "portal", "dashboard", "blog", "cms"],
    "rest_api":     ["api", "rest", "endpoint", "microservice", "backend", "service", "server"],
    "desktop_gui":  ["desktop", "gui", "window", "tkinter", "application", "app", "form"],
    "data_analyzer":["data", "analysis", "analytics", "csv", "report", "chart", "statistics", "pipeline"],
    "game":         ["game", "puzzle", "adventure", "quiz", "rpg", "arcade", "play"],
    "chat_app":     ["chat", "messenger", "messaging", "communication", "socket"],
    "inventory":    ["inventory", "stock", "warehouse", "product", "item", "catalogue", "supply"],
    "ai_system":    ["ai", "machine learning", "ml", "neural", "model", "prediction", "classifier"],
    "scheduler":    ["scheduler", "cron", "job", "queue", "worker", "task runner"],
    "file_manager": ["file", "directory", "folder", "storage", "organizer", "backup"],
}


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _topic_hash(goal: str) -> str:
    return hashlib.sha256(goal.strip().lower().encode()).hexdigest()[:16]


def _detect_project_type(goal: str) -> str:
    goal_l = goal.lower()
    scores: dict = {pt: 0 for pt in _TYPE_KEYWORDS}
    for ptype, keywords in _TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in goal_l:
                scores[ptype] += 1
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "generic"


def _extract_concepts(goal: str) -> list:
    stop = {"a", "an", "the", "build", "create", "make", "simple",
            "basic", "complete", "full", "new", "and", "or", "for",
            "with", "that", "can", "will", "my", "our", "your"}
    words = re.findall(r"[a-zA-Z]+", goal.lower())
    return list(dict.fromkeys(w for w in words if w not in stop and len(w) > 2))


def _consult_memory_db() -> dict:
    """Read Memory AI database for historical lessons."""
    if not MEMORY_DB.exists():
        return {}
    try:
        with open(MEMORY_DB) as f:
            data = json.load(f)
        return data.get("graph", {})
    except Exception:
        return {}


# ------------------------------------------------------------------ #
# Research AI                                                          #
# ------------------------------------------------------------------ #

class ResearchAI:
    """
    NEXUS Permanent Intelligence System.

    Consults three internal sources on every topic:
      1. Internal engineering pattern library
      2. Memory AI historical database
      3. Goal semantic analysis

    Verified knowledge is stored permanently and reused on
    subsequent runs — the same topic is never researched
    twice unless the goal changes significantly.
    """

    def __init__(self, shared_memory):
        self.memory     = shared_memory
        self.kb_path    = KB_FILE
        self.backup_dir = KB_BACKUP
        self._kb: dict  = {}
        self._bootstrap()
        print("[Research AI] Connected to Shared Memory.")

    def start(self):
        print("[Research AI] Permanent Intelligence System Ready.")

    # ---------------------------------------------------------------- #
    # Bootstrap                                                          #
    # ---------------------------------------------------------------- #

    def _bootstrap(self):
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        if self.kb_path.exists():
            try:
                with open(self.kb_path) as f:
                    self._kb = json.load(f)
            except Exception:
                self._kb = self._fresh_kb()
        else:
            self._kb = self._fresh_kb()
            self._save()

    @staticmethod
    def _fresh_kb() -> dict:
        return {
            "manifest": {
                "engine":       ENGINE_NAME,
                "version":      ENGINE_VER,
                "created":      datetime.now(timezone.utc).isoformat(),
                "last_updated": None,
            },
            "topics": {},
        }

    def _save(self):
        """Atomic save of the knowledge base."""
        tmp = self.kb_path.with_suffix(".tmp")
        self._kb["manifest"]["last_updated"] = (
            datetime.now(timezone.utc).isoformat()
        )
        with open(tmp, "w") as f:
            json.dump(self._kb, f, indent=4)
        # Backup existing
        if self.kb_path.exists():
            ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
            bak = self.backup_dir / f"kb_{ts}.bak"
            import shutil
            shutil.copy2(self.kb_path, bak)
        os.replace(tmp, self.kb_path)

    # ---------------------------------------------------------------- #
    # Research Engine                                                    #
    # ---------------------------------------------------------------- #

    def _research(self, goal: str) -> dict:
        """
        Conduct full research on *goal* using all three sources.
        Returns a verified research record.
        """
        project_type = _detect_project_type(goal)
        concepts     = _extract_concepts(goal)
        patterns     = _PATTERNS.get(project_type, _PATTERNS["generic"])

        # Source 1: Internal pattern library
        source1 = {
            "source":       "Internal Engineering Pattern Library",
            "project_type": project_type,
            "paradigm":     patterns["paradigm"],
            "patterns":     patterns["patterns"],
            "stack":        patterns["stack"],
            "complexity":   patterns["complexity"],
            "estimated_hours": patterns["hours"],
            "risks":        patterns["risks"],
            "best_practices": patterns["best_practices"],
        }

        # Source 2: Memory AI historical database
        memory_graph = _consult_memory_db()
        past_successes = list(memory_graph.get("successes", {}).values())
        past_failures  = list(memory_graph.get("failures",  {}).values())

        source2 = {
            "source":          "Memory AI Historical Database",
            "past_successes":  len(past_successes),
            "past_failures":   len(past_failures),
            "success_lessons": [
                s.get("goal") for s in past_successes[:3]
            ],
            "failure_lessons": [
                f.get("goal") for f in past_failures[:3]
            ],
            "historical_frameworks": list({
                s.get("framework") for s in past_successes
                if s.get("framework")
            }),
        }

        # Source 3: Semantic concept analysis
        source3 = {
            "source":   "Goal Semantic Analysis",
            "concepts": concepts,
            "goal_length_words": len(goal.split()),
            "domain_keywords":  [
                c for c in concepts
                if c in project_type.replace("_", " ")
                or any(c in kws for kws in _TYPE_KEYWORDS.values())
            ],
        }

        # Verification: cross-reference sources 1 & 3
        verified = bool(
            source3["domain_keywords"]
            or project_type != "generic"
        )

        return {
            "researched_at":  datetime.now(timezone.utc).isoformat(),
            "goal":           goal,
            "project_type":   project_type,
            "verified":       verified,
            "concepts":       concepts,
            "sources":        [source1, source2, source3],
            "recommended_stack":     patterns["stack"],
            "recommended_patterns":  patterns["patterns"],
            "complexity":            patterns["complexity"],
            "estimated_hours":       patterns["hours"],
            "risks":                 patterns["risks"],
            "best_practices":        patterns["best_practices"],
        }

    # ---------------------------------------------------------------- #
    # Pipeline Entry Point                                               #
    # ---------------------------------------------------------------- #

    def process_project_task(self, task_id: str):

        key     = f"active_project_{task_id}"
        project = self.memory.read(key)

        if project is None:
            print("[Research AI] Project not found.")
            return

        goal      = project.get("goal", "")
        topic_key = _topic_hash(goal)

        print(f"[Research AI] Researching: {task_id}")
        print(f"[Research AI] Goal       : {goal}")

        # Check knowledge base — never research the same topic twice
        if topic_key in self._kb["topics"]:
            existing = self._kb["topics"][topic_key]
            print(f"[Research AI] Topic already researched — reusing verified knowledge.")
            print(f"[Research AI] Original research: {existing['researched_at']}")
            research = existing
        else:
            print(f"[Research AI] New topic — consulting all sources...")
            research = self._research(goal)
            self._kb["topics"][topic_key] = research
            self._save()
            print(f"[Research AI] Knowledge permanently stored.")

        # Publish to Shared Memory for all other workers
        self.memory.write(f"research_context_{task_id}", research)

        # Update project
        project["research"]     = research
        project["project_type"] = research["project_type"]
        project["status"]       = "RESEARCH_COMPLETE"
        self.memory.write(key, project)

        print(f"[Research AI] Project Type  : {research['project_type']}")
        print(f"[Research AI] Verified      : {research['verified']}")
        print(f"[Research AI] Complexity    : {research['complexity']}")
        print(f"[Research AI] Est. Hours    : {research['estimated_hours']}")
        print(f"[Research AI] Sources Used  : {len(research['sources'])}")
        print(f"[Research AI] KB Topics     : {len(self._kb['topics'])}")
