"""
NEXUS
AI Provider — Abstract Base Class

Module ID : AI-PROVIDER-001
Version   : 1.0.0

All AI provider adapters inherit from AIProvider.
NEXUS routes every generation request through this interface,
making it trivial to swap or add new backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Abstract base class for all NEXUS AI providers.

    Concrete implementations:
      - BuiltinProvider   : NEXUS rule-based engine (always available)
      - OpenRouterProvider: OpenRouter API (cloud, free models available)
      - OllamaProvider    : Ollama local server
      - LMStudioProvider  : LM Studio local server
    """

    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return True if this provider is reachable and configured.
        Should be fast (< 3 s timeout for network checks).
        """

    @abstractmethod
    def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        """
        Generate a text completion for *prompt*.

        Parameters
        ----------
        prompt : str
            The user / instruction prompt.
        system : str
            Optional system-level instruction prepended to the conversation.
        **kwargs
            Provider-specific overrides (model, temperature, max_tokens …).

        Returns
        -------
        str
            Raw generated text.  Callers are responsible for any parsing.
        """
