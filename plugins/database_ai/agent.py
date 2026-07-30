"""
NEXUS
Database AI — Schema Design Engine

Module ID : DATABASE-001
Version   : 1.0.0

Generates real, executable database schemas from the project
goal and architecture blueprint.  Produces SQL DDL and a
Python sqlite3 helper module for immediate use.
"""

import os
from datetime import datetime


# ------------------------------------------------------------------ #
# Schema Templates                                                     #
# ------------------------------------------------------------------ #

_SCHEMAS: dict = {

    "calculator": {
        "description": "Calculation history log",
        "tables": [
            """CREATE TABLE IF NOT EXISTS calculation_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expression  TEXT    NOT NULL,
    result      REAL    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
        ],
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_calc_history_created ON calculation_history(created_at DESC);",
        ],
    },

    "todo_app": {
        "description": "Task management schema",
        "tables": [
            """CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT,
    status      TEXT    NOT NULL DEFAULT 'PENDING'
                        CHECK(status IN ('PENDING','IN_PROGRESS','DONE','CANCELLED')),
    priority    TEXT    NOT NULL DEFAULT 'MEDIUM'
                        CHECK(priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    due_date    TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
            """CREATE TABLE IF NOT EXISTS task_tags (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag     TEXT    NOT NULL
);""",
        ],
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);",
            "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);",
            "CREATE INDEX IF NOT EXISTS idx_task_tags_task ON task_tags(task_id);",
        ],
    },

    "web_app": {
        "description": "Web application schema",
        "tables": [
            """CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT    NOT NULL UNIQUE,
    email        TEXT    NOT NULL UNIQUE,
    password_hash TEXT   NOT NULL,
    role         TEXT    NOT NULL DEFAULT 'user',
    is_active    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
            """CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token      TEXT    NOT NULL UNIQUE,
    expires_at TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
            """CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER REFERENCES users(id),
    action     TEXT    NOT NULL,
    details    TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
        ],
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_users_email     ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_token  ON sessions(token);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user   ON sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_audit_user      ON audit_log(user_id);",
        ],
    },

    "rest_api": {
        "description": "REST API resource schema",
        "tables": [
            """CREATE TABLE IF NOT EXISTS api_keys (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    key_hash   TEXT    NOT NULL UNIQUE,
    is_active  INTEGER NOT NULL DEFAULT 1,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
            """CREATE TABLE IF NOT EXISTS resources (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    type       TEXT    NOT NULL,
    payload    TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
            """CREATE TABLE IF NOT EXISTS request_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    method      TEXT NOT NULL,
    path        TEXT NOT NULL,
    status_code INTEGER,
    duration_ms REAL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);""",
        ],
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_apikeys_hash      ON api_keys(key_hash);",
            "CREATE INDEX IF NOT EXISTS idx_resources_type    ON resources(type);",
            "CREATE INDEX IF NOT EXISTS idx_reqlog_created    ON request_log(created_at DESC);",
        ],
    },

    "inventory": {
        "description": "Inventory management schema",
        "tables": [
            """CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);""",
            """CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sku         TEXT    NOT NULL UNIQUE,
    name        TEXT    NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    unit_price  REAL    NOT NULL DEFAULT 0.0,
    stock_qty   INTEGER NOT NULL DEFAULT 0,
    min_stock   INTEGER NOT NULL DEFAULT 0,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
            """CREATE TABLE IF NOT EXISTS stock_movements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    type        TEXT    NOT NULL CHECK(type IN ('IN','OUT','ADJUST')),
    quantity    INTEGER NOT NULL,
    reference   TEXT,
    notes       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);""",
        ],
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_products_sku      ON products(sku);",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);",
            "CREATE INDEX IF NOT EXISTS idx_stock_product     ON stock_movements(product_id);",
        ],
    },

    "generic": {
        "description": "General purpose application schema",
        "tables": [
            """CREATE TABLE IF NOT EXISTS records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    type       TEXT NOT NULL DEFAULT 'general',
    name       TEXT NOT NULL,
    data       TEXT,
    status     TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);""",
            """CREATE TABLE IF NOT EXISTS event_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event      TEXT NOT NULL,
    details    TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);""",
        ],
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_records_type   ON records(type);",
            "CREATE INDEX IF NOT EXISTS idx_records_status ON records(status);",
        ],
    },
}


def _db_helper(schema_desc: str, tables: list) -> str:
    table_names = []
    for t in tables:
        match = __import__("re").search(r"CREATE TABLE IF NOT EXISTS (\w+)", t)
        if match:
            table_names.append(match.group(1))

    return f'''\'\'\' 
Database Helper — Auto-generated by NEXUS Database AI
Schema: {schema_desc}
Tables: {", ".join(table_names)}
\'\'\'
import sqlite3
from pathlib import Path

DB_PATH = Path("data/database.sqlite")


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def initialize_database():
    """Create all tables if they don\'t exist."""
    with get_connection() as conn:
        conn.executescript(open("schema.sql").read())
    print("Database initialized.")


def fetch_all(query: str, params: tuple = ()) -> list:
    """Execute a SELECT query and return all rows as dicts."""
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def fetch_one(query: str, params: tuple = ()) -> dict | None:
    """Execute a SELECT query and return one row as a dict."""
    with get_connection() as conn:
        row = conn.execute(query, params).fetchone()
    return dict(row) if row else None


def execute(query: str, params: tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE and return lastrowid."""
    with get_connection() as conn:
        cursor = conn.execute(query, params)
        conn.commit()
    return cursor.lastrowid


if __name__ == "__main__":
    initialize_database()
    print("Database ready at:", DB_PATH)
'''


class DatabaseAI:
    """
    NEXUS Database Designer.

    Reads the project goal and architecture blueprint, selects
    the most appropriate schema, generates real SQL DDL and a
    Python database helper, and writes both to the deployment
    folder.

    Responsibilities
    ----------------
    • Project type detection
    • SQL DDL schema generation
    • Index strategy
    • Python sqlite3 helper generation
    • Deployment artifact writing
    """

    def __init__(self, shared_memory, deployment_root: str = "deployments"):
        self.memory          = shared_memory
        self.deployment_root = deployment_root
        print("[Database AI] Connected to Shared Memory.")

    def start(self):
        print("[Database AI] Schema Design Engine Ready.")

    # ---------------------------------------------------------------- #
    # Schema Selection                                                   #
    # ---------------------------------------------------------------- #

    def _select_schema(self, project_type: str) -> dict:
        return _SCHEMAS.get(project_type, _SCHEMAS["generic"])

    # ---------------------------------------------------------------- #
    # Pipeline Entry Point                                               #
    # ---------------------------------------------------------------- #

    def process_project_task(self, task_id: str):

        key     = f"active_project_{task_id}"
        project = self.memory.read(key)

        if project is None:
            print("[Database AI] Project not found.")
            return

        print(f"[Database AI] Designing schema: {task_id}")

        project_type = project.get("project_type", "generic")
        schema       = self._select_schema(project_type)
        all_ddl      = "\n\n".join(schema["tables"] + schema["indexes"])
        helper_code  = _db_helper(schema["description"], schema["tables"])

        # Write to deployment folder
        goal_slug = (
            project.get("goal", "project")
            .lower().replace(" ", "_")[:40]
        )
        folder = os.path.join(
            self.deployment_root,
            f"{task_id}_{goal_slug}"
        )
        os.makedirs(folder, exist_ok=True)

        schema_path = os.path.join(folder, "schema.sql")
        helper_path = os.path.join(folder, "database.py")

        with open(schema_path, "w") as f:
            f.write(f"-- NEXUS Database AI — Auto-generated Schema\n")
            f.write(f"-- Project  : {project.get('goal')}\n")
            f.write(f"-- Type     : {project_type}\n")
            f.write(f"-- Generated: {datetime.utcnow().isoformat()}\n\n")
            f.write(all_ddl)

        with open(helper_path, "w") as f:
            f.write(helper_code)

        db_report = {
            "generated_at":  datetime.utcnow().isoformat(),
            "project_type":  project_type,
            "schema_file":   schema_path,
            "helper_file":   helper_path,
            "tables":        len(schema["tables"]),
            "indexes":       len(schema["indexes"]),
            "description":   schema["description"],
        }

        project["database"] = db_report
        project["status"]   = "DATABASE_SCHEMA_COMPLETE"
        self.memory.write(key, project)

        print(f"[Database AI] Schema Type : {project_type}")
        print(f"[Database AI] Tables      : {db_report['tables']}")
        print(f"[Database AI] Indexes     : {db_report['indexes']}")
        print(f"[Database AI] schema.sql  : {schema_path}")
        print(f"[Database AI] database.py : {helper_path}")
