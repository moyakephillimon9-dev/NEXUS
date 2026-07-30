"""
NEXUS
=============
Private AI Software Engineering Company

Entry point for the NEXUS CLI.

Usage
-----
Interactive mode (default):
    python nexus.py

One-shot scripting:
    python nexus.py --goal "Build a REST API"

Vision document mode:
    python nexus.py --vision path/to/vision.txt
    python nexus.py --vision -   (read from stdin)

After pip install -e .:
    nexus
    nexus --goal "Build a REST API"
    nexus --vision vision.txt
    nexus --version
    nexus --workers
    nexus --history
"""

import argparse
import json
import os
import sys

from core.kernel import Kernel
from core.config import Config


# ------------------------------------------------------------------ #
# Version                                                              #
# ------------------------------------------------------------------ #

__version__ = Config.VERSION


# ------------------------------------------------------------------ #
# Banner                                                               #
# ------------------------------------------------------------------ #

BANNER = r"""
 _   _  _______  _____  _    _  _____
| \ | ||  _____||  __ \| |  | |/ ____|
|  \| || |___   | |  | | |  | | (___
| . ` ||  ___|  | |  | | |  | |\___ \
| |\  || |_____ | |__| | |__| |____) |
|_| \_||_______||_____/ \____/|_____/

NEXUS  v{version}
Private AI Software Engineering Company
Owner : {owner}
{line}
"""


def print_banner():
    print(BANNER.format(
        version=Config.VERSION,
        owner=Config.OWNER,
        line="=" * 50,
    ))


# ------------------------------------------------------------------ #
# Actions                                                              #
# ------------------------------------------------------------------ #

def action_workers():
    """Show all registered AI workers."""
    workers = [
        # Stage  ID               Name                  Responsibility
        (  0, "VISION-001",    "Vision Parser AI",    "Parses vision docs; extracts requirements, modules, technologies"),
        (  1, "ASSESS-001",    "Capability Assessor", "Classifies features: Fully/Partially/Unsupported — never fakes"),
        (  2, "RESEARCH-001",  "Research AI",         "Permanent knowledge base; pattern library; topic dedup"),
        (  3, "MODULE-001",    "Module Detector AI",  "Detects modules, builds dependency graph, exec order"),
        (  4, "PLANNER-001",   "Planner AI",          "19-phase plan with tasks, subtasks, effort, risk, calendar"),
        (  5, "ARCHITECT-001", "Architect AI",        "9-layer architecture: module, API, DB, security, deploy..."),
        (  6, "DATABASE-001",  "Database AI",         "SQL DDL schema + Python sqlite3 helper per project type"),
        (  7, "CODER-001",     "Coder AI",            "13-template type-aware source code generation"),
        (  8, "DESIGN-001",    "Design AI",           "Colour palette, production CSS, layout specification"),
        (  9, "REVIEWER-001",  "Reviewer AI",         "AST static analysis + quality gate (score ≥ 70)"),
        ( 10, "TESTER-001",    "Tester AI",           "Sandboxed runtime validation + coverage estimation"),
        ( 11, "SECURITY-001",  "Security AI",         "Vulnerability & secret scanning; risk classification"),
        ( 12, "PERFORMANCE-001","Performance AI",     "Benchmarks + cyclomatic complexity; grade A–F"),
        ( 13, "DOCS-001",      "Documentation AI",    "README, API.md, ARCHITECTURE.md, CHANGELOG, CONTRIBUTING"),
        ( 14, "MONITOR-001",   "Monitoring AI",       "Health checks, metrics, logger config, alerts.json"),
        ( 15, "INTEGRATION-001","Integration AI",     "API client with retries, HMAC webhook handler, config"),
        ( 16, "DEVOPS-001",    "DevOps AI",           "Dockerfile, GitHub Actions CI/CD, Makefile"),
        ( 17, "DEPLOY-001",    "Deployment AI",       "Release archive, requirements.txt, deployment.json"),
        ( 18, "VERIFY-001",    "Verification AI",     "Pre-release honesty check — blocks false success claims"),
        ( 19, "PROGRESS-001",  "Progress Tracker AI", "Completion %, feature classification, limitations, recs"),
        ( 20, "MEMORY-001",    "Memory AI",           "Persistent semantic knowledge graph + learning engine"),
    ]

    print(f"\n  {'St':>3}  {'ID':<20} {'Worker':<22} {'Responsibility'}")
    print("  " + "-" * 90)
    for stage, wid, name, desc in workers:
        print(f"  {stage:>3}  {wid:<20} {name:<22} {desc}")
    print(f"\n  Total: {len(workers)} AI workers  |  Pipeline: 21 stages\n")


def action_about():
    """Print the NEXUS constitution summary."""
    about = """
  NEXUS BUILDER — ABOUT
  =====================================================================

  NEXUS is a private AI software engineering company.

  It operates a team of 21 specialised AI workers that:

    ① Parse any vision document or goal into structured specifications
    ② Honestly assess which features are buildable vs unsupported
    ③ Detect required modules and build a dependency graph
    ④ Plan phases, milestones, tasks, subtasks with effort estimates
    ⑤ Design 9-layer system architecture with full reasoning
    ⑥ Generate SQL schemas and Python database layers
    ⑦ Generate type-aware source code (13 project templates)
    ⑧ Design colour palettes and production CSS
    ⑨ Review code quality with AST analysis
    ⑩ Validate code in a sandboxed runtime
    ⑪ Scan for security vulnerabilities
    ⑫ Benchmark performance and complexity
    ⑬ Write comprehensive documentation (5 files)
    ⑭ Configure observability (health, metrics, alerts)
    ⑮ Generate integration layer (API client, webhooks)
    ⑯ Build DevOps pipeline (Docker, CI/CD, Makefile)
    ⑰ Package releases with correct dependencies
    ⑱ Verify honesty — never claims unsupported features are done
    ⑲ Report progress with completion percentages per stage
    ⑳ Preserve knowledge for continuous improvement

  CORE PRINCIPLE: Honesty, verification, and transparency
  take priority over claiming completion.

  Owner   : Moyake Phillimon
  Version : {version}
  =====================================================================
""".format(version=Config.VERSION)
    print(about)


def action_history():
    """Show completed projects from the projects directory."""
    projects_dir = str(getattr(Config, "PROJECTS_FOLDER", Config.ROOT / "projects"))
    if not os.path.isdir(projects_dir):
        print(f"\n  No project history found (folder '{projects_dir}' does not exist).\n")
        return

    files = sorted(
        f for f in os.listdir(projects_dir) if f.endswith(".json")
    )

    if not files:
        print(f"\n  No projects on record in '{projects_dir}'.\n")
        return

    print(f"\n  {'Task ID':<20} {'Goal':<45} {'Status':<25} {'Type'}")
    print("  " + "-" * 105)

    for filename in files[-20:]:          # show last 20
        filepath = os.path.join(projects_dir, filename)
        try:
            with open(filepath) as fh:
                data = json.load(fh)
            tid    = data.get("task_id", filename)[:20]
            goal   = data.get("goal", "N/A")[:44]
            status = data.get("status", "N/A")[:24]
            ptype  = data.get("research", {}).get("project_type", "N/A")
            print(f"  {tid:<20} {goal:<45} {status:<25} {ptype}")
        except Exception:
            print(f"  {filename:<20} (could not read)")

    print()


def action_run(goal: str):
    """Execute the full 21-stage pipeline for a goal."""
    from core.orchestrator import Orchestrator
    Orchestrator().run(goal=goal)


def action_vision(source: str):
    """
    Parse a vision document and run the full pipeline.

    Parameters
    ----------
    source : str
        File path, or '-' to read from stdin.
    """
    if source == "-":
        print("[NEXUS] Reading vision document from stdin...")
        text = sys.stdin.read()
    else:
        if not os.path.isfile(source):
            print(f"[NEXUS] Error: file not found — '{source}'")
            sys.exit(1)
        with open(source, encoding="utf-8") as fh:
            text = fh.read()

    if not text.strip():
        print("[NEXUS] Error: vision document is empty.")
        sys.exit(1)

    print(f"[NEXUS] Vision document loaded: {len(text)} chars, {text.count(chr(10))} lines")
    action_run(goal=text)


# ------------------------------------------------------------------ #
# Interactive menu                                                     #
# ------------------------------------------------------------------ #

def action_ai_settings():
    """Interactive AI provider settings panel."""
    from core.provider_manager import ProviderManager
    from core.settings import Settings

    while True:
        providers = ProviderManager.list_providers()

        print("\n  AI PROVIDER SETTINGS")
        print("  " + "=" * 60)
        print(f"  {'#':<4} {'Provider':<22} {'Status':<12} {'Active'}")
        print("  " + "-" * 60)

        pid_map = {}
        for i, p in enumerate(providers, 1):
            status  = "✓ Available" if p["available"] else "✗ Offline"
            active  = "◀ ACTIVE"   if p["active"]    else ""
            print(f"  [{i}]  {p['name']:<22} {status:<12} {active}")
            pid_map[str(i)] = p["id"]

        print("\n  Current model settings:")
        active_id = Settings.get("ai_provider", "builtin")
        if active_id == "openrouter":
            print(f"    OpenRouter model : {Settings.get('openrouter_model')}")
            print(f"    (Free models: meta-llama/llama-3.1-8b-instruct:free,")
            print(f"                  mistralai/mistral-7b-instruct:free,")
            print(f"                  google/gemma-2-9b-it:free)")
        elif active_id == "ollama":
            print(f"    Ollama host  : {Settings.get('ollama_host')}")
            print(f"    Ollama model : {Settings.get('ollama_model')}")
        elif active_id == "lmstudio":
            print(f"    LM Studio host  : {Settings.get('lmstudio_host')}")
            print(f"    LM Studio model : {Settings.get('lmstudio_model')}")

        print("\n  [1-4] Switch provider  [M] Change model/host  [B] Back")
        print()

        choice = input("  > ").strip().upper()

        if choice in pid_map:
            new_id   = pid_map[choice]
            new_prov = next(p for p in providers if p["id"] == new_id)
            if not new_prov["available"] and new_id != "builtin":
                print(f"\n  ⚠  {new_prov['name']} is not reachable.")
                print(f"     {new_prov['notes']}")
                confirm = input("  Switch anyway? (y/N) ").strip().lower()
                if confirm != "y":
                    continue
            ProviderManager.set_provider(new_id)
            print(f"\n  ✓  AI provider switched to: {new_prov['name']}")

        elif choice == "M":
            active_id = Settings.get("ai_provider", "builtin")
            if active_id == "openrouter":
                model = input(f"\n  OpenRouter model [{Settings.get('openrouter_model')}]: ").strip()
                if model:
                    Settings.set("openrouter_model", model)
                    print(f"  ✓  Model set to: {model}")
            elif active_id == "ollama":
                host  = input(f"\n  Ollama host [{Settings.get('ollama_host')}]: ").strip()
                model = input(f"  Ollama model [{Settings.get('ollama_model')}]: ").strip()
                if host:  Settings.set("ollama_host",  host)
                if model: Settings.set("ollama_model", model)
                print("  ✓  Ollama settings saved.")
            elif active_id == "lmstudio":
                host  = input(f"\n  LM Studio host [{Settings.get('lmstudio_host')}]: ").strip()
                model = input(f"  LM Studio model [{Settings.get('lmstudio_model')}]: ").strip()
                if host:  Settings.set("lmstudio_host",  host)
                if model: Settings.set("lmstudio_model", model)
                print("  ✓  LM Studio settings saved.")
            else:
                print("  Built-in engine has no configurable model.")

        elif choice in ("B", "BACK", ""):
            break

        else:
            print("  Unknown option.")


def interactive_menu():
    """Full interactive CLI menu."""
    print_banner()

    while True:
        print("\n  MAIN MENU")
        print("  " + "-" * 40)
        print("  [1]  Run pipeline with a goal")
        print("  [2]  Run pipeline from a vision document file")
        print("  [3]  List all AI workers")
        print("  [4]  View project history")
        print("  [5]  About NEXUS")
        print("  [6]  AI Provider Settings")
        print("  [Q]  Quit")
        print()

        choice = input("  > ").strip().upper()

        if choice == "1":
            goal = input("\n  Enter your goal: ").strip()
            if goal:
                action_run(goal)
            else:
                print("  No goal entered.")

        elif choice == "2":
            path = input("\n  Enter path to vision document (or - for stdin): ").strip()
            if path:
                action_vision(path)
            else:
                print("  No path entered.")

        elif choice == "3":
            action_workers()

        elif choice == "4":
            action_history()

        elif choice == "5":
            action_about()

        elif choice == "6":
            action_ai_settings()

        elif choice in ("Q", "QUIT", "EXIT"):
            print("\n  NEXUS shutting down. Goodbye.\n")
            break

        else:
            print("  Unknown option. Please choose 1–6 or Q.")


# ------------------------------------------------------------------ #
# CLI argument parser                                                  #
# ------------------------------------------------------------------ #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="NEXUS — Private AI Software Engineering Company",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nexus                                    # interactive menu
  nexus --goal "Build a REST API"          # one-shot goal
  nexus --vision master_vision.txt         # vision document file
  nexus --vision -                         # vision document from stdin
  nexus --workers                          # list all AI workers
  nexus --history                          # show project history
  nexus --version                          # show version
        """,
    )

    parser.add_argument(
        "--goal", "-g",
        metavar="GOAL",
        help="Project goal (runs the full 21-stage pipeline).",
    )

    parser.add_argument(
        "--vision", "-V",
        metavar="FILE",
        help="Path to a vision document file (or '-' for stdin).",
    )

    parser.add_argument(
        "--workers", "-w",
        action="store_true",
        help="List all registered AI workers and exit.",
    )

    parser.add_argument(
        "--history",
        action="store_true",
        help="Show completed project history and exit.",
    )

    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Print version and exit.",
    )

    return parser


# ------------------------------------------------------------------ #
# Entry point                                                          #
# ------------------------------------------------------------------ #

def main():
    parser = build_parser()
    args   = parser.parse_args()

    if args.version:
        print(f"NEXUS v{Config.VERSION}")
        sys.exit(0)

    if args.workers:
        action_workers()
        sys.exit(0)

    if args.history:
        action_history()
        sys.exit(0)

    if args.vision:
        print_banner()
        action_vision(args.vision)
        sys.exit(0)

    if args.goal:
        print_banner()
        action_run(args.goal)
        sys.exit(0)

    # Default: interactive menu
    interactive_menu()


if __name__ == "__main__":
    main()
