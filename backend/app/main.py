"""
Terra Mystica FastAPI Application
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.api_v1.api import api_router
from mcp.fastapi_integration import (
    mcp_health, 
    mcp_info, 
    test_mcp_integration,
    setup_mcp_integration
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    setup_logging()
    logger = structlog.get_logger()
    logger.info("Terra Mystica API starting up", version="0.1.0")
    
    # Initialize MCP integration
    try:
        mcp_integration = setup_mcp_integration(app)
        logger.info("MCP server integration initialized")
    except Exception as e:
        logger.error("Failed to initialize MCP integration", error=str(e))
        # Continue without MCP if it fails
    
    yield
    
    # Shutdown
    logger.info("Terra Mystica API shutting down")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-powered geolocation service for outdoor images",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "terra-mystica-api", "version": "0.1.0"}


@app.get("/mcp/health")
async def mcp_health_endpoint():
    """MCP server health check endpoint"""
    return await mcp_health()


@app.get("/mcp/info")
async def mcp_info_endpoint():
    """MCP server information endpoint"""
    return await mcp_info()


@app.get("/mcp/test")
async def mcp_test_endpoint():
    """Test MCP server functionality"""
    return await test_mcp_integration()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Terra Mystica API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "api": f"{settings.API_V1_STR}",
        "mcp": {
            "health": "/mcp/health",
            "info": "/mcp/info",
            "test": "/mcp/test"
        }
    }