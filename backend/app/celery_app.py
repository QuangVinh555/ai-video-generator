from celery import Celery

celery_app = Celery(
    "video_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    broker_connection_retry_on_startup=True
)
