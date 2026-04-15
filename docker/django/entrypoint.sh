#!/bin/sh

# archivault/docker/django/entrypoint.sh
DB_HOST=${MYSQL_HOST:-db}
DB_PORT=${MYSQL_PORT:-3306}

echo "⏳ Attente de MySQL sur $DB_HOST:$DB_PORT..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "✅ Base de données prête"

python manage.py migrate
python manage.py collectstatic --noinput --clear

exec "$@"
