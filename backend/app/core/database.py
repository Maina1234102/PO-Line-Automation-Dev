from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

# Use settings.DATABASE_URL if available, otherwise fallback (or fail)
# For now, we'll assume settings has it or we default to a standard local url
SQLALCHEMY_DATABASE_URL = getattr(settings, "DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
