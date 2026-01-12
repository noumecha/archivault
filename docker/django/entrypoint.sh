#!/bin/sh

echo "Attente de la base de données..."
while ! nc -z db 3306; do
  sleep 1
done

echo "La base de données est prête !"

python manage.py migrate
python manage.py collectstatic --noinput --clear

exec gunicorn archivault.config.wsgi:application --bind 0.0.0.0:8000
