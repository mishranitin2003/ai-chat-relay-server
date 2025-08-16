"""
FastAPI OpenAI Relay Server
A production-ready API server that acts as a relay for OpenAI API calls
with authentication, rate limiting, and streaming support.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.security import setup_security
from app.middleware.logging import setup_logging
from app.middleware.rate_limiting import RateLimitMiddleware
from app.api.v1.endpoints import chat, health, auth
from app.services.auth_service import auth_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting OpenAI Relay Server and initializing database if not exist...")
    # Initialize the database
    await auth_service.initialize_db()
    yield
    # Shutdown
    logger.info("Shutting down OpenAI Relay Server...")


# Create FastAPI app instance
app = FastAPI(
    title="OpenAI Relay Server",
    description="Production-ready relay server for OpenAI API with authentication and rate limiting",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Setup security
setup_security(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger = logging.getLogger(__name__)
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
