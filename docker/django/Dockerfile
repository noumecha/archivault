FROM python:3.11-slim

# variables d'env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    netcat-openbsd \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# dossier de travail
WORKDIR /app

# installer les dépendances python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# copier le code de l'application
COPY . .

# script d'entrée
COPY docker/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
