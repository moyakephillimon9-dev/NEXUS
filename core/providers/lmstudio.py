"""
NEXUS
LM Studio AI Provider

Module ID : LMSTUDIO-001
Version   : 1.0.0

Connects to a locally running LM Studio instance.
LM Studio exposes an OpenAI-compatible REST API, so this provider
works with any model loaded in LM Studio.

Download LM Studio : https://lmstudio.ai
Load a model and start the local server (default: http://localhost:1234).

Popular models available in LM Studio:
  • Llama 3.2 (Meta)
  • Mistral 7B / Mixtral (Mistral AI)
  • Qwen 2.5 (Alibaba)
  • Gemma 2 (Google)
  • Phi-3 (Microsoft)
  • DeepSeek Coder (DeepSeek)

Default endpoint : http://localhost:1234
Configure via Settings: lmstudio_host, lmstudio_model

No third-party packages required — uses Python stdlib urllib only.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from core.ai_provider import AIProvider
from core.settings import Settings


class LMStudioProvider(AIProvider):

    # ------------------------------------------------------------------ #
    # AIProvider interface                                                  #
    # ------------------------------------------------------------------ #

    def name(self) -> str:
        model = Settings.get("lmstudio_model", "local-model")
        return f"LM Studio ({model})"

    def is_available(self) -> bool:
        """Ping /v1/models — fast health-check."""
        try:
            req = urllib.request.Request(
                f"{self._host()}/v1/models",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=3):
                return True
        except Exception:
            return False

    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        host        = self._host()
        model       = kwargs.get("model",       Settings.get("lmstudio_model", "local-model"))
        max_tokens  = kwargs.get("max_tokens",  Settings.get("max_tokens",  4096))
        temperature = kwargs.get("temperature", Settings.get("temperature", 0.7))

        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model":       model,
            "messages":    messages,
            "max_tokens":  max_tokens,
            "temperature": temperature,
        }).encode()

        req = urllib.request.Request(
            f"{host}/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Cannot reach LM Studio at {host}. "
                "Start the local server inside LM Studio first."
            ) from exc

    # ------------------------------------------------------------------ #
    # Helpers                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _host() -> str:
        return Settings.get("lmstudio_host", "http://localhost:1234").rstrip("/")
