from fastapi import Depends, HTTPException, status, Cookie
from fastapi.responses import RedirectResponse
from typing import Optional
import httpx

AUTH_SERVICE_URL = "http://auth-service:8001"

def require_auth_token(redirection_url: str = "/ui/login"):
    async def dependency(access_token: Optional[str] = Cookie(None)):
        if not access_token:
            # Redirect because no token found
            return RedirectResponse(url=redirection_url, status_code=status.HTTP_302_FOUND)
        token = access_token.removeprefix("Bearer ").strip()

        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(f"{AUTH_SERVICE_URL}/verify", headers=headers, timeout=5.0)
                if response.status_code == 200:
                    # Token valid, return token or user info as needed
                    return token
            except Exception:
                pass

        # Token invalid or verification failed
        return RedirectResponse(url=redirection_url, status_code=status.HTTP_302_FOUND)

    return dependency
