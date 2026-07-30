"""
NEXUS
OpenRouter AI Provider

Module ID : OPENROUTER-001
Version   : 1.0.0

Connects to OpenRouter.ai, which proxies dozens of LLMs — including
several completely free models — through a single OpenAI-compatible API.

Free models (no billing required, just a free API key):
  • meta-llama/llama-3.1-8b-instruct:free
  • mistralai/mistral-7b-instruct:free
  • google/gemma-2-9b-it:free
  • qwen/qwen-2-7b-instruct:free

Get a free key at: https://openrouter.ai/keys
Set it as the OPENROUTER_API_KEY environment variable (Replit Secret).

No third-party packages required — uses Python stdlib urllib only.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from core.ai_provider import AIProvider
from core.settings import Settings


class OpenRouterProvider(AIProvider):

    # ------------------------------------------------------------------ #
    # AIProvider interface                                                  #
    # ------------------------------------------------------------------ #

    def name(self) -> str:
        return "OpenRouter"

    def is_available(self) -> bool:
        return bool(self._api_key())

    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        api_key = self._api_key()
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. "
                "Get a free key at https://openrouter.ai/keys and add it "
                "as a Replit Secret named OPENROUTER_API_KEY."
            )

        model       = kwargs.get("model",       Settings.get("openrouter_model",    "meta-llama/llama-3.1-8b-instruct:free"))
        base_url    = kwargs.get("base_url",    Settings.get("openrouter_base_url", "https://openrouter.ai/api/v1"))
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
            f"{base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://nexus-builder.replit.app",
                "X-Title":       "NEXUS",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            raise RuntimeError(f"OpenRouter HTTP {exc.code}: {body}") from exc

    # ------------------------------------------------------------------ #
    # Helpers                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _api_key() -> str:
        return os.environ.get("OPENROUTER_API_KEY", "").strip()
