#!/bin/bash

set -e

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
	python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
	python manage.py collectstatic --noinput
fi

if [ "${RUN_COMPRESS:-1}" = "1" ]; then
	python manage.py compress --force
fi

if [ "${ENABLE_CELERY:-1}" = "1" ]; then
	celery -A portotours worker -l INFO --beat --scheduler django &
fi

# Use runserver for development (when DEBUG=True), gunicorn for production
if [ "${DEBUG:-False}" = "True" ]; then
	exec python manage.py runserver 0.0.0.0:8000
else
	exec gunicorn --workers "${GUNICORN_WORKERS:-4}" --bind 0.0.0.0:8000 portotours.wsgi:application
fi

