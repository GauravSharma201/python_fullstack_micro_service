from fastapi import APIRouter, status
from app.services.service_discovery import service_registry
from app.config import settings
import redis
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """Gateway health check endpoint."""
    
    # Check Redis connectivity
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        redis_healthy = True
    except Exception:
        redis_healthy = False
    
    # Check dependent services
    services_health = {}
    for service_name in service_registry.services.keys():
        services_health[service_name] = service_registry.healthy_services.get(
            service_name, False
        )
    
    overall_health = redis_healthy and all(services_health.values())
    
    response = {
        "status": "healthy" if overall_health else "unhealthy",
        "timestamp": int(time.time()),
        "version": settings.VERSION,
        "services": {
            "redis": redis_healthy,
            **services_health
        }
    }
    
    status_code = status.HTTP_200_OK if overall_health else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return response

@router.get("/readiness")
async def readiness_check():
    """Readiness probe for Kubernetes."""
    return {"status": "ready"}

@router.get("/liveness")
async def liveness_check():
    """Liveness probe for Kubernetes."""
    return {"status": "alive"}
