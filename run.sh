#!/bin/bash

# Wait for the database to be ready
echo "Waiting for DB to be ready..."
while ! nc -z db 5432; do
  sleep 0.2
done
echo "DB is ready."

# Run Alembic Migrations
alembic upgrade head

# Start the FastAPI application
cd app && exec uvicorn main:app --host 0.0.0.0 --port 8000

# debug hold open if we want to shell into the container to snoop around, comment in as needed
# exec /bin/sh -c "while true; do sleep 30; done"