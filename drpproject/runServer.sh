#!/bin/bash

# Run migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Collect static files
python3 manage.py collectstatic --noinput

# Start the development server
python3 manage.py runserver