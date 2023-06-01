FROM python:3.11.3-slim-bullseye

# Set working directory
WORKDIR /drpproject

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Install APT dependencies
RUN apt update && apt install -y build-essential

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install PIP dependencies
COPY ./requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

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