"""
Unit tests for the RAG retrieval service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_retrieve_from_selection():
    """Test retrieving relevant chunks from selected text only."""
    # Mock dependencies
    mock_embedding_service = AsyncMock()
    mock_db_session = AsyncMock()

    retrieval_service = RetrievalService(
        embedding_service=mock_embedding_service,
        db_session=mock_db_session
    )

    # Mock the search results
    mock_result = MagicMock()
    mock_result.payload = {
        "content_id": "test-content-1",
        "book_id": "test-book-1",
        "title": "Test Title",
        "section": "1.1",
        "page_number": 10,
        "chunk_index": 0,
        "original_text": "This is a relevant text chunk from selection.",
        "source_file": "test.md",
        "created_at": "2023-01-01T00:00:00",
        "metadata": {}
    }
    mock_result.score = 0.92

    mock_embedding_service.search_selection_chunks.return_value = [mock_result]

    # Call the method
    query = "Explain this concept?"
    selected_text = "This is the selected text that contains important information."
    book_id = "test-book-1"
    results = await retrieval_service.retrieve_from_selection(query, selected_text, book_id)

    # Assertions
    assert len(results) == 1
    assert "relevant text chunk from selection" in results[0]["text"]
    assert results[0]["score"] == 0.92
    assert results[0]["source"]["title"] == "Test Title"
    mock_embedding_service.search_selection_chunks.assert_called_once()


@pytest.mark.asyncio
async def test_retrieve_from_selection_empty():
    """Test retrieving with empty selected text."""
    mock_embedding_service = AsyncMock()
    mock_db_session = AsyncMock()

    retrieval_service = RetrievalService(
        embedding_service=mock_embedding_service,
        db_session=mock_db_session
    )

    # Call the method with empty selected text
    query = "Explain this concept?"
    selected_text = ""
    book_id = "test-book-1"

    # Should raise ValueError
    with pytest.raises(ValueError, match="Selected text cannot be empty"):
        await retrieval_service.retrieve_from_selection(query, selected_text, book_id)


@pytest.mark.asyncio
async def test_retrieve_from_selection_too_long():
    """Test retrieving with overly long selected text."""
    mock_embedding_service = AsyncMock()
    mock_db_session = AsyncMock()

    retrieval_service = RetrievalService(
        embedding_service=mock_embedding_service,
        db_session=mock_db_session
    )

    # Call the method with overly long selected text
    query = "Explain this concept?"
    selected_text = "A" * 6000  # Exceeds 5000 character limit
    book_id = "test-book-1"

    # Should raise ValueError
    with pytest.raises(ValueError, match="Selected text too long"):
        await retrieval_service.retrieve_from_selection(query, selected_text, book_id)