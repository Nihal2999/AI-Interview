import logging
from groq import AsyncGroq
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def chat(self, messages: list[dict], max_tokens: int = 1024) -> str:
        try:
            logger.info(f"Calling Groq with model: {settings.GROQ_MODEL}")
            response = await self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            content = (response.choices[0].message.content or '').strip()
            logger.info(f"Groq response: finish_reason={response.choices[0].finish_reason}, length={len(content)}")

            # Retry once if empty
            if not content:
                logger.warning("Groq returned empty, retrying...")
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

        except Exception as e:
            logger.error(f"Groq failed: {e}")
            raise RuntimeError(f"LLM call failed: {e}")


# Singleton
llm_client = LLMClient()