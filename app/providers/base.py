"""
The common "shape" every LLM provider must follow.
Nothing else in the app is allowed to talk to a specific provider's SDK
directly — everything goes through this interface. This is what makes
swapping Groq for OpenAI, Claude, or Ollama later a small, isolated change.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, message: str) -> str:
        """
        Send a single user message to the LLM and return its text reply.
        Every provider (Groq, OpenAI, Claude, Ollama) must implement this
        exact method signature.
        """
        raise NotImplementedError