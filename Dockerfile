##############################
# VENV STAGE
# Python base + virtual environment
##############################
FROM python:3.11.3-slim-bullseye AS venv-stage

# Set working directory
WORKDIR /drpproject

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

##############################
# DEPENDENCY STAGE
# VENV + dependencies
##############################
FROM venv-stage AS dependency-stage

# APT dependencies
RUN apt update && \
    # GCC-related
    apt install -y build-essential \
                   postgresql-client

COPY ./requirements.txt .
# Install PIP dependencies
RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    python3 -c "import nltk; nltk.download('averaged_perceptron_tagger')" && \
    # SpaCy EN language pack
    python3 -m spacy download en_core_web_sm

##############################
# PRODUCTION STAGE
# VENV + DEPENDENCY + our code
##############################
FROM venv-stage AS production-stage

ENTRYPOINT ["./entrypoint.sh"]

# Set environment variables
ARG DB_PASSWORD
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DOCKER_ENV 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Copy dependencies from dependency-stage
COPY --from=dependency-stage ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy project
COPY . .

RUN cd drpproject && \
    # Apply database migrations
    python3 manage.py makemigrations && \
    python3 manage.py migrate && \
    # Collect static files
    python3 manage.py collectstatic && \
    # Add and run as non-root user
    adduser --disabled-password --gecos "" myuser
USER myuser

# Run gunicorn
CMD if [ "${IN_HEROKU}" = "true" ]; then \
        cd drpproject && gunicorn drpproject.wsgi; \
    else \
        cd drpproject && gunicorn --bind 0.0.0.0:8000 drpproject.wsgi; \
    fi