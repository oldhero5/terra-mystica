"""
Environment Tools for MCP Server
Provides environment variable access for CrewAI agents
"""

import os
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger(__name__)


class EnvironmentTools:
    """Environment variable tools for MCP server"""
    
    def __init__(self, allowed_prefixes: Optional[List[str]] = None):
        """
        Initialize environment tools
        
        Args:
            allowed_prefixes: List of allowed environment variable prefixes for security
        """
        # Default allowed prefixes for Terra Mystica
        self.allowed_prefixes = allowed_prefixes or [
            "TERRA_",
            "API_",
            "DATABASE_",
            "REDIS_",
            "AWS_",
            "OPENAI_",
            "CREWAI_",
            "MCP_",
            "FASTAPI_",
            "UVICORN_",
            "CELERY_",
            "OPENSEARCH_",
            "S3_",
            "JWT_",
            "CORS_",
            "DEBUG",
            "ENVIRONMENT",
            "LOG_",
            "PROMETHEUS_",
            "WEBHOOK_",
        ]
        
        # Sensitive patterns to exclude from listing
        self.sensitive_patterns = [
            "PASSWORD",
            "SECRET",
            "KEY",
            "TOKEN",
            "CREDENTIAL",
            "PRIVATE",
        ]
        
        logger.info("EnvironmentTools initialized", 
                   allowed_prefixes=self.allowed_prefixes)
    
    def _is_allowed_variable(self, var_name: str) -> bool:
        """
        Check if environment variable is allowed to be accessed
        
        Args:
            var_name: Variable name to check
            
        Returns:
            True if variable is allowed
        """
        # Check if variable starts with any allowed prefix
        for prefix in self.allowed_prefixes:
            if var_name.startswith(prefix):
                return True
        return False
    
    def _is_sensitive_variable(self, var_name: str) -> bool:
        """
        Check if environment variable contains sensitive information
        
        Args:
            var_name: Variable name to check
            
        Returns:
            True if variable is likely sensitive
        """
        var_upper = var_name.upper()
        for pattern in self.sensitive_patterns:
            if pattern in var_upper:
                return True
        return False
    
    def get_env_var(self, var_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable value
        
        Args:
            var_name: Environment variable name
            default: Default value if variable not found
            
        Returns:
            Environment variable value or default
        """
        try:
            # Security check
            if not self._is_allowed_variable(var_name):
                logger.warning("Access denied to environment variable", var_name=var_name)
                return f"Access denied: {var_name} is not in allowed prefixes"
            
            value = os.getenv(var_name, default)
            
            # Mask sensitive values in logs
            if self._is_sensitive_variable(var_name) and value:
                log_value = f"{value[:3]}***{value[-3:]}" if len(value) > 6 else "***"
                logger.info("Environment variable retrieved", 
                           var_name=var_name, value=log_value, masked=True)
            else:
                logger.info("Environment variable retrieved", 
                           var_name=var_name, value=value, masked=False)
            
            return value
            
        except Exception as e:
            logger.error("Failed to get environment variable", 
                        var_name=var_name, error=str(e))
            return None
    
    def list_env_vars(self, prefix: Optional[str] = None, 
                      include_sensitive: bool = False) -> Dict[str, str]:
        """
        List environment variables
        
        Args:
            prefix: Optional prefix to filter variables
            include_sensitive: Whether to include sensitive variables (masked)
            
        Returns:
            Dictionary of environment variables
        """
        try:
            result = {}
            
            for var_name, value in os.environ.items():
                # Apply prefix filter if specified
                if prefix and not var_name.startswith(prefix):
                    continue
                
                # Security check
                if not self._is_allowed_variable(var_name):
                    continue
                
                # Handle sensitive variables
                if self._is_sensitive_variable(var_name):
                    if not include_sensitive:
                        continue
                    # Mask sensitive values
                    if value and len(value) > 6:
                        result[var_name] = f"{value[:3]}***{value[-3:]}"
                    else:
                        result[var_name] = "***"
                else:
                    result[var_name] = value
            
            logger.info("Environment variables listed", 
                       prefix=prefix, count=len(result), include_sensitive=include_sensitive)
            return result
            
        except Exception as e:
            logger.error("Failed to list environment variables", 
                        prefix=prefix, error=str(e))
            return {"error": str(e)}
    
    def get_terra_mystica_config(self) -> Dict[str, Any]:
        """
        Get Terra Mystica specific configuration from environment
        
        Returns:
            Dictionary with Terra Mystica configuration
        """
        try:
            config = {
                "api": {
                    "host": self.get_env_var("API_HOST", "0.0.0.0"),
                    "port": int(self.get_env_var("API_PORT", "8000")),
                    "debug": self.get_env_var("DEBUG", "false").lower() == "true",
                    "environment": self.get_env_var("ENVIRONMENT", "development"),
                    "cors_origins": self.get_env_var("CORS_ORIGINS", "").split(",") if self.get_env_var("CORS_ORIGINS") else [],
                },
                "database": {
                    "url": self.get_env_var("DATABASE_URL"),
                    "pool_size": int(self.get_env_var("DATABASE_POOL_SIZE", "5")),
                    "echo": self.get_env_var("DATABASE_ECHO", "false").lower() == "true",
                },
                "redis": {
                    "url": self.get_env_var("REDIS_URL", "redis://localhost:6379"),
                    "db": int(self.get_env_var("REDIS_DB", "0")),
                },
                "aws": {
                    "region": self.get_env_var("AWS_REGION", "us-west-2"),
                    "s3_bucket": self.get_env_var("AWS_S3_BUCKET"),
                    "access_key_id": "***" if self.get_env_var("AWS_ACCESS_KEY_ID") else None,
                    "secret_access_key": "***" if self.get_env_var("AWS_SECRET_ACCESS_KEY") else None,
                },
                "ml": {
                    "openai_api_key": "***" if self.get_env_var("OPENAI_API_KEY") else None,
                    "model_path": self.get_env_var("ML_MODEL_PATH", "/app/models"),
                    "gpu_enabled": self.get_env_var("GPU_ENABLED", "false").lower() == "true",
                },
                "celery": {
                    "broker_url": self.get_env_var("CELERY_BROKER_URL", "redis://localhost:6379/0"),
                    "result_backend": self.get_env_var("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
                },
                "logging": {
                    "level": self.get_env_var("LOG_LEVEL", "INFO"),
                    "format": self.get_env_var("LOG_FORMAT", "json"),
                },
                "security": {
                    "jwt_secret": "***" if self.get_env_var("JWT_SECRET_KEY") else None,
                    "jwt_algorithm": self.get_env_var("JWT_ALGORITHM", "HS256"),
                    "access_token_expire_minutes": int(self.get_env_var("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
                },
                "mcp": {
                    "server_name": self.get_env_var("MCP_SERVER_NAME", "Terra Mystica MCP Server"),
                    "transport": self.get_env_var("MCP_TRANSPORT", "stdio"),
                    "host": self.get_env_var("MCP_HOST", "0.0.0.0"),
                    "port": int(self.get_env_var("MCP_PORT", "8001")),
                }
            }
            
            # Remove None values
            def clean_dict(d):
                if isinstance(d, dict):
                    return {k: clean_dict(v) for k, v in d.items() if v is not None}
                return d
            
            config = clean_dict(config)
            
            logger.info("Terra Mystica configuration retrieved", 
                       sections=list(config.keys()))
            return config
            
        except Exception as e:
            logger.error("Failed to get Terra Mystica configuration", error=str(e))
            return {"error": str(e)}
    
    def validate_required_env_vars(self) -> Dict[str, Any]:
        """
        Validate that required environment variables are set
        
        Returns:
            Validation results
        """
        required_vars = [
            "DATABASE_URL",
            "JWT_SECRET_KEY",
            "OPENAI_API_KEY",
            "REDIS_URL",
        ]
        
        optional_vars = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY", 
            "AWS_S3_BUCKET",
            "CELERY_BROKER_URL",
            "CELERY_RESULT_BACKEND",
        ]
        
        results = {
            "valid": True,
            "required": {},
            "optional": {},
            "missing_required": [],
            "missing_optional": [],
        }
        
        # Check required variables
        for var in required_vars:
            value = self.get_env_var(var)
            is_set = value is not None and value.strip() != ""
            results["required"][var] = is_set
            
            if not is_set:
                results["valid"] = False
                results["missing_required"].append(var)
        
        # Check optional variables
        for var in optional_vars:
            value = self.get_env_var(var)
            is_set = value is not None and value.strip() != ""
            results["optional"][var] = is_set
            
            if not is_set:
                results["missing_optional"].append(var)
        
        logger.info("Environment validation completed", 
                   valid=results["valid"], 
                   missing_required=len(results["missing_required"]),
                   missing_optional=len(results["missing_optional"]))
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information from environment
        
        Returns:
            System information dictionary
        """
        try:
            info = {
                "platform": {
                    "os": os.name,
                    "path_separator": os.pathsep,
                    "line_separator": repr(os.linesep),
                },
                "python": {
                    "executable": os.sys.executable,
                    "version": os.sys.version,
                    "path": os.sys.path[:5],  # First 5 entries only
                },
                "process": {
                    "pid": os.getpid(),
                    "ppid": os.getppid() if hasattr(os, 'getppid') else None,
                    "cwd": os.getcwd(),
                    "user": self.get_env_var("USER") or self.get_env_var("USERNAME"),
                },
                "environment": {
                    "home": self.get_env_var("HOME") or self.get_env_var("USERPROFILE"),
                    "shell": self.get_env_var("SHELL"),
                    "term": self.get_env_var("TERM"),
                    "lang": self.get_env_var("LANG"),
                    "timezone": self.get_env_var("TZ"),
                }
            }
            
            logger.info("System information retrieved")
            return info
            
        except Exception as e:
            logger.error("Failed to get system information", error=str(e))
            return {"error": str(e)}