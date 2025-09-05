from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    PROJECT_NAME: str = "Ashilog API"
    APP_ENV: str = "dev"
    PORT: int = 8080
    
    # Database Configuration
    DATABASE_URL: str
    
    # JWT Configuration
    JWT_SECRET: str
    JWT_EXPIRE_HOURS: int = 24
    ALGORITHM: str = "HS256"
    
    # CORS Configuration - 開発環境でより柔軟に
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001,https://app-002-gen10-step3-2-node-oshima13.azurewebsites.net"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # File Upload Configuration
    FILE_MAX_MB: int = 5
    UPLOAD_DIR: str = "./uploads"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    # Redis Configuration (optional)
    REDIS_HOST: Optional[str] = "localhost"
    REDIS_PORT: Optional[int] = 6379
    
    # Email Configuration (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None


settings = Settings()