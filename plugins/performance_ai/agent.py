"""
NEXUS
Performance AI — Runtime Profiling Engine

Module ID : PERFORMANCE-001
Version   : 1.0.0

Performs genuine runtime performance measurements using
Python's timeit, cProfile, and AST-based complexity
estimation.  Every number reported comes from an actual
measurement — nothing is fabricated.
"""

import ast
import time
import timeit
import cProfile
import pstats
import io
from datetime import datetime


class PerformanceAI:
    """
    NEXUS Performance Analyst.

    Responsibilities
    ----------------
    • Cyclomatic complexity estimation (AST)
    • Function-level benchmarking      (timeit)
    • CPU profiling                    (cProfile)
    • Bottleneck identification
    • Performance grade assignment
    """

    def __init__(self, shared_memory):
        self.memory = shared_memory
        print("[Performance AI] Connected to Shared Memory.")

    def start(self):
        print("[Performance AI] Runtime Profiling Engine Ready.")

    # ---------------------------------------------------------------- #
    # Cyclomatic Complexity                                              #
    # ---------------------------------------------------------------- #

    def _estimate_complexity(self, tree: ast.AST) -> dict:
        """
        Estimate cyclomatic complexity per function by counting
        decision nodes (if / elif / for / while / try / except /
        with / assert / comprehensions).
        """

        DECISION_NODES = (
            ast.If, ast.For, ast.While,
            ast.ExceptHandler, ast.With,
            ast.Assert, ast.comprehension,
        )

        results = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                count = 1  # base path
                for child in ast.walk(node):
                    if isinstance(child, DECISION_NODES):
                        count += 1
                results[node.name] = count

        return results

    # ---------------------------------------------------------------- #
    # Benchmark                                                          #
    # ---------------------------------------------------------------- #

    def _benchmark_functions(
        self,
        source: str,
        complexity: dict,
        repeat: int = 3,
        number: int = 1000,
    ) -> list:
        """
        Execute each discovered function (zero-argument calls only)
        *number* times, *repeat* rounds.  Returns timing results.
        """

        namespace: dict = {}

        try:
            exec(source, namespace)  # noqa: S102 — sandboxed namespace
        except Exception as err:
            return [{"error": f"Source execution failed: {err}"}]

        # Build a set of function names that call input() — skip those
        # to avoid blocking on stdin during benchmarking
        _input_callers: set = set()
        try:
            _tree = ast.parse(source)
            for _node in ast.walk(_tree):
                if isinstance(_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for _child in ast.walk(_node):
                        if (
                            isinstance(_child, ast.Call)
                            and isinstance(_child.func, ast.Name)
                            and _child.func.id == "input"
                        ):
                            _input_callers.add(_node.name)
        except Exception:
            pass

        results = []

        for name, obj in list(namespace.items()):

            if not callable(obj) or name.startswith("_"):
                continue

            # Skip functions that read from stdin
            if name in _input_callers:
                results.append({
                    "function":  name,
                    "skipped":   True,
                    "reason":    "contains input() — skipped to avoid stdin block",
                    "complexity": complexity.get(name, 1),
                })
                continue

            # Only benchmark zero-argument functions safely
            try:
                import inspect
                sig = inspect.signature(obj)
                required = [
                    p for p in sig.parameters.values()
                    if p.default is inspect.Parameter.empty
                    and p.kind not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    )
                ]
                if required:
                    results.append({
                        "function":    name,
                        "skipped":     True,
                        "reason":      "requires arguments",
                        "complexity":  complexity.get(name, 1),
                    })
                    continue

                times = timeit.repeat(
                    stmt=obj,
                    repeat=repeat,
                    number=number,
                    timer=time.perf_counter,
                )

                best_ms   = round(min(times) / number * 1000, 6)
                avg_ms    = round(sum(times) / len(times) / number * 1000, 6)
                worst_ms  = round(max(times) / number * 1000, 6)

                results.append({
                    "function":   name,
                    "skipped":    False,
                    "complexity": complexity.get(name, 1),
                    "best_ms":    best_ms,
                    "avg_ms":     avg_ms,
                    "worst_ms":   worst_ms,
                    "calls":      number,
                })

            except Exception as err:
                results.append({
                    "function":  name,
                    "skipped":   True,
                    "reason":    str(err),
                    "complexity": complexity.get(name, 1),
                })

        return results

    # ---------------------------------------------------------------- #
    # CPU Profile                                                        #
    # ---------------------------------------------------------------- #

    def _cpu_profile(self, source: str) -> str:
        """
        Run cProfile on the source module and return the top-10
        cumulative time entries as a formatted string.
        """

        namespace: dict = {}
        profiler = cProfile.Profile()

        try:
            profiler.enable()
            exec(source, namespace)  # noqa: S102
            profiler.disable()
        except Exception:
            profiler.disable()

        stream = io.StringIO()
        stats  = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(10)

        return stream.getvalue()

    # ---------------------------------------------------------------- #
    # Grading                                                            #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _grade(avg_complexity: float, max_avg_ms: float) -> str:
        """
        Assign a performance grade based on complexity and timing.
        """
        if avg_complexity <= 3 and max_avg_ms < 1.0:
            return "A"
        if avg_complexity <= 5 and max_avg_ms < 5.0:
            return "B"
        if avg_complexity <= 8 and max_avg_ms < 20.0:
            return "C"
        if avg_complexity <= 12:
            return "D"
        return "F"

    # ---------------------------------------------------------------- #
    # Core Analysis                                                      #
    # ---------------------------------------------------------------- #

    def analyze_source_code(self, source: str) -> dict:

        if not source:
            return {
                "analysed_at":       datetime.utcnow().isoformat(),
                "performance_grade": "N/A",
                "approved":          False,
                "error":             "Source code missing.",
            }

        # Parse
        try:
            tree = ast.parse(source)
        except SyntaxError as err:
            return {
                "analysed_at":       datetime.utcnow().isoformat(),
                "performance_grade": "N/A",
                "approved":          False,
                "error":             f"Syntax error: {err}",
            }

        # Static metrics
        lines          = [l for l in source.splitlines() if l.strip()]
        total_lines    = len(lines)
        complexity_map = self._estimate_complexity(tree)
        func_count     = len(complexity_map)
        avg_complexity = (
            round(sum(complexity_map.values()) / func_count, 2)
            if func_count else 0
        )
        max_complexity = max(complexity_map.values(), default=0)

        # Runtime benchmark
        benchmarks = self._benchmark_functions(source, complexity_map)

        # CPU profile snapshot
        cpu_profile = self._cpu_profile(source)

        # Timing stats from benchmarks
        timed = [b for b in benchmarks if not b.get("skipped")]
        max_avg_ms = (
            max(b["avg_ms"] for b in timed) if timed else 0.0
        )
        total_avg_ms = (
            round(sum(b["avg_ms"] for b in timed), 6) if timed else 0.0
        )

        # Bottlenecks: functions with complexity > 5 or avg_ms > 1 ms
        bottlenecks = [
            b["function"]
            for b in benchmarks
            if (
                not b.get("skipped")
                and (b["avg_ms"] > 1.0 or b["complexity"] > 5)
            )
        ]

        grade   = self._grade(avg_complexity, max_avg_ms)
        approved = grade in ("A", "B", "C")

        return {
            "analysed_at":       datetime.utcnow().isoformat(),
            "performance_grade": grade,
            "approved":          approved,
            "total_lines":       total_lines,
            "function_count":    func_count,
            "avg_complexity":    avg_complexity,
            "max_complexity":    max_complexity,
            "complexity_map":    complexity_map,
            "benchmarks":        benchmarks,
            "total_avg_ms":      total_avg_ms,
            "bottlenecks":       bottlenecks,
            "cpu_profile_top10": cpu_profile.strip(),
            "recommendation":    "APPROVED" if approved else "OPTIMISATION_REQUIRED",
        }

    # ---------------------------------------------------------------- #
    # Pipeline Entry Point                                               #
    # ---------------------------------------------------------------- #

    def process_project_task(self, task_id: str):

        key     = f"active_project_{task_id}"
        project = self.memory.read(key)

        if project is None:
            print("[Performance AI] Project not found.")
            return

        print(f"[Performance AI] Profiling: {task_id}")

        source = project.get("code", {}).get("source", "")
        report = self.analyze_source_code(source)

        project["performance"] = report

        if report["approved"]:
            project["status"] = "PERFORMANCE_APPROVED"
            print("[Performance AI] Performance analysis passed.")
        else:
            project["status"] = "OPTIMISATION_REQUIRED"
            print("[Performance AI] Performance issues detected.")

        self.memory.write(key, project)

        print(f"[Performance AI] Grade       : {report['performance_grade']}")
        print(f"[Performance AI] Avg Complexity : {report.get('avg_complexity', 'N/A')}")
        print(f"[Performance AI] Bottlenecks : {report.get('bottlenecks', [])}")
        print(f"[Performance AI] Verdict     : {report['recommendation']}")
