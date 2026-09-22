"""
Groq implementation of the LLMProvider interface.
This is the ONLY file in the entire app that is allowed to import the
Groq SDK directly.
"""

from groq import Groq

from app.core.config import settings
from app.providers.base import LLMProvider


class GroqProvider(LLMProvider):
    def __init__(self) -> None:
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def chat(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": message}],
        )
        return response.choices[0].message.content