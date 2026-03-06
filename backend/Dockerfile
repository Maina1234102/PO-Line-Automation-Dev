FROM python:3.12-slim

WORKDIR /app

# Install dependencies required for some python packages like psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
# The application expects to be run with the module path backend.app...
# Since we are copying it to /app/backend, we ensure the python path works
COPY . /app/backend

# We change workdir to /app/backend so the imports like backend.app... might need to be resolved
# Actually, if the code does `from backend.app...`, and we are in `/app/backend`,
# python will look for `backend/app`. So we should set WORKDIR to /app or copy the backend
# to /app/backend. Let's set WORKDIR mapping correctly.
WORKDIR /app/backend

# Setup entrypoint script
# We copied entrypoint.sh to /app/backend/entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 8000

# Healthcheck to ensure the API is running
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
CMD curl --fail http://localhost:8000/docs || exit 1

ENTRYPOINT ["./entrypoint.sh"]
