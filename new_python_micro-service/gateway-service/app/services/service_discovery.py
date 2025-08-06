import httpx
import asyncio
from typing import Dict, List, Optional
from app.config import settings
from app.services.circuit_breaker import CircuitBreaker
import structlog

logger = structlog.get_logger()

class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, Dict] = settings.SERVICE_REGISTRY.copy()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.healthy_services: Dict[str, bool] = {}
        
        # Initialize circuit breakers for each service
        for service_name in self.services.keys():
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                timeout=settings.CIRCUIT_BREAKER_TIMEOUT
            )
            self.healthy_services[service_name] = True

    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get healthy service URL."""
        if service_name not in self.services:
            return None
            
        if self.healthy_services.get(service_name, False):
            return self.services[service_name]["url"]
        
        return None

    async def health_check(self, service_name: str) -> bool:
        """Perform health check on service."""
        if service_name not in self.services:
            return False
            
        service_config = self.services[service_name]
        health_url = f"{service_config['url']}{service_config['health_endpoint']}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    health_url,
                    timeout=service_config.get("timeout", 10)
                )
                is_healthy = response.status_code == 200
                self.healthy_services[service_name] = is_healthy
                
                if is_healthy:
                    logger.info(f"Service {service_name} is healthy")
                else:
                    logger.warning(f"Service {service_name} health check failed")
                    
                return is_healthy
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {str(e)}")
            self.healthy_services[service_name] = False
            return False

    async def start_health_monitoring(self):
        """Start periodic health checks for all services."""
        while True:
            tasks = [
                self.health_check(service_name) 
                for service_name in self.services.keys()
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)

# Global service registry instance
service_registry = ServiceRegistry()
