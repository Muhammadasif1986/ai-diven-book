"""
Ingestion API routes for the RAG chatbot system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.database import get_async_session
from src.core.embeddings import EmbeddingService
from src.services.ingestion_service import IngestionService
from src.api.dependencies import check_rate_limit
from src.models.content_models import BookMetadata


router = APIRouter()


@router.post("/ingest",
             summary="Ingest book content into vector store",
             description="Process and store book content for RAG retrieval")
async def ingest_content(
    request: dict,
    rate_limit = Depends(check_rate_limit),
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Ingest book content into the system.

    Args:
        request: Dictionary containing book information
                Expected keys: book_id, title, content, author (optional)
        rate_limit: Dependency to check rate limits
        db_session: Database session

    Returns:
        Dictionary with ingestion results
    """
    try:
        # Validate required fields
        required_fields = ["book_id", "title", "content"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        # Initialize services
        embedding_service = EmbeddingService()
        ingestion_service = IngestionService(
            embedding_service=embedding_service,
            db_session=db_session
        )

        # Perform ingestion
        result = await ingestion_service.ingest_book_content(request)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.get("/ingest/status/{book_id}",
            summary="Get ingestion status for a book",
            description="Check the status of book content ingestion")
async def get_ingestion_status(
    book_id: str,
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Get the ingestion status for a specific book.

    Args:
        book_id: The ID of the book to check
        db_session: Database session

    Returns:
        Dictionary with ingestion status information
    """
    try:
        # Query the book metadata from the database
        result = await db_session.execute(
            select(BookMetadata).where(BookMetadata.id == book_id)
        )
        book_metadata = result.scalar_one_or_none()

        if not book_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )

        return {
            "book_id": book_metadata.id,
            "title": book_metadata.title,
            "status": book_metadata.ingestion_status,
            "total_chunks": book_metadata.total_chunks,
            "total_pages": book_metadata.total_pages,
            "word_count": book_metadata.word_count,
            "ingestion_started_at": book_metadata.ingestion_started_at,
            "ingestion_completed_at": book_metadata.ingestion_completed_at
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ingestion status: {str(e)}"
        )