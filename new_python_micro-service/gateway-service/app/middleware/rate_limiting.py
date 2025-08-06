from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

def get_user_id(request: Request) -> str:
    """Get user ID for rate limiting. Falls back to IP if user not authenticated."""
    if hasattr(request.state, 'user') and request.state.user:
        return f"user:{request.state.user['user_id']}"
    return f"ip:{get_remote_address(request)}"

# Create limiter instance
limiter = Limiter(
    key_func=get_user_id,
    storage_uri=settings.REDIS_URL,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/minute"]
)

class RateLimitMiddleware:
    def __init__(self):
        self.limiter = limiter
        
    async def __call__(self, request: Request, call_next):
        try:
            # Apply rate limiting
            await self.check_rate_limit(request)
            response = await call_next(request)
            return response
        except RateLimitExceeded:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

    async def check_rate_limit(self, request: Request):
        """Check if request exceeds rate limit."""
        identifier = get_user_id(request)
        
        # Custom rate limiting logic
        window_key = f"rate_limit:{identifier}:{int(request.state.timestamp // settings.RATE_LIMIT_WINDOW)}"
        current_requests = redis_client.get(window_key)
        
        if current_requests is None:
            redis_client.setex(window_key, settings.RATE_LIMIT_WINDOW, 1)
        else:
            current_count = int(current_requests)
            if current_count >= settings.RATE_LIMIT_REQUESTS:
                raise RateLimitExceeded("Rate limit exceeded")
            redis_client.incr(window_key)
