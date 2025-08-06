from pydantic_settings import BaseSettings
from typing import Dict, List, Optional
import os

class Settings(BaseSettings):
    # Gateway Settings
    APP_NAME: str = "API Gateway"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    JOB_SERVICE_URL: str = "http://job-service:8002"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8003"
    
    # Authentication
    SECRET_KEY: str = "your-gateway-secret-key"
    ALGORITHM: str = "HS256"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_BURST: int = 10
    
    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60
    CIRCUIT_BREAKER_EXPECTED_EXCEPTION: tuple = (Exception,)
    
    # Request Timeout
    REQUEST_TIMEOUT: int = 30
    
    # Health Check
    HEALTH_CHECK_INTERVAL: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Service Discovery
    SERVICE_REGISTRY: Dict[str, Dict] = {
        "auth": {
            "url": AUTH_SERVICE_URL,
            "health_endpoint": "/health",
            "timeout": 10
        },
        "jobs": {
            "url": JOB_SERVICE_URL,
            "health_endpoint": "/health",
            "timeout": 30
        },
        "notifications": {
            "url": NOTIFICATION_SERVICE_URL,
            "health_endpoint": "/health",
            "timeout": 15
        }
    }
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8001

    class Config:
        env_file = ".env"

settings = Settings()
