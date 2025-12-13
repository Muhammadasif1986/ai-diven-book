"""
Health check API routes for the RAG chatbot system.
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import time
import logging

from src.core.config import settings
from src.core.embeddings import EmbeddingService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health",
            summary="Health check endpoint",
            description="Check the health status of the RAG chatbot service")
async def health_check():
    """
    Health check endpoint to verify the service is running.

    Returns:
        Dictionary with health status and service information
    """
    start_time = time.time()

    try:
        # Check if core services are available
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": getattr(health_check, 'start_time', start_time) - start_time,
            "services": {
                "app": "available",
                "database": "pending",  # Would check actual DB connection in real implementation
                "vector_db": "pending",  # Would check actual vector DB connection
                "llm_service": "pending"  # Would check actual LLM service connection
            },
            "version": "1.0.0",
            "environment": settings.APP_ENV
        }

        # Check vector database connectivity
        try:
            # Attempt to create an embedding service instance
            embedding_service = EmbeddingService()
            # If instantiation succeeds, mark as available
            health_status["services"]["vector_db"] = "available"
        except Exception as e:
            logger.error(f"Vector DB health check failed: {e}")
            health_status["services"]["vector_db"] = "unavailable"
            health_status["status"] = "degraded"

        # Check LLM service connectivity
        try:
            # In a real implementation, we would make a test call to the LLM service
            # For now, we'll assume it's available if the API key is configured
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
                health_status["services"]["llm_service"] = "available"
            else:
                health_status["services"]["llm_service"] = "unconfigured"
                health_status["status"] = "degraded"
        except Exception as e:
            logger.error(f"LLM service health check failed: {e}")
            health_status["services"]["llm_service"] = "unavailable"
            health_status["status"] = "degraded"

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        health_status["response_time_ms"] = response_time_ms

        # Determine overall status based on service availability
        unavailable_services = [k for k, v in health_status["services"].items() if v == "unavailable"]
        unconfigured_services = [k for k, v in health_status["services"].items() if v == "unconfigured"]

        if unavailable_services:
            health_status["status"] = "unavailable"
        elif unconfigured_services:
            health_status["status"] = "degraded"

        health_status["checks"] = {
            "unavailable_services": unavailable_services,
            "unconfigured_services": unconfigured_services
        }

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unavailable",
                "error": "Health check failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/ready",
            summary="Readiness check endpoint",
            description="Check if the RAG chatbot service is ready to handle requests")
async def readiness_check():
    """
    Readiness check endpoint to verify the service is ready to handle requests.

    Returns:
        Dictionary with readiness status
    """
    try:
        # In a real implementation, this would check if all required services
        # are ready to handle requests (e.g., models loaded, connections established)

        readiness_status = {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "ready_at": getattr(readiness_check, 'ready_since', datetime.now().isoformat())
        }

        # Check that essential configurations are in place
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
            readiness_status["status"] = "not_ready"
            readiness_status["reason"] = "OpenAI API key not configured"

        return readiness_status

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/live",
            summary="Liveness check endpoint",
            description="Check if the RAG chatbot service process is alive")
async def liveness_check():
    """
    Liveness check endpoint to verify the service process is alive.

    Returns:
        Dictionary with liveness status
    """
    try:
        return {
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "process": "running"
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service is not alive"
        )