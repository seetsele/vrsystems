from celery import Celery
import os

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

app = Celery("verity_runner", broker=REDIS_URL, backend=REDIS_URL)

# Example configuration; adapt to production
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_acks_late=True,
)
