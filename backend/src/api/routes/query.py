"""
Query API routes for the RAG chatbot system.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import time

from src.core.database import get_async_session
from src.core.embeddings import EmbeddingService
from src.services.rag_service import RAGService
from src.services.retrieval_service import RetrievalService
from src.api.dependencies import check_rate_limit
from src.utils.validators import validate_query_input, validate_session_token


router = APIRouter()


@router.post("/query",
             summary="Query the RAG system with whole-book context",
             description="Ask questions about the entire book content",
             responses={
                 200: {"description": "Query processed successfully"},
                 400: {"description": "Invalid input parameters"},
                 429: {"description": "Rate limit exceeded"},
                 500: {"description": "Internal server error"}
             })
async def query_whole_book(
    request: Request,
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Query the RAG system with whole-book context.

    Args:
        request: FastAPI request object containing query data
        rate_limit: Dependency to check rate limits
        db_session: Database session

    Returns:
        Dictionary with the answer, citations, and metadata
    """
    start_time = time.time()

    try:
        # Parse the request body
        body = await request.json()

        # Validate request structure
        if "question" not in body or "session_token" not in body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: 'question' and 'session_token'"
            )

        question = body["question"]
        session_token = body["session_token"]
        book_id = body.get("book_id", "default-book")  # Default to a default book if not provided
        max_results = body.get("max_results", 5)

        # Validate inputs
        is_valid, error_msg = validate_query_input(question, "full_book")
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        is_valid, error_msg = validate_session_token(session_token)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Initialize services
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService(
            embedding_service=embedding_service,
            db_session=db_session
        )
        rag_service = RAGService(
            retrieval_service=retrieval_service,
            db_session=db_session
        )

        # Process the query
        result = await rag_service.query_book(
            question=question,
            book_id=book_id,
            session_token=session_token,
            context_type="full_book"
        )

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        result["response_time_ms"] = response_time_ms

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@router.post("/query/selection",
             summary="Query the RAG system with selected text context only",
             description="Ask questions constrained to only the user-selected text",
             responses={
                 200: {"description": "Query processed successfully"},
                 400: {"description": "Invalid input parameters"},
                 413: {"description": "Selected text too long"},
                 429: {"description": "Rate limit exceeded"},
                 500: {"description": "Internal server error"}
             })
async def query_selection(
    request: Request,
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Query the RAG system with selected text context only.

    Args:
        request: FastAPI request object containing query data
        rate_limit: Dependency to check rate limits
        db_session: Database session

    Returns:
        Dictionary with the answer, citations, and metadata
    """
    start_time = time.time()

    try:
        # Parse the request body
        body = await request.json()

        # Validate request structure
        required_fields = ["question", "selected_text", "session_token"]
        for field in required_fields:
            if field not in body:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        question = body["question"]
        selected_text = body["selected_text"]
        session_token = body["session_token"]
        book_id = body.get("book_id", "default-book")  # Default to a default book if not provided

        # Validate inputs
        is_valid, error_msg = validate_query_input(question, "selection", selected_text)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if "too long" in error_msg else status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        is_valid, error_msg = validate_session_token(session_token)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Initialize services
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService(
            embedding_service=embedding_service,
            db_session=db_session
        )
        rag_service = RAGService(
            retrieval_service=retrieval_service,
            db_session=db_session
        )

        # Process the query with selection context
        result = await rag_service.query_book(
            question=question,
            book_id=book_id,
            session_token=session_token,
            context_type="selection",
            selected_text=selected_text
        )

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        result["response_time_ms"] = response_time_ms

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Selection-based query processing failed: {str(e)}"
        )


@router.get("/query/history",
            summary="Get query history for a session",
            description="Retrieve the history of queries for a specific session")
async def get_query_history(
    session_token: str,
    limit: int = 10,
    offset: int = 0,
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Get query history for a specific session.

    Args:
        session_token: The session token to retrieve history for
        limit: Maximum number of results to return
        offset: Offset for pagination
        db_session: Database session

    Returns:
        List of query sessions for the given session token
    """
    try:
        # Validate session token
        is_valid, error_msg = validate_session_token(session_token)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # This would normally query the database for query history
        # For now, returning a placeholder response
        # In a real implementation, this would query the UserQuerySession table

        # Placeholder implementation
        return {
            "session_token": session_token,
            "limit": limit,
            "offset": offset,
            "total_queries": 0,
            "queries": []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve query history: {str(e)}"
        )