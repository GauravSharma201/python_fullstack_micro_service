# ui-service/main.py
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import os
from dependencies import require_auth_token

app = FastAPI(title="UI Service", version="1.0.0")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

environment = os.getenv('ENV')
# AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
AUTH_SERVICE_URL = "http://localhost:8001" if environment=='dev' else  "http://auth-service:8001"

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
            token = data.get("access_token")
            redirect = RedirectResponse(url="/ui/dashboard",status_code=302)
            if(token):
                redirect.set_cookie("access_token",f"Bearer {token}",httponly=True,max_age=3600,samesite="lax")
            return redirect
            
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
            data = response.json()
            token = data.get("access_token")
            redirect = RedirectResponse('/ui/dashboard',status_code=302)
            if(token):
                redirect.set_cookies("access_token",f"Bearer {token}",httponly=True,max_age=3600,samesite="lax")
            return redirect
        else:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Registration failed"}
            )
        

guardDashboard=require_auth_token()
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request,token=Depends(guardDashboard)):
    if(isinstance(token,RedirectResponse)):
        return token
    response = templates.TemplateResponse("dashboard.html", {"request": request})
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/logout",response_class=RedirectResponse)
async def logout():
    response = RedirectResponse(url="/ui/login",status_code=302)
    response.delete_cookie("access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)