from .settings import *
from dotenv import load_dotenv

# Charger .env.local pour le dev
load_dotenv(BASE_DIR / '.env.local', override=True)

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'archivault'),
        'USER': os.environ.get('MYSQL_USER', 'archivault_user'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'StrongPassword123'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

DATABASES_ROUTERS = ['config.router']
