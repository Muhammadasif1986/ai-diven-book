"""
Main FastAPI application for the RAG chatbot system.
"""
from contextlib import asynccontextmanager
import logging
import traceback
from datetime import datetime
from typing import Union

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.routes import ingest, query, health
from src.core.config import settings
from src.core.embeddings import EmbeddingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Initializing RAG Chatbot API...")

    # Initialize embedding service and Qdrant collection
    embedding_service = EmbeddingService()
    await embedding_service.initialize_collection()

    print("RAG Chatbot API initialized successfully!")
    yield
    # Shutdown
    print("Shutting down RAG Chatbot API...")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="API for the integrated RAG chatbot system in Docusaurus book",
    version="1.0.0",
    lifespan=lifespan
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup CORS for Docusaurus integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose custom headers if needed
    # expose_headers=["Access-Control-Allow-Origin"]
)

# Include API routes
app.include_router(ingest.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

# Custom error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": str(exc.detail),
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
            "status_code": 422,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "RAG Chatbot API is running!"}


# Health check endpoint (redundant since we have it in routes, but keeping for clarity)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "RAG Chatbot API is running!"}


