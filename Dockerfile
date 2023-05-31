FROM python:3.12-alpine

# Set working directory
WORKDIR /drp01

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy project
COPY . .

# Add and run as non-root user
RUN adduser -D myuser
USER myuser