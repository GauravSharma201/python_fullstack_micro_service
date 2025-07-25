# ui-service/main.py
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import os

app = FastAPI(title="UI Service", version="1.0.0")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/login",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            # In a real app, you'd set a secure cookie here
            return RedirectResponse(url="/ui/dashboard", status_code=302)
        else:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid credentials"}
            )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    async with httpx.AsyncClient() as client:
        print('inside ui-service , register call...')
        print('calling the route ==>',f"{AUTH_SERVICE_URL}/register")
        response = await client.post(
            f"{AUTH_SERVICE_URL}/register",
            json={"username": username, "email": email, "password": password}
        )

        if response.status_code == 200:
            return RedirectResponse(url="/ui/dashboard", status_code=302)
        else:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Registration failed"}
            )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # In a real app, you'd verify the user's token here
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)