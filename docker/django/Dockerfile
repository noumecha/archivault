##################################
# 1️⃣ STAGE FRONTEND (Node)
##################################
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# copier uniquement les fichiers nécessaires
COPY src/package*.json ./
RUN npm install

# copier le reste du front
COPY src/ .

# build prod (génère assets/vendor)
RUN npm run build


##################################
# 2️⃣ STAGE BACKEND (Django)
##################################
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

# 🔥 copier les assets buildés par Node
COPY --from=frontend-builder /frontend/assets/vendor /app/src/assets/vendor

# script d'entrée
COPY docker/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
