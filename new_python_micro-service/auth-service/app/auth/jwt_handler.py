from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import settings
from app.schemas.token import TokenData
import redis

# Redis client for token blacklisting
redis_client = redis.from_url(settings.REDIS_URL)

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        # Check if token is blacklisted
        if redis_client.get(f"blacklist:{token}"):
            return None
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            return None
            
        token_data = TokenData(username=username, email=email, user_id=user_id)
        return token_data
    except JWTError:
        return None

def verify_refresh_token(token: str) -> Optional[TokenData]:
    """Verify refresh token."""
    try:
        if redis_client.get(f"blacklist:{token}"):
            return None
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            return None
            
        token_data = TokenData(username=username, email=email, user_id=user_id)
        return token_data
    except JWTError:
        return None

def blacklist_token(token: str, expire_time: Optional[int] = None):
    """Add token to blacklist."""
    if expire_time is None:
        expire_time = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    redis_client.setex(f"blacklist:{token}", expire_time, "true")
