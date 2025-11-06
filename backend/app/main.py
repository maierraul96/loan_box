from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import applications, pipelines, runs, catalog


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


# Create FastAPI app
app = FastAPI(
    title="Loan Orchestrator API",
    description="API for managing loan applications and processing pipelines",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router)
app.include_router(pipelines.router)
app.include_router(runs.router)
app.include_router(catalog.router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Loan Orchestrator API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
