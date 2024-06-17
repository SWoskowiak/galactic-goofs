FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    curl \
    netcat-openbsd \
    && curl -sSL https://install.python-poetry.org | python - \
    && apt-get remove -y curl \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /galactic-goofs-webserver

# Copy and install Python dependencies
COPY ./pyproject.toml ./poetry.lock /galactic-goofs-webserver/
RUN /opt/poetry/bin/poetry install --no-dev --no-interaction --no-ansi && rm -rf "/opt/poetry/cache"

# Copy application files
COPY ./app /galactic-goofs-webserver/app/
COPY ./templates /galactic-goofs-webserver/templates/
COPY ./alembic /galactic-goofs-webserver/alembic/
COPY ./alembic.ini /galactic-goofs-webserver/alembic.ini
COPY ./run.sh /galactic-goofs-webserver/run.sh

# Make the entrypoint script executable
RUN chmod +x /galactic-goofs-webserver/run.sh

# Set the entrypoint
ENTRYPOINT ["/galactic-goofs-webserver/run.sh"]

# Expose the port the app runs on
EXPOSE 8000