"""
Main FastAPI application for OpenShift Cluster Navigator.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager
from src.api.routes import router as api_router
from src.services import segments_manager_sync_service
from src.config import config
from src.utils.logging_config import setup_logging
from src.middleware import LoggingMiddleware

# Setup logging - read from environment or default to INFO
import os
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(
    log_level=log_level,
    log_file="app.log",
    log_dir=Path("logs")
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Application starting up...")
    # Startup: Start Segments Manager sync service
    await segments_manager_sync_service.start()
    logger.info("Segments Manager sync service started")
    # Perform initial sync
    await segments_manager_sync_service.sync_data()
    logger.info("Initial data sync completed")
    yield
    # Shutdown: Stop Segments Manager sync service
    logger.info("Application shutting down...")
    segments_manager_sync_service.stop()
    logger.info("Segments Manager sync service stopped")

# Create FastAPI app
app = FastAPI(
    title="OpenShift Cluster Navigator",
    description="API for managing and navigating OpenShift clusters organized by site",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add logging middleware only in DEBUG mode
if log_level == "DEBUG":
    app.add_middleware(LoggingMiddleware)
    logger.info("Detailed request/response logging enabled (DEBUG mode)")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_title": config.app_title
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "service": "openshift-cluster-navigator"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "detail": "Internal server error",
        "path": str(request.url.path)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
