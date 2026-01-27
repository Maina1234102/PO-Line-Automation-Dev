from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.app.core.config import settings
from backend.app.services.mappings import mapping_service
from backend.app.api.endpoints import router as api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    from backend.app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    # Load mappings on startup
    logger.info("Loading mappings...")
    mapping_service.load_mappings()

    # Seed User
    from backend.app.models.logging_models import User
    from backend.app.core.database import SessionLocal
    db = SessionLocal()
    try:
        user_email = "maina@inspiraenterprise.com"
        user_password = "Welcome@123"
        
        existing_user = db.query(User).filter(User.email == user_email).first()
        if not existing_user:
            logger.info(f"Seeding user: {user_email}")
            new_user = User(email=user_email, password=user_password)
            db.add(new_user)
            db.commit()
        else:
            # Ensure password is correct even if user exists (to match request)
            if existing_user.password != user_password:
                logger.info(f"Updating password for user: {user_email}")
                existing_user.password = user_password
                db.commit()
    finally:
        db.close()

    yield
    # Clean up resources if needed
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    logger.error(f"Request Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router)
