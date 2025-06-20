"""
Application configuration settings
"""

from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator, Field
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Terra Mystica"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://terra_user:change_this_password@localhost:5432/terra_mystica"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenSearch
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USERNAME: str = "admin"
    OPENSEARCH_PASSWORD: str = "admin"
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-west-2"
    S3_BUCKET_NAME: str = "terra-mystica-images"
    S3_ENDPOINT_URL: Optional[str] = None  # For LocalStack or MinIO testing
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your_jwt_secret_key_here_make_it_long_and_random"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ML Configuration
    GEOCLIP_MODEL_PATH: str = "/app/models/geoclip"
    MODEL_CACHE_SIZE: int = 1
    ENABLE_GPU: bool = True
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_TEMPERATURE: float = Field(default=0.1)
    OPENAI_MAX_TOKENS: int = Field(default=4000)
    
    # CrewAI Configuration
    CREWAI_LOG_LEVEL: str = Field(default="INFO")
    CREWAI_AGENT_TIMEOUT: int = Field(default=120)
    CREWAI_MAX_ITERATIONS: int = Field(default=5)
    CREWAI_VERBOSE: bool = Field(default=True)
    
    # Storage Configuration
    UPLOAD_DIR: str = Field(default="/app/uploads")
    THUMBNAIL_DIR: str = Field(default="/app/thumbnails")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(default=["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"])
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


settings = Settings()