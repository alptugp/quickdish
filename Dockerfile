FROM python:3.8.2-alpine

# Set working directory
WORKDIR /drpproject

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Install dependencies
RUN apk add build-base
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN cd drpproject && python3 manage.py collectstatic --noinput

# Add and run as non-root user
RUN adduser -D myuser
USER myuser

# Run gunicorn
CMD gunicorn drpproject.wsgi:drpapp --bind 0.0.0.0:8000