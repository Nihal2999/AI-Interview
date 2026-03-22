"""
LLM Client with automatic fallback chain:
  1. Groq (fastest, free tier)
  2. Ollama (local, unlimited - final safety net)
"""

import logging
from abc import ABC, abstractmethod
from groq import AsyncGroq
import httpx
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Base Provider ─────────────────────────────────────────────────────────────

class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def chat(self, messages: list[dict], max_tokens: int = 1024) -> str:
        pass


# ── Groq Provider ─────────────────────────────────────────────────────────────

class GroqProvider(LLMProvider):
    name = "Groq"

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def chat(self, messages: list[dict], max_tokens: int = 1024) -> str:
        response = await self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        content = (response.choices[0].message.content or '').strip()

        # If Groq returns empty, retry once with a hint
        if not content:
            logger.warning("Groq returned empty, retrying with nudge...")
            retry_messages = messages + [{
                "role": "user",
                "content": "Please respond to what I just said and continue the interview."
            }]
            retry = await self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=retry_messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            content = (retry.choices[0].message.content or '').strip()

        return content


# ── Ollama Provider ───────────────────────────────────────────────────────────

class OllamaProvider(LLMProvider):
    name = "Ollama"

    def __init__(self):
        # host.docker.internal lets Docker containers reach host machine's localhost
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def chat(self, messages: list[dict], max_tokens: int = 1024) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"num_predict": max_tokens}
                }
            )
            response.raise_for_status()
            return response.json()["message"]["content"].strip()


# ── Fallback Chain ────────────────────────────────────────────────────────────

class LLMClient:
    def __init__(self):
        self.providers: list[LLMProvider] = [
            GroqProvider(),
            OllamaProvider(),
        ]

    async def chat(self, messages: list[dict], max_tokens: int = 1024) -> str:
        last_error = None

        for provider in self.providers:
            try:
                logger.info(f"Trying provider: {provider.name}")
                result = await provider.chat(messages, max_tokens)
                logger.info(f"Success with provider: {provider.name}")
                return result
            except Exception as e:
                logger.warning(f"{provider.name} failed: {e}")
                last_error = e
                continue

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")


# Singleton instance
llm_client = LLMClient()
