from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest@rabbitmq//")

celery_app = Celery("worker", broker=CELERY_BROKER_URL)

@celery_app.task
def add(x, y):
    return x + y
