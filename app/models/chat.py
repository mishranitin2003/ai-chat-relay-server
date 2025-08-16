"""
Pydantic models for chat functionality
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")
    name: Optional[str] = Field(None, description="Name of the sender")


class ChatRequest(BaseModel):
    """Request model for chat completions"""
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    model: Optional[str] = Field(None, description="Model to use for completion")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="Presence penalty")
    stream: Optional[bool] = Field(False, description="Whether to stream responses")
    user: Optional[str] = Field(None, description="User identifier for monitoring")


class ChatChoice(BaseModel):
    """Individual choice in chat response"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str]


class ChatUsage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    """Response model for chat completions"""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatChoice]
    usage: ChatUsage
