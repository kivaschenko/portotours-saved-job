#!/bin/bash

# Start Gunicorn server with HTTPS support
gunicorn --workers 4 --bind 0.0.0.0:8000 --certfile=/etc/ssl/certs/fullchain.pem --keyfile=/etc/ssl/private/privkey.pem portotours.wsgi:application &
# Wait for Django to start
sleep 10  # Adjust the sleep time as needed to ensure Django has started
# Start Celery worker alongside Django server
celery -A portotours worker -l INFO --beat --scheduler django
