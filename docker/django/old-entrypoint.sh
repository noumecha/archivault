#!/bin/sh

# archivault/docker/django/entrypoint.sh
DB_HOST=${MYSQL_HOST:-db}
DB_PORT=${MYSQL_PORT:-3306}
ENV=${DJANGO_ENVIRONMENT}

echo "⏳ Attente de MySQL sur $DB_HOST:$DB_PORT..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "La base de données est prête !"

python manage.py migrate

if [ $ENV = "development" ]; then
  echo "Démarrage du serveur de développement Django rendez-vous sur http://localhost:8000/"
  exec "$@"
# python manage.py runserver 0.0.0.0:8000
else
  python manage.py collectstatic --noinput --clear
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
fi
