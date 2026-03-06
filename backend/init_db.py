import logging
import sys
import os

# Ensure the backend directory is in the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import Base, engine
from backend.app.models.logging_models import User, ExcelUpload, LineItemLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Initializing database tables...")
    # This will create tables if they do not exist, but will NOT seed any database entries.
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables successfully created without seeded data.")

if __name__ == "__main__":
    init_db()
