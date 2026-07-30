"""
NEXUS
Provider Manager

Module ID : PROVIDER-MANAGER-001
Version   : 1.0.0

Central registry for all AI provider adapters.
Handles provider selection, instantiation, availability checks,
and runtime switching without restarting NEXUS.

Provider IDs
------------
  builtin    : NEXUS Built-in Engine   (always available, no setup)
  openrouter : OpenRouter API          (free tier: Llama, Mistral, Gemma, Qwen)
  ollama     : Ollama local server     (install https://ollama.ai)
  lmstudio   : LM Studio local server  (install https://lmstudio.ai)
"""

from __future__ import annotations

import importlib

from core.ai_provider import AIProvider
from core.settings import Settings


# ── Provider registry ────────────────────────────────────────────────
#   id → (module_path, class_name, display_name, notes)

_REGISTRY: dict[str, tuple[str, str, str, str]] = {
    "builtin": (
        "core.providers.builtin",
        "BuiltinProvider",
        "NEXUS Built-in Engine",
        "Rule-based orchestration engine. Always available. No API key needed.",
    ),
    "openrouter": (
        "core.providers.openrouter",
        "OpenRouterProvider",
        "OpenRouter",
        "Cloud API. Free models: Llama 3.1, Mistral 7B, Gemma 2, Qwen 2. "
        "Requires OPENROUTER_API_KEY secret. Get one free at https://openrouter.ai/keys",
    ),
    "ollama": (
        "core.providers.ollama",
        "OllamaProvider",
        "Ollama (Local)",
        "Run open-weight models locally. Install: https://ollama.ai  "
        "then: ollama pull llama3.2 && ollama serve",
    ),
    "lmstudio": (
        "core.providers.lmstudio",
        "LMStudioProvider",
        "LM Studio (Local)",
        "OpenAI-compatible local server. Download: https://lmstudio.ai  "
        "Load a model, then start the local server.",
    ),
}


class ProviderManager:
    """
    Manages AI provider selection and instantiation.

    All methods are class-level — no instance required.
    """

    # ------------------------------------------------------------------ #
    # Public API                                                            #
    # ------------------------------------------------------------------ #

    @classmethod
    def get_provider(cls) -> AIProvider:
        """Return an instance of the currently configured provider."""
        provider_id = Settings.get("ai_provider", "builtin")
        return cls._instantiate(provider_id)

    @classmethod
    def set_provider(cls, provider_id: str) -> bool:
        """
        Switch to *provider_id*.  Returns True on success, False if unknown.
        """
        if provider_id not in _REGISTRY:
            return False
        Settings.set("ai_provider", provider_id)
        return True

    @classmethod
    def list_providers(cls) -> list[dict]:
        """
        Return metadata for every registered provider, including
        live availability status and whether it is currently active.
        """
        active = Settings.get("ai_provider", "builtin")
        results = []

        for pid, (mod, cls_name, display, notes) in _REGISTRY.items():
            try:
                instance  = cls._instantiate(pid)
                available = instance.is_available()
            except Exception:
                available = False

            results.append({
                "id":        pid,
                "name":      display,
                "available": available,
                "active":    pid == active,
                "notes":     notes,
            })

        return results

    @classmethod
    def provider_ids(cls) -> list[str]:
        return list(_REGISTRY.keys())

    @classmethod
    def describe(cls, provider_id: str) -> dict | None:
        entry = _REGISTRY.get(provider_id)
        if not entry:
            return None
        _, _, display, notes = entry
        return {"id": provider_id, "name": display, "notes": notes}

    # ------------------------------------------------------------------ #
    # Internal                                                              #
    # ------------------------------------------------------------------ #

    @classmethod
    def _instantiate(cls, provider_id: str) -> AIProvider:
        entry = _REGISTRY.get(provider_id)
        if not entry:
            # Fallback to builtin
            from core.providers.builtin import BuiltinProvider
            return BuiltinProvider()
        mod_path, class_name, _, _ = entry
        mod = importlib.import_module(mod_path)
        return getattr(mod, class_name)()
