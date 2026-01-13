import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
    ORACLE_USER = os.getenv("ORACLE_USER")
    ORACLE_PASS = os.getenv("ORACLE_PASS")
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    BACKEND_DIR = BASE_DIR

settings = Settings()
