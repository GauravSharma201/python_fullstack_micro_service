# gateway/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import redis
import json
import os

app = FastAPI(title="API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Service URLs
SERVICES = {
    "auth": "http://auth-service:8001",
    "tasks": "http://task-service:8002",
    "ui": "http://ui-service:8003",
    "notifications": "http://notification-service:8004"
}

async def forward_request(service_url: str, path: str, method: str, headers: dict, body: bytes = None):
    async with httpx.AsyncClient() as client:
        url = f"{service_url}{path}"
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            content=body,
            timeout=30.0
        )
        return response

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    body = await request.body()
    response = await forward_request(
        SERVICES["auth"],
        f"/{path}",
        request.method,
        dict(request.headers),
        body
    )
    return response.json()

@app.api_route("/tasks/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def tasks_proxy(path: str, request: Request):
    body = await request.body()
    response = await forward_request(
        SERVICES["tasks"],
        f"/{path}",
        request.method,
        dict(request.headers),
        body
    )
    return response.json()

@app.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def notifications_proxy(path: str, request: Request):
    body = await request.body()
    response = await forward_request(
        SERVICES["notifications"],
        f"/{path}",
        request.method,
        dict(request.headers),
        body
    )
    return response.json()

@app.api_route("/ui/{path:path}", methods=["GET", "POST"])
async def ui_proxy(path: str, request: Request):
    body = await request.body()
    response = await forward_request(
        SERVICES["ui"],
        f"/{path}",
        request.method,
        dict(request.headers),
        body
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type")
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": SERVICES}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)