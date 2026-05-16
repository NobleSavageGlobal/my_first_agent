"""
Agent Puller - Main Application Entry Point

SEC Edgar Analysis Application for identifying narrative shift opportunities
in utility companies.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import get_settings
from .database import engine, Base
from .routers import companies_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name}...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    ## Agent Puller - SEC Edgar Narrative Shift Analyzer
    
    This application analyzes SEC EDGAR filings to identify utility companies
    where a growing new segment (e.g., renewable energy) is outpacing legacy
    segments (e.g., transmission/distribution).
    
    ### Features:
    - **Company Screening**: Analyze utilities for narrative shift opportunities
    - **Segment Analysis**: Detailed breakdown of revenue by business segment
    - **Growth Metrics**: Track growth ratios between legacy and growth segments
    - **Favorites**: Save companies for later review
    
    ### Analysis Criteria:
    - Growth segment grows 2-3x faster than legacy segment
    - Growth segment represents 15-25% of total revenue
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with better messages."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )


# Include routers
app.include_router(companies_router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "SEC Edgar Narrative Shift Analyzer",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "timestamp": logging.Formatter().formatTime(
            logging.LogRecord("", 0, "", 0, "", (), None)
        )
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
