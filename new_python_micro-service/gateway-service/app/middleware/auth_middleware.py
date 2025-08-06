from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, List
import redis
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

class AuthMiddleware:
    def __init__(self):
        self.bearer = HTTPBearer(auto_error=False)
        
    # Routes that don't require authentication
    EXCLUDE_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/metrics",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/token"
    ]

    async def __call__(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        # Skip authentication for excluded paths
        if any(path.startswith(excluded) for excluded in self.EXCLUDE_PATHS):
            response = await call_next(request)
            return response
        
        # Extract and validate token
        try:
            token = await self.extract_token(request)
            if token:
                user_info = self.validate_token(token)
                if user_info:
                    # Add user info to request state
                    request.state.user = user_info
                    request.state.token = token
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )
        
        response = await call_next(request)
        return response

    async def extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ")[1]
        return None

    def validate_token(self, token: str) -> Optional[dict]:
        """Validate JWT token and return user info."""
        try:
            # Check if token is blacklisted
            if redis_client.get(f"blacklist:{token}"):
                return None
                
            # Decode and validate token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Extract user information
            user_info = {
                "user_id": payload.get("user_id"),
                "username": payload.get("sub"),
                "email": payload.get("email"),
                "exp": payload.get("exp")
            }
            
            return user_info
        except JWTError:
            return None
