from celery import current_task
from celery_app import celery_app

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