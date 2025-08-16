import asyncio
import logging
from typing import AsyncGenerator, Dict, List, Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLM APIs (OpenAI or Perplexity)"""
    def __init__(self):
        # Use Perplexity as default if API key is set
        if settings.PERPLEXITY_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url=settings.PERPLEXITY_BASE_URL
            )
            self.default_model = settings.DEFAULT_MODEL or "sonar-medium-online"
        else:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            self.default_model = settings.DEFAULT_MODEL or "gpt-4o-mini"
        self.max_tokens = settings.MAX_TOKENS

    async def create_chat_completion(self, request):
        try:
            response = await self.client.chat.completions.create(
                model=request.model or self.default_model,
                messages=[msg.dict() for msg in request.messages],
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or self.max_tokens,
                top_p=request.top_p or 1.0,
                frequency_penalty=request.frequency_penalty or 0.0,
                presence_penalty=request.presence_penalty or 0.0,
                stream=False,
                user=request.user
            )
            return {
                "id": response.id,
                "object": response.object,
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            }
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            raise Exception(f"LLM API error: {str(e)}")

    async def create_chat_completion_stream(self, request):
        try:
            stream = await self.client.chat.completions.create(
                model=request.model or self.default_model,
                messages=[msg.dict() for msg in request.messages],
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or self.max_tokens,
                top_p=request.top_p or 1.0,
                frequency_penalty=request.frequency_penalty or 0.0,
                presence_penalty=request.presence_penalty or 0.0,
                stream=True,
                user=request.user
            )
            async for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    if choice.delta.content is not None:
                        yield {
                            "id": chunk.id,
                            "object": chunk.object,
                            "created": chunk.created,
                            "model": chunk.model,
                            "choices": [
                                {
                                    "index": choice.index,
                                    "delta": {
                                        "content": choice.delta.content
                                    },
                                    "finish_reason": choice.finish_reason
                                }
                            ]
                        }
                    if choice.finish_reason:
                        yield {
                            "id": chunk.id,
                            "object": chunk.object,
                            "created": chunk.created,
                            "model": chunk.model,
                            "choices": [
                                {
                                    "index": choice.index,
                                    "delta": {},
                                    "finish_reason": choice.finish_reason
                                }
                            ]
                        }
        except Exception as e:
            logger.error(f"LLM streaming error: {str(e)}")
            raise Exception(f"LLM streaming error: {str(e)}")

    async def get_available_models(self) -> List[str]:
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            # Return default models if API call fails
            return [
                "sonar-medium-online",
                "sonar-small-online",
                "sonar-medium-chat",
                "sonar-small-chat"
            ]

    async def health_check(self) -> Dict[str, str]:
        try:
            models = await self.client.models.list()
            return {"status": "healthy", "models_count": len(models.data)}
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

llm_service = LLMService()
