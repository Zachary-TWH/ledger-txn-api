# Sets up the Celery app and its connection to RabbitMQ

from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")

celery_app = Celery("ledger", broker=RABBITMQ_URL)