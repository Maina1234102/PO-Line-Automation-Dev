#!/bin/bash
set -e

echo "Starting backend entrypoint..."

# Set Python path so it can resolve 'backend.app...'
export PYTHONPATH=/app

# Initialize the database
echo "Initializing database..."
python init_db.py

# Execute the main application server
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
