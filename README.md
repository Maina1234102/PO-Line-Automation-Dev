# PO Line Automation Dev

This project automates PO Line creation in Oracle via a FastAPI backend and React frontend. It uses Docker Compose to orchestrate the application and connects to HashiCorp Vault to dynamically retrieve sensitive API credentials.

## Running Locally

1. Create a `.env` file or export your Vault token: `export VAULT_TOKEN="..."`.
2. Start the application:
```bash
docker-compose up -d --build
```
3. Access the frontend at `http://localhost:5173` and the backend swagger docs at `http://localhost:8000/docs`.
