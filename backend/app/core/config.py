"""
Application configuration settings
"""

from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator
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
    S3_BUCKET: str = "terra-mystica-images"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your_jwt_secret_key_here_make_it_long_and_random"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ML Configuration
    GEOCL IP_MODEL_PATH: str = "/app/models/geocl ip"
    MODEL_CACHE_SIZE: int = 1
    ENABLE_GPU: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()