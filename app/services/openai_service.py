"""
OpenAI API service for handling chat completions
"""

import asyncio
import logging
from typing import AsyncGenerator, Dict, List, Optional
import openai
from openai import AsyncOpenAI
import json

from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.default_model = settings.DEFAULT_MODEL
        self.max_tokens = settings.MAX_TOKENS

    async def create_chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Create a non-streaming chat completion"""
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

            return ChatResponse(
                id=response.id,
                object=response.object,
                created=response.created,
                model=response.model,
                choices=[
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
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            )

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {str(e)}")
            raise Exception(f"Chat completion failed: {str(e)}")

    async def create_chat_completion_stream(
        self, 
        request: ChatRequest
    ) -> AsyncGenerator[Dict, None]:
        """Create a streaming chat completion"""
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

                    # Send final chunk with finish reason
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

        except openai.APIError as e:
            logger.error(f"OpenAI API streaming error: {str(e)}")
            raise Exception(f"OpenAI streaming error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in streaming: {str(e)}")
            raise Exception(f"Streaming failed: {str(e)}")

    async def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            # Return default models if API call fails
            return [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ]

    async def health_check(self) -> Dict[str, str]:
        """Check OpenAI API health"""
        try:
            # Try to list models as a health check
            models = await self.client.models.list()
            return {"status": "healthy", "models_count": len(models.data)}
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}


# Global service instance
openai_service = OpenAIService()
