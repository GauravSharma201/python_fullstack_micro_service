import httpx
import asyncio
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from app.config import settings
from app.services.service_discovery import service_registry
import structlog

logger = structlog.get_logger()

class GatewayHTTPClient:
    def __init__(self):
        self.timeout = httpx.Timeout(settings.REQUEST_TIMEOUT)
        
    async def forward_request(
        self,
        request: Request,
        service_name: str,
        target_path: str,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """Forward request to target microservice."""
        
        # Get service URL
        service_url = await service_registry.get_service_url(service_name)
        if not service_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {service_name} is unavailable"
            )
        
        # Construct target URL
        target_url = f"{service_url}{target_path}"
        
        # Prepare headers
        forwarded_headers = self._prepare_headers(request, headers)
        
        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Get query parameters
        query_params = dict(request.query_params)
        
        try:
            # Use circuit breaker for the request
            circuit_breaker = service_registry.circuit_breakers[service_name]
            response = await circuit_breaker.call(
                self._make_request,
                request.method,
                target_url,
                headers=forwarded_headers,
                content=body,
                params=query_params
            )
            
            logger.info(
                f"Forwarded {request.method} request to {service_name}",
                target_url=target_url,
                status_code=response.status_code
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to forward request to {service_name}",
                error=str(e),
                target_url=target_url
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with {service_name} service"
            )

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        content: bytes = None,
        params: Dict[str, Any] = None
    ) -> httpx.Response:
        """Make HTTP request to microservice."""
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=content,
                params=params
            )
            return response

    def _prepare_headers(
        self,
        request: Request,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Prepare headers for forwarding."""
        
        # Start with original headers, excluding hop-by-hop headers
        headers = {}
        hop_by_hop_headers = {
            "connection", "keep-alive", "proxy-authenticate",
            "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
        }
        
        for name, value in request.headers.items():
            if name.lower() not in hop_by_hop_headers:
                headers[name] = value
        
        # Add forwarding headers
        headers["X-Forwarded-For"] = request.client.host
        headers["X-Forwarded-Proto"] = request.url.scheme
        headers["X-Gateway-Version"] = settings.VERSION
        
        # Add user information if available
        if hasattr(request.state, 'user') and request.state.user:
            headers["X-User-ID"] = str(request.state.user["user_id"])
            headers["X-Username"] = request.state.user["username"]
        
        # Add any additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        return headers

# Global HTTP client instance
http_client = GatewayHTTPClient()
