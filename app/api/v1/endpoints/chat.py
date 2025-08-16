"""
Chat endpoint for OpenAI API relay with streaming support
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials
import json
import asyncio
import logging
from typing import AsyncGenerator

from app.core.security import get_current_user
from app.services.perplexityai_service import llm_service as openai_service
# from app.services.openai_service import openai_service
from app.models.chat import ChatRequest, ChatResponse
from app.core.rate_limiter import rate_limiter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/completions", response_model=ChatResponse)
async def chat_completions(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Non-streaming chat completions endpoint"""
    try:
        # Check rate limit
        user_key = f"user:{current_user['user_id']}"
        if not await rate_limiter.is_allowed(user_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Call OpenAI API
        response = await openai_service.create_chat_completion(request)

        logger.info(f"Chat completion for user {current_user['user_id']}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat completions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/completions/stream")
async def chat_completions_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Streaming chat completions endpoint"""
    try:
        # Check rate limit
        user_key = f"user:{current_user['user_id']}"
        if not await rate_limiter.is_allowed(user_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Enable streaming
        request.stream = True

        async def generate_stream() -> AsyncGenerator[str, None]:
            try:
                async for chunk in openai_service.create_chat_completion_stream(request):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                error_data = {
                    "error": {
                        "message": "Stream error occurred",
                        "type": "server_error"
                    }
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        logger.info(f"Streaming chat completion for user {current_user['user_id']}")
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/models")
async def get_available_models(
    current_user: dict = Depends(get_current_user)
):
    """Get available OpenAI models"""
    try:
        models = await openai_service.get_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve models"
        )
