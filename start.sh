#!/bin/sh
echo "Running migrations..."
python manage.py migrate
python manage.py runserver
echo "Starting server..."
python manage.py celery

