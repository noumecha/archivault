# config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

environment = os.environ.get("DJANGO_ENVIRONMENT", "development")

if environment == "production":
    settings_module = "config.production"
else:
    settings_module = "config.development"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_wsgi_application()
