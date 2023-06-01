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

# Install APT dependencies
RUN apt update && apt install -y build-essential

# Install PIP dependencies
COPY ./requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Download SpaCy EN language pack
RUN python3 -m spacy download en_core_web_sm

##############################
# PRODUCTION STAGE
# VENV + DEPENDENCY + our code
##############################
FROM venv-stage AS production-stage

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Copy dependencies from dependency-stage
COPY --from=dependency-stage ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy project
COPY . .

# Collect static files
RUN cd drpproject && python3 manage.py collectstatic

# Add and run as non-root user
RUN adduser --disabled-password --gecos "" myuser
USER myuser

# Run gunicorn
CMD cd drpproject && gunicorn drpproject.wsgi