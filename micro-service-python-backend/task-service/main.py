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