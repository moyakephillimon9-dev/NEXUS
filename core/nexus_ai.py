"""
NEXUS
NEXUS AI Engine — Central Intelligence Layer

Module ID : NEXUS-AI-001
Version   : 1.0.0

Architecture
------------
  NexusAI
    ├── ProviderManager  ─► AIProvider  (builtin / openrouter / ollama / lmstudio)
    ├── Reasoning layer  ─► structured multi-step reasoning for each task type
    ├── Context builder  ─► enriches every prompt with pipeline context
    └── JSON parser      ─► safely extracts structured data from LLM output

All 22 NEXUS agents route their generation requests through this class.
Swapping AI providers requires only a settings change — zero agent rewrites.

Fallback chain
--------------
  Configured provider → BuiltinProvider (if configured provider fails)

This guarantees the pipeline always completes even without internet access
or a configured API key.
"""

from __future__ import annotations

import json
import re

from core.provider_manager import ProviderManager
from core.logger import Logger


_log = Logger()


class NexusAI:
    """
    Central AI engine for the NEXUS pipeline.

    Usage (inside any agent)
    ------------------------
    from core.nexus_ai import NexusAI

    nexus = NexusAI(self.memory)
    code  = nexus.generate_code(goal, project_type, modules, architecture)
    plan  = nexus.parse_json(nexus.generate_plan(goal, ptype, features, complexity))
    """

    def __init__(self, shared_memory=None) -> None:
        self._memory   = shared_memory
        self._provider = None   # lazy — loaded on first call

    # ------------------------------------------------------------------ #
    # Core generate()                                                       #
    # ------------------------------------------------------------------ #

    def generate(
        self,
        prompt:  str,
        system:  str = "",
        context: dict | None = None,
        **kwargs,
    ) -> str:
        """
        Generate text using the active AI provider.

        Parameters
        ----------
        prompt  : user / instruction text
        system  : optional system-level instruction
        context : optional pipeline state dict used to enrich the prompt
        **kwargs: forwarded to the provider (model, temperature, max_tokens …)

        Returns
        -------
        str — raw generated text (may be JSON, code, or prose)
        """
        provider = self._provider_instance()

        full_prompt = self._build_prompt(prompt, context)

        try:
            result = provider.generate(full_prompt, system=system, **kwargs)
            _log.info(f"[{provider.name()}] ✓ {len(result)} chars generated")
            return result
        except Exception as exc:
            _log.warning(
                f"Provider '{provider.name()}' failed ({exc}). "
                "Falling back to NEXUS Built-in Engine."
            )
            from core.providers.builtin import BuiltinProvider
            return BuiltinProvider().generate(full_prompt, system=system)

    # ------------------------------------------------------------------ #
    # Specialised generation methods (called by agents)                    #
    # ------------------------------------------------------------------ #

    def generate_requirements(self, goal: str, vision_spec: dict) -> str:
        """Parse a goal/vision doc into structured requirements JSON."""
        system = (
            "You are a senior requirements analyst. "
            "Extract precise, actionable requirements from the user's goal. "
            "Output ONLY valid JSON — no prose, no markdown fences."
        )
        prompt = f"""Extract requirements from this software goal and return a JSON object.

Goal: {goal}

Return this exact JSON structure:
{{
  "functional_requirements": ["<req1>", "..."],
  "non_functional_requirements": ["<req1>", "..."],
  "features": ["<feature1>", "..."],
  "modules": ["<module_name1>", "..."],
  "technologies": ["<tech1>", "..."],
  "complexity": "simple" | "moderate" | "complex" | "enterprise",
  "estimated_phases": <number>
}}"""
        return self.generate(prompt, system=system,
                             context={"goal": goal})

    def generate_plan(
        self,
        goal:       str,
        ptype:      str,
        features:   list,
        complexity: str,
    ) -> str:
        """Generate a phased project execution plan as JSON."""
        system = (
            "You are an expert software project manager. "
            "Generate detailed, realistic project plans. "
            "Output ONLY valid JSON — no prose, no markdown fences."
        )
        feat_str = ", ".join(features[:10]) if features else "core functionality"
        prompt = f"""Create a phased project execution plan.

Goal      : {goal}
Type      : {ptype}
Complexity: {complexity}
Features  : {feat_str}

Return this JSON structure:
{{
  "phases": [
    {{
      "name": "<phase name>",
      "description": "<what this phase delivers>",
      "tasks": ["<task1>", "..."],
      "effort_hours": <number>
    }}
  ],
  "total_phases": <number>,
  "estimated_total_hours": <number>,
  "execution_strategy": "<string>",
  "risks": [
    {{"risk": "<string>", "severity": "LOW|MEDIUM|HIGH", "mitigation": "<string>"}}
  ],
  "calendar_estimate": {{
    "optimistic_days": <number>,
    "realistic_days": <number>,
    "pessimistic_days": <number>
  }}
}}"""
        return self.generate(prompt, system=system,
                             context={"goal": goal, "project_type": ptype})

    def generate_architecture(
        self,
        goal:    str,
        ptype:   str,
        modules: list,
    ) -> str:
        """Design a system architecture as JSON."""
        system = (
            "You are a principal software architect. "
            "Design clean, scalable, production-grade system architectures. "
            "Output ONLY valid JSON — no prose, no markdown fences."
        )
        mod_str = ", ".join(modules[:8]) if modules else "core modules"
        prompt = f"""Design the system architecture for this project.

Goal   : {goal}
Type   : {ptype}
Modules: {mod_str}

Return this JSON structure:
{{
  "architecture_pattern": "<pattern name>",
  "framework": "<framework>",
  "language": "Python 3.11+",
  "database": "<database>",
  "authentication": "<auth method or None>",
  "api_style": "<REST|GraphQL|CLI|gRPC>",
  "architecture_reason": "<one paragraph explaining the choice>",
  "layers": {{
    "presentation":   {{"description": "...", "components": ["..."]}},
    "business_logic": {{"description": "...", "components": ["..."]}},
    "data_access":    {{"description": "...", "components": ["..."]}},
    "security":       {{"description": "...", "components": ["..."]}},
    "infrastructure": {{"description": "...", "components": ["..."]}}
  }}
}}"""
        return self.generate(prompt, system=system,
                             context={"goal": goal, "project_type": ptype})

    def generate_code(
        self,
        goal:         str,
        project_type: str,
        modules:      list,
        architecture: dict,
    ) -> str:
        """Generate complete, production-grade Python source code."""
        system = (
            "You are a senior Python engineer. "
            "Write complete, production-grade, immediately runnable Python code. "
            "Include proper error handling, docstrings, type hints, and a CLI entry point. "
            "Output ONLY Python code — no explanations, no markdown fences."
        )
        arch_pat = architecture.get("architecture_pattern", "Modular")
        arch_fw  = architecture.get("framework",            "Python stdlib")
        arch_db  = architecture.get("database",             "SQLite")
        mod_str  = ", ".join(modules[:8]) if modules else "core logic"

        prompt = f"""Generate a complete Python application.

Goal              : {goal}
Project Type      : {project_type}
Architecture      : {arch_pat}
Framework         : {arch_fw}
Database          : {arch_db}
Required Modules  : {mod_str}

Requirements:
- Fully functional and immediately runnable
- Uses {arch_fw} and {arch_db}
- Implements all required modules listed above
- Full error handling with try/except throughout
- Type hints on all functions and methods
- Docstrings on all classes and public methods
- argparse-based CLI with subcommands
- At least 200 lines of real, working implementation
- No placeholder pass statements in logic paths
"""
        return self.generate(prompt, system=system,
                             context={"goal": goal, "project_type": project_type})

    def generate_review(self, code: str, project_type: str) -> str:
        """Review code quality and return a structured JSON report."""
        system = (
            "You are a senior code reviewer and security expert. "
            "Perform thorough, honest code reviews. "
            "Output ONLY valid JSON — no prose, no markdown fences."
        )
        snippet = code[:3500] if len(code) > 3500 else code
        prompt = f"""Review this Python code for quality, security, and best practices.

Project Type: {project_type}

Code:
{snippet}

Return this JSON structure:
{{
  "quality_score": <0-100>,
  "approved": <true if score >= 70>,
  "technical_debt": <0-100>,
  "issues": ["<issue1>", "..."],
  "strengths": ["<strength1>", "..."],
  "release_recommendation": "APPROVED|NEEDS_REVISION|REJECTED"
}}"""
        return self.generate(prompt, system=system)

    def generate_tests(self, code: str, goal: str) -> str:
        """Generate a pytest test suite for the given source code."""
        system = (
            "You are an expert Python test engineer. "
            "Write comprehensive pytest suites with edge-case coverage. "
            "Output ONLY valid Python test code — no markdown fences."
        )
        snippet = code[:2500] if len(code) > 2500 else code
        prompt = f"""Write a complete pytest test suite for this Python application.

Goal: {goal}

Source code:
{snippet}

Requirements:
- Use pytest (no unittest)
- At least 8 meaningful test functions
- Cover happy paths, edge cases, and error conditions
- Each test has a clear docstring explaining what it tests
- Include a test for import, a test for empty/None input, and a test for boundary values
"""
        return self.generate(prompt, system=system,
                             context={"goal": goal})

    def generate_docs(self, goal: str, architecture: dict, project_type: str) -> str:
        """Generate a professional README.md."""
        system = (
            "You are a technical writer. "
            "Write clear, professional documentation. "
            "Output only the markdown content."
        )
        prompt = f"""Write a professional README.md for this project.

Goal         : {goal}
Project Type : {project_type}
Architecture : {architecture.get('architecture_pattern', 'Modular')}
Framework    : {architecture.get('framework', 'Python stdlib')}
Database     : {architecture.get('database', 'SQLite')}

Include: Overview, Requirements, Installation, Usage (with examples),
Architecture table, Running tests, Contributing guide, License.
"""
        return self.generate(prompt, system=system,
                             context={"goal": goal})

    # ------------------------------------------------------------------ #
    # JSON utilities                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def parse_json(text: str, fallback: dict | None = None) -> dict:
        """
        Safely parse JSON from AI output.

        Handles:
          - Pure JSON strings
          - JSON wrapped in ```json ... ``` fences
          - JSON embedded in prose (finds first { or [)
        """
        if not text:
            return fallback or {}

        # Strip markdown fences
        clean = re.sub(r"```(?:json)?\s*", "", text)
        clean = re.sub(r"```\s*",          "", clean).strip()

        # Try direct parse
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        # Try extracting first JSON object or array
        for start_ch, end_ch in [('{', '}'), ('[', ']')]:
            start = clean.find(start_ch)
            end   = clean.rfind(end_ch)
            if start != -1 and end > start:
                try:
                    return json.loads(clean[start:end + 1])
                except json.JSONDecodeError:
                    pass

        return fallback or {}

    # ------------------------------------------------------------------ #
    # Internal                                                              #
    # ------------------------------------------------------------------ #

    def _provider_instance(self):
        """Lazy-load and cache the configured AI provider."""
        if self._provider is None:
            self._provider = ProviderManager.get_provider()
            _log.info(f"AI Provider: {self._provider.name()}")
        return self._provider

    @staticmethod
    def _build_prompt(prompt: str, context: dict | None) -> str:
        """Prefix the prompt with relevant pipeline context."""
        if not context:
            return prompt
        parts = []
        if "goal" in context:
            parts.append(f"Project Goal: {context['goal']}")
        if "project_type" in context:
            parts.append(f"Project Type: {context['project_type']}")
        if "modules" in context:
            mods = context["modules"]
            parts.append(f"Modules: {', '.join(mods[:6])}")
        header = "\n".join(parts)
        return f"{header}\n\n{prompt}" if header else prompt
