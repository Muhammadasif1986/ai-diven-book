"""
Unit tests for the ingestion service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.ingestion_service import IngestionService
from src.models.content_models import BookMetadata


@pytest.mark.asyncio
async def test_ingest_book_content():
    """Test ingesting book content into the system."""
    # Mock dependencies
    mock_embedding_service = AsyncMock()
    mock_db_session = AsyncMock()

    ingestion_service = IngestionService(
        embedding_service=mock_embedding_service,
        db_session=mock_db_session
    )

    # Sample book content
    book_content = {
        "book_id": "test-book-123",
        "title": "Test Book",
        "content": "This is a test book content with multiple sections.",
        "author": "Test Author"
    }

    # Mock the text processor
    with patch('src.services.ingestion_service.default_text_processor') as mock_processor:
        mock_chunks = [
            {"text": "This is the first chunk.", "start_idx": 0, "end_idx": 25, "chunk_id": "chunk-1"},
            {"text": "This is the second chunk.", "start_idx": 25, "end_idx": 50, "chunk_id": "chunk-2"}
        ]
        mock_processor.chunk_text.return_value = mock_chunks

        # Mock embedding generation
        mock_embedding_service.generate_embeddings.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        # Call the method
        result = await ingestion_service.ingest_book_content(book_content)

        # Assertions
        assert result["status"] == "success"
        assert result["total_chunks"] == 2
        mock_embedding_service.upsert_content_chunks.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_book_content_empty():
    """Test ingesting empty book content."""
    mock_embedding_service = AsyncMock()
    mock_db_session = AsyncMock()

    ingestion_service = IngestionService(
        embedding_service=mock_embedding_service,
        db_session=mock_db_session
    )

    # Sample empty book content
    book_content = {
        "book_id": "test-book-123",
        "title": "Test Book",
        "content": "",
        "author": "Test Author"
    }

    # Call the method
    result = await ingestion_service.ingest_book_content(book_content)

    # Assertions
    assert result["status"] == "success"
    assert result["total_chunks"] == 0


@pytest.mark.asyncio
async def test_ingest_book_content_invalid():
    """Test ingesting invalid book content."""
    mock_embedding_service = AsyncMock()
    mock_db_session = AsyncMock()

    ingestion_service = IngestionService(
        embedding_service=mock_embedding_service,
        db_session=mock_db_session
    )

    # Sample invalid book content
    book_content = {
        "book_id": "test-book-123",
        "title": "Test Book"
        # Missing content field
    }

    # Call the method and expect an error
    with pytest.raises(KeyError):
        await ingestion_service.ingest_book_content(book_content)