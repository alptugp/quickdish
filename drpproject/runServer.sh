#!/bin/bash

# Run migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Start the development server
python3 manage.py runserver