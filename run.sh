#!/bin/sh
ENV=${DJANGO_ENVIRONMENT}

if [ $ENV = "development" ]; then
  echo "Démarrage du serveur de développement Django rendez-vous sur http://localhost:8000/"
  docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
else
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
fi
