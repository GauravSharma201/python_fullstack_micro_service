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