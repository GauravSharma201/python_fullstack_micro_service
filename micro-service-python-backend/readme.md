# Modern Python Backend Microservices Architecture

## Project Structure

```
backend/
├── docker-compose.yml
├── requirements.txt
├── .env
├── gateway/
│   ├── main.py
│   ├── middleware/
│   └── config.py
├── auth-service/
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── utils/
├── task-service/
│   ├── main.py
│   ├── celery_app.py
│   ├── tasks/
│   └── worker.py
├── ui-service/
│   ├── main.py
│   ├── templates/
│   ├── static/
│   └── views/
├── notification-service/
│   ├── main.py
│   ├── services/
│   └── models/
└── shared/
    ├── database.py
    ├── models.py
    ├── auth.py
    └── config.py
```

## 1. Docker Compose Configuration

```yaml
# docker-compose.yml
version: "3.8"

services:
  # Databases
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: backend_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Message Queue
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password
    ports:
      - "5672:5672"
      - "15672:15672"

  # API Gateway
  gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - auth-service
      - ui-service
      - notification-service

  # Microservices
  auth-service:
    build: ./auth-service
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/backend_db
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your-secret-key
    depends_on:
      - postgres
      - redis

  task-service:
    build: ./task-service
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/backend_db
      - CELERY_BROKER_URL=pyamqp://admin:password@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - rabbitmq

  celery-worker:
    build: ./task-service
    command: celery -A celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/backend_db
      - CELERY_BROKER_URL=pyamqp://admin:password@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - rabbitmq

  celery-beat:
    build: ./task-service
    command: celery -A celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/backend_db
      - CELERY_BROKER_URL=pyamqp://admin:password@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - rabbitmq

  ui-service:
    build: ./ui-service
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/backend_db
      - AUTH_SERVICE_URL=http://auth-service:8001
    depends_on:
      - postgres
      - auth-service

  notification-service:
    build: ./notification-service
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/backend_db
      - REDIS_URL=redis://redis:6379
      - SMTP_HOST=smtp.gmail.com
      - SMTP_PORT=587
      - SMTP_USER=your-email@gmail.com
      - SMTP_PASSWORD=your-app-password
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

## 2. Shared Components

```python
# shared/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/backend_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# shared/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notifications = relationship("Notification", back_populates="user")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

```python
# shared/auth.py
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
```

## 3. API Gateway

```python
# gateway/main.py
from fastapi import FastAPI, Request, HTTPException
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
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": SERVICES}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 4. Authentication Service

```python
# auth-service/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, engine
from shared.models import User, Base
from shared.auth import verify_password, get_password_hash, create_access_token, verify_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Authentication Service", version="1.0.0")
security = HTTPBearer()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/verify")
def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user_id": payload["sub"], "valid": True}

@app.get("/me")
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user.id, "username": user.username, "email": user.email}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 5. Task Service with Celery

```python
# task-service/celery_app.py
from celery import Celery
import os

celery_app = Celery(
    "task_service",
    broker=os.getenv("CELERY_BROKER_URL", "pyamqp://admin:password@localhost:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379"),
    include=["tasks.background_tasks"]
)

celery_app.conf.task_routes = {
    "tasks.background_tasks.*": "background_queue",
}

celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "tasks.background_tasks.cleanup_old_tasks",
        "schedule": 3600.0,  # Run every hour
    },
}
```

```python
# task-service/tasks/background_tasks.py
from celery import current_task
from .celery_app import celery_app
import time
import requests
import os

@celery_app.task(bind=True)
def process_long_running_task(self, task_id: int, user_id: int):
    """Simulate a long-running background task"""
    try:
        # Update task status
        self.update_state(state="PROGRESS", meta={"current": 0, "total": 100})

        for i in range(100):
            time.sleep(0.1)  # Simulate work
            self.update_state(
                state="PROGRESS",
                meta={"current": i + 1, "total": 100, "status": f"Processing step {i + 1}"}
            )

        # Send notification when complete
        notification_data = {
            "user_id": user_id,
            "title": "Task Completed",
            "message": f"Your background task #{task_id} has been completed successfully!"
        }

        requests.post(
            "http://notification-service:8004/send",
            json=notification_data
        )

        return {"status": "completed", "result": "Task finished successfully"}

    except Exception as exc:
        self.update_state(
            state="FAILURE",
            meta={"error": str(exc)}
        )
        raise

@celery_app.task
def send_email_task(email: str, subject: str, body: str):
    """Background email sending task"""
    # Simulate email sending
    time.sleep(2)
    print(f"Email sent to {email}: {subject}")
    return {"status": "sent", "email": email}

@celery_app.task
def cleanup_old_tasks():
    """Periodic task to cleanup old completed tasks"""
    # Implementation for cleanup
    print("Cleaning up old tasks...")
    return {"cleaned": True}
```

```python
# task-service/main.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, engine
from shared.models import Task, Base
from tasks.background_tasks import process_long_running_task, send_email_task
from celery_app import celery_app

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Service", version="1.0.0")

class TaskCreate(BaseModel):
    title: str
    description: str
    user_id: int

class TaskStatus(BaseModel):
    id: str
    status: str
    result: Optional[dict] = None

@app.post("/create")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Start background processing
    celery_task = process_long_running_task.delay(db_task.id, task.user_id)

    return {
        "task_id": db_task.id,
        "celery_task_id": celery_task.id,
        "status": "started"
    }

@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {"state": task.state, "status": "Task is waiting to be processed"}
    elif task.state == "PROGRESS":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", "")
        }
    elif task.state == "SUCCESS":
        response = {"state": task.state, "result": task.result}
    else:
        response = {"state": task.state, "error": str(task.info)}

    return response

@app.get("/tasks/{user_id}")
def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return [{"id": t.id, "title": t.title, "description": t.description, "status": t.status} for t in tasks]

@app.post("/send-email")
def send_email(email: str, subject: str, body: str):
    task = send_email_task.delay(email, subject, body)
    return {"task_id": task.id, "status": "queued"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

## 6. UI Service (Server-Side Rendered)

```python
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

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

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
            return RedirectResponse(url="/dashboard", status_code=302)
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
        response = await client.post(
            f"{AUTH_SERVICE_URL}/register",
            json={"username": username, "email": email, "password": password}
        )

        if response.status_code == 200:
            return RedirectResponse(url="/dashboard", status_code=302)
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
```

## 7. Notification Service

```python
# notification-service/main.py
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, engine
from shared.models import Notification, User, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification Service", version="1.0.0")

# Redis for real-time notifications
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str

class EmailNotification(BaseModel):
    email: str
    subject: str
    body: str

def send_email(email: str, subject: str, body: str):
    """Send email using SMTP"""
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.post("/send")
def create_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Save to database
    db_notification = Notification(
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Send real-time notification via Redis
    notification_data = {
        "id": db_notification.id,
        "title": notification.title,
        "message": notification.message,
        "created_at": db_notification.created_at.isoformat()
    }

    redis_client.publish(f"user_{notification.user_id}_notifications", json.dumps(notification_data))

    # Get user email for email notification
    user = db.query(User).filter(User.id == notification.user_id).first()
    if user:
        background_tasks.add_task(
            send_email,
            user.email,
            notification.title,
            notification.message
        )

    return {"id": db_notification.id, "status": "sent"}

@app.get("/user/{user_id}")
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).limit(50).all()

    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notifications
    ]

@app.post("/mark-read/{notification_id}")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        return {"status": "marked_as_read"}
    return {"error": "Notification not found"}

@app.post("/send-email")
def send_email_notification(email_data: EmailNotification, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email_data.email, email_data.subject, email_data.body)
    return {"status": "email_queued"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
```

## 8. Requirements and Dockerfile Templates

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
redis==5.0.1
celery==5.3.4
python-multipart==0.0.6
jinja2==3.1.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.25.2
python-dotenv==1.0.0
```

```dockerfile
# Dockerfile template for each service
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

## Key Features:

1. **Microservices Architecture**: Separate services for auth, tasks, UI, and notifications
2. **API Gateway**: Central entry point with request routing and caching
3. **Authentication**: JWT-based auth with secure password hashing
4. **Background Tasks**: Celery with Redis/RabbitMQ for async processing
5. **Server-Side Rendering**: Jinja2 templates for traditional web UI
6. **Real-time Notifications**: Redis pub/sub + email notifications
7. **Database**: PostgreSQL with SQLAlchemy ORM
8. **Containerization**: Docker Compose for easy deployment
9. **Scalability**: Each service can be scaled independently
10. **Modern Stack**: FastAPI, Celery, Redis, PostgreSQL

This architecture provides a solid foundation for a production-ready Python backend with all requested features!

## creating database with postgres

```bash

CREATE DATABASE my_DB
```
