from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Any
import json
from app.utils.http_client import http_client
from app.middleware.rate_limiting import limiter
import structlog

logger = structlog.get_logger()
router = APIRouter()

# Service routing configuration
SERVICE_ROUTES = {
    "/api/v1/auth": {
        "service": "auth",
        "strip_prefix": "/api/v1"
    },
    "/api/v1/jobs": {
        "service": "jobs", 
        "strip_prefix": "/api/v1"
    },
    "/api/v1/notifications": {
        "service": "notifications",
        "strip_prefix": "/api/v1"
    }
}

@router.api_route(
    "/api/v1/auth/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
@limiter.limit("50/minute")
async def auth_service_proxy(request: Request, path: str):
    """Proxy requests to authentication service."""
    target_path = f"/auth/{path}"
    
    try:
        response = await http_client.forward_request(
            request=request,
            service_name="auth",
            target_path=target_path
        )
        
        return StreamingResponse(
            iter([response.content]),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth service proxy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable"
        )

@router.api_route(
    "/api/v1/jobs/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
@limiter.limit("30/minute")
async def job_service_proxy(request: Request, path: str):
    """Proxy requests to background job service."""
    target_path = f"/jobs/{path}"
    
    try:
        response = await http_client.forward_request(
            request=request,
            service_name="jobs",
            target_path=target_path
        )
        
        return StreamingResponse(
            iter([response.content]),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job service proxy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Job service unavailable"
        )

@router.api_route(
    "/api/v1/notifications/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
@limiter.limit("20/minute")
async def notification_service_proxy(request: Request, path: str):
    """Proxy requests to notification service."""
    target_path = f"/notifications/{path}"
    
    try:
        response = await http_client.forward_request(
            request=request,
            service_name="notifications",
            target_path=target_path
        )
        
        return StreamingResponse(
            iter([response.content]),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Notification service proxy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Notification service unavailable"
        )

@router.get("/api/v1/gateway/status")
async def gateway_status():
    """Get gateway status and service health."""
    from app.services.service_discovery import service_registry
    
    service_status = {}
    for service_name in service_registry.services.keys():
        is_healthy = await service_registry.health_check(service_name)
        service_status[service_name] = {
            "healthy": is_healthy,
            "url": service_registry.services[service_name]["url"]
        }
    
    return {
        "gateway": "healthy",
        "version": "1.0.0",
        "services": service_status
    }
