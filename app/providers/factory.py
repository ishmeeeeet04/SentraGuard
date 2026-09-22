"""
Factory function: returns the "active" LLM provider.
Right now it always returns Groq. Later, this is the ONLY place we'll
change to switch providers (e.g. based on a setting, or per-organization
configuration) — nothing else in the app needs to know or care.
"""

from app.providers.base import LLMProvider
from app.providers.groq_provider import GroqProvider


def get_llm_provider() -> LLMProvider:
    return GroqProvider()