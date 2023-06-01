FROM python:3.11.3-slim-bullseye

# Set working directory
WORKDIR /drpproject

# Set up virtual environment
RUN python3 -m venv /opt/venv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Install dependencies
RUN python3 -m pip install --upgrade pip
RUN apt install gcc libxml2-dev libxslt-dev
COPY ./requirements.txt .
RUN . /opt/venv/bin/activate && pip3 install -r requirements.txt

# Download SpaCy EN language pack
RUN python3 -m spacy download en

# Copy project
COPY . .

# Collect static files
RUN cd drpproject && python3 manage.py collectstatic

# Add and run as non-root user
RUN adduser -D myuser
USER myuser

# Run gunicorn
CMD cd drpproject && gunicorn drpproject.wsgi