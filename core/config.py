"""
NEXUS — AI Operating System
Configuration Manager

Module ID : CONFIG-001
Version   : 0.1.0
"""

from pathlib import Path


class Config:

    VERSION = "0.1.0"

    PROJECT_NAME = "NEXUS"

    OWNER = "Moyake Phillimon"

    DEBUG = True

    ROOT = Path(__file__).resolve().parent.parent

    PLUGIN_FOLDER = ROOT / "plugins"

    LOG_FOLDER = ROOT / "logs"

    MEMORY_FOLDER = ROOT / "memory"

    PROJECTS_FOLDER = ROOT / "projects"

    KNOWLEDGE_FOLDER = ROOT / "knowledge"

    RESEARCH_FOLDER = ROOT / "research"

    SECURITY_FOLDER = ROOT / "security"

    TEST_FOLDER = ROOT / "tests"
