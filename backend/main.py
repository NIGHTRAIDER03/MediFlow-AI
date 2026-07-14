import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import engine, init_db, async_session
from database.seed import seed_database
from auth.routes import router as auth_router
from api.routes import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    # Seed database
    logger.info("Seeding database...")
    async with async_session() as session:
        await seed_database(session)
    
    yield
    
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="MediFlow AI API",
    description="API for the AI-first Healthcare CRM",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to MediFlow AI API"}
