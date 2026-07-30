"""
NEXUS
Ollama AI Provider

Module ID : OLLAMA-001
Version   : 1.0.0

Connects to a locally running Ollama instance, enabling fully offline,
free, private AI inference with open-weight models such as:
  • llama3.2       (Meta — general purpose)
  • mistral        (Mistral AI — fast and capable)
  • qwen2.5        (Alibaba — multilingual)
  • gemma2         (Google — lightweight)
  • codellama      (Meta — code generation)
  • phi3           (Microsoft — small but strong)

Install Ollama : https://ollama.ai
Pull a model   : ollama pull llama3.2
Start server   : ollama serve   (or it auto-starts on macOS/Linux)

Default endpoint: http://localhost:11434
Configure via Settings: ollama_host, ollama_model

No third-party packages required — uses Python stdlib urllib only.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from core.ai_provider import AIProvider
from core.settings import Settings


class OllamaProvider(AIProvider):

    # ------------------------------------------------------------------ #
    # AIProvider interface                                                  #
    # ------------------------------------------------------------------ #

    def name(self) -> str:
        model = Settings.get("ollama_model", "llama3.2")
        return f"Ollama ({model})"

    def is_available(self) -> bool:
        """Ping /api/tags — fast health-check."""
        try:
            req = urllib.request.Request(
                f"{self._host()}/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=3):
                return True
        except Exception:
            return False

    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        host       = self._host()
        model      = kwargs.get("model",      Settings.get("ollama_model", "llama3.2"))
        max_tokens = kwargs.get("max_tokens", Settings.get("max_tokens",   4096))

        # Ollama /api/generate uses a single prompt string
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        payload = json.dumps({
            "model":   model,
            "prompt":  full_prompt,
            "stream":  False,
            "options": {"num_predict": max_tokens},
        }).encode()

        req = urllib.request.Request(
            f"{host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            return data.get("response", "")
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Cannot reach Ollama at {host}. "
                "Make sure Ollama is running: `ollama serve`"
            ) from exc

    # ------------------------------------------------------------------ #
    # Helpers                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _host() -> str:
        return Settings.get("ollama_host", "http://localhost:11434").rstrip("/")
