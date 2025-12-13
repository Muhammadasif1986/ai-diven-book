"""
Integration tests for the query endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.core.embeddings import ContentChunk
from src.models.content_models import BookMetadata


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
async def test_query_endpoint_success(client, mock_embedding_service, sample_query_request):
    """Test successful query to the /query endpoint."""
    # Mock the embedding service
    mock_result = MagicMock()
    mock_result.payload = {
        "content_id": "test-content-1",
        "book_id": "test-book-1",
        "title": "Test Title",
        "section": "1.1",
        "page_number": 10,
        "chunk_index": 0,
        "original_text": "RAG systems combine retrieval and generation for better responses.",
        "source_file": "test.md",
        "created_at": "2023-01-01T00:00:00",
        "metadata": {}
    }
    mock_result.score = 0.85

    with patch('src.api.main.embedding_service', mock_embedding_service):
        mock_embedding_service.search_similar_chunks.return_value = [mock_result]

        # Mock the OpenAI client response
        with patch('src.core.config.openai_client') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "RAG systems improve response accuracy by retrieving relevant information."
            mock_openai.chat.completions.create.return_value = mock_response

            response = client.post("/api/v1/query", json=sample_query_request)

            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "citations" in data
            assert "response_time_ms" in data
            assert data["context_type"] == "full_book"


@pytest.mark.asyncio
async def test_query_endpoint_empty_question(client):
    """Test query endpoint with empty question."""
    empty_request = {
        "question": "",
        "session_token": "test_session_123"
    }

    response = client.post("/api/v1/query", json=empty_request)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_query_endpoint_missing_fields(client):
    """Test query endpoint with missing required fields."""
    incomplete_request = {
        "session_token": "test_session_123"
        # Missing question
    }

    response = client.post("/api/v1/query", json=incomplete_request)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_query_selection_endpoint_success(client, sample_selection_query_request):
    """Test successful query to the /query/selection endpoint."""
    # Mock the embedding service
    mock_embedding_service = AsyncMock()
    mock_result = MagicMock()
    mock_result.payload = {
        "content_id": "test-content-1",
        "book_id": "test-book-1",
        "title": "Test Title",
        "section": "1.1",
        "page_number": 10,
        "chunk_index": 0,
        "original_text": "RAG systems offer advantages like accuracy and freshness.",
        "source_file": "test.md",
        "created_at": "2023-01-01T00:00:00",
        "metadata": {}
    }
    mock_result.score = 0.92

    with patch('src.api.main.embedding_service', mock_embedding_service):
        mock_embedding_service.search_selection_chunks.return_value = [mock_result]

        # Mock the OpenAI client response
        with patch('src.core.config.openai_client') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "The advantages of RAG systems include accuracy and freshness."
            mock_openai.chat.completions.create.return_value = mock_response

            response = client.post("/api/v1/query/selection", json=sample_selection_query_request)

            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "citations" in data
            assert data["context_type"] == "selection"


@pytest.mark.asyncio
async def test_query_selection_endpoint_too_long_selection(client):
    """Test query selection endpoint with overly long selection."""
    long_selection_request = {
        "question": "Explain this concept?",
        "selected_text": "A" * 6000,  # Exceeds 5000 character limit
        "session_token": "test_session_123"
    }

    response = client.post("/api/v1/query/selection", json=long_selection_request)
    assert response.status_code == 413  # Payload too large


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test the health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "services" in data


@pytest.mark.asyncio
async def test_ingest_endpoint(client):
    """Test the ingest endpoint."""
    ingest_data = {
        "book_id": "test-book-123",
        "title": "Test Book",
        "content": "This is test content for ingestion.",
        "author": "Test Author"
    }

    # Mock the embedding service
    mock_embedding_service = AsyncMock()

    with patch('src.api.main.embedding_service', mock_embedding_service):
        response = client.post("/api/v1/ingest", json=ingest_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "total_chunks" in data