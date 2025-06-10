"""
MCP Server Configuration
Configuration settings for Terra Mystica MCP server
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class MCPServerConfig(BaseSettings):
    """MCP Server configuration"""
    
    # Server Identity
    server_name: str = Field(default="Terra Mystica MCP Server", env="MCP_SERVER_NAME")
    version: str = Field(default="1.0.0", env="MCP_VERSION")
    
    # Transport Configuration
    transport: str = Field(default="stdio", env="MCP_TRANSPORT")  # stdio, sse, http
    host: str = Field(default="0.0.0.0", env="MCP_HOST")
    port: int = Field(default=8001, env="MCP_PORT")
    
    # API Configuration
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    api_timeout: float = Field(default=30.0, env="API_TIMEOUT")
    
    # Security
    allowed_env_prefixes: List[str] = Field(
        default=[
            "TERRA_", "API_", "DATABASE_", "REDIS_", "AWS_", "OPENAI_",
            "CREWAI_", "MCP_", "FASTAPI_", "UVICORN_", "CELERY_",
            "OPENSEARCH_", "S3_", "JWT_", "CORS_", "DEBUG", "ENVIRONMENT",
            "LOG_", "PROMETHEUS_", "WEBHOOK_"
        ],
        env="MCP_ALLOWED_ENV_PREFIXES"
    )
    
    # File System
    base_path: str = Field(default="/Users/marty/repos/terra-mystica/backend", env="MCP_BASE_PATH")
    uploads_path: str = Field(default="uploads", env="MCP_UPLOADS_PATH")
    thumbnails_path: str = Field(default="thumbnails", env="MCP_THUMBNAILS_PATH")
    
    # Logging
    log_level: str = Field(default="INFO", env="MCP_LOG_LEVEL")
    
    # Authentication (for SSE/HTTP transports)
    auth_enabled: bool = Field(default=False, env="MCP_AUTH_ENABLED")
    auth_secret: Optional[str] = Field(default=None, env="MCP_AUTH_SECRET")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class MCPClientConfig(BaseModel):
    """Configuration for MCP clients"""
    
    name: str
    description: str
    transport: str = "stdio"
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None


def get_mcp_config() -> MCPServerConfig:
    """Get MCP server configuration"""
    return MCPServerConfig()


def get_claude_client_config() -> MCPClientConfig:
    """Get configuration for Claude MCP client"""
    return MCPClientConfig(
        name="terra-mystica",
        description="Terra Mystica geolocation service MCP server",
        transport="stdio",
        command="python",
        args=["-m", "mcp.server"],
        env={
            "MCP_SERVER_NAME": "Terra Mystica MCP Server",
            "API_BASE_URL": "http://localhost:8000",
            "MCP_TRANSPORT": "stdio"
        }
    )


def generate_claude_config() -> Dict[str, Any]:
    """Generate Claude Desktop configuration for MCP"""
    config = get_claude_client_config()
    
    return {
        "mcpServers": {
            config.name: {
                "command": config.command,
                "args": config.args,
                "env": config.env
            }
        }
    }


def get_crewai_integration_config() -> Dict[str, Any]:
    """Get configuration for CrewAI integration"""
    return {
        "mcp_server": {
            "enabled": True,
            "transport": "stdio",
            "tools": {
                "filesystem": {
                    "enabled": True,
                    "base_path": "/Users/marty/repos/terra-mystica/backend",
                    "allowed_operations": ["read", "write", "list", "info"]
                },
                "http": {
                    "enabled": True,
                    "base_url": "http://localhost:8000",
                    "timeout": 30.0,
                    "allowed_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"]
                },
                "environment": {
                    "enabled": True,
                    "allowed_prefixes": [
                        "TERRA_", "API_", "DATABASE_", "REDIS_", "AWS_",
                        "OPENAI_", "CREWAI_", "MCP_"
                    ]
                },
                "directory": {
                    "enabled": True,
                    "uploads_management": True,
                    "thumbnail_management": True,
                    "temp_cleanup": True
                }
            }
        }
    }