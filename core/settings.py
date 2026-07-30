"""
NEXUS
Settings Manager

Module ID : SETTINGS-001
Version   : 1.0.0

Manages persistent configuration for NEXUS, including AI provider
selection and per-provider options. Written to nexus_settings.json
at the project root.
"""

from __future__ import annotations

import json
from pathlib import Path

# ------------------------------------------------------------------ #
# Defaults                                                             #
# ------------------------------------------------------------------ #

_DEFAULTS: dict = {
    # Which provider to use: "builtin" | "openrouter" | "ollama" | "lmstudio"
    "ai_provider": "builtin",

    # OpenRouter settings (https://openrouter.ai — free models available)
    "openrouter_base_url": "https://openrouter.ai/api/v1",
    "openrouter_model":    "meta-llama/llama-3.1-8b-instruct:free",

    # Ollama settings (local, https://ollama.ai)
    "ollama_host":  "http://localhost:11434",
    "ollama_model": "llama3.2",

    # LM Studio settings (local, https://lmstudio.ai)
    "lmstudio_host":  "http://localhost:1234",
    "lmstudio_model": "local-model",

    # Generation parameters
    "max_tokens":  4096,
    "temperature": 0.7,
}

_SETTINGS_FILE = Path(__file__).resolve().parent.parent / "nexus_settings.json"


# ------------------------------------------------------------------ #
# Settings class                                                        #
# ------------------------------------------------------------------ #

class Settings:
    """
    Lazy-loading key-value settings store backed by nexus_settings.json.
    All public methods are class-level so no instance is needed.
    """

    _data: dict = {}
    _loaded: bool = False

    # ── Load / Save ──────────────────────────────────────────────── #

    @classmethod
    def _load(cls) -> None:
        if _SETTINGS_FILE.exists():
            try:
                with open(_SETTINGS_FILE, encoding="utf-8") as fh:
                    cls._data = json.load(fh)
                cls._loaded = True
                return
            except Exception:
                pass
        cls._data  = dict(_DEFAULTS)
        cls._loaded = True

    @classmethod
    def _save(cls) -> None:
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as fh:
            json.dump(cls._data, fh, indent=2)

    # ── Public API ───────────────────────────────────────────────── #

    @classmethod
    def get(cls, key: str, default=None):
        if not cls._loaded:
            cls._load()
        return cls._data.get(key, _DEFAULTS.get(key, default))

    @classmethod
    def set(cls, key: str, value) -> None:
        if not cls._loaded:
            cls._load()
        cls._data[key] = value
        cls._save()

    @classmethod
    def all(cls) -> dict:
        if not cls._loaded:
            cls._load()
        return dict(cls._data)

    @classmethod
    def reset(cls) -> None:
        cls._data   = dict(_DEFAULTS)
        cls._loaded = True
        cls._save()
