# config/celery.py
import os
import django
from celery import Celery
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
environment = os.environ.get("DJANGO_ENVIRONMENT", "development")

if environment == "production":
    settings_module = "config.production"
else:
    load_dotenv(BASE_DIR / '.env.local', override=True)
    settings_module = "config.development"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

django.setup()

app = Celery('archivault')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
