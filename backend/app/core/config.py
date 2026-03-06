import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")

    if RUNNING_IN_DOCKER:
        try:
            vault_url = f"{VAULT_ADDR}/v1/PO-line-Integration/data/dev-keys"
            headers = {"X-Vault-Token": VAULT_TOKEN}
            response = requests.get(vault_url, headers=headers)
            response.raise_for_status()
            vault_data = response.json().get("data", {}).get("data", {})

            ORACLE_BASE_URL = vault_data.get("ORACLE_BASE_URL", os.getenv("ORACLE_BASE_URL"))
            DATABASE_URL = vault_data.get("DATABASE_URL", os.getenv("DATABASE_URL", "postgresql://postgres:hrms5t6YPg@localhost/poline_db"))
            if DATABASE_URL and "localhost" in DATABASE_URL:
                DATABASE_URL = DATABASE_URL.replace("localhost:5433", "database:5432").replace("localhost", "database")
        except Exception as e:
            print(f"Error loading secrets from Vault: {e}")
            ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
            DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:hrms5t6YPg@localhost/poline_db")
    else:
        ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:hrms5t6YPg@localhost/poline_db")
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    BACKEND_DIR = BASE_DIR

settings = Settings()
