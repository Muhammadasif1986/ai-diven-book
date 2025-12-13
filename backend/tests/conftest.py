"""
Pytest configuration and fixtures for the RAG chatbot system.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.core.database import Base
from src.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def test_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
async def async_test_db():
    """Create an in-memory async database for testing."""
    # Use SQLite in-memory database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=True,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = AsyncMock()

    # Mock the chat completions create method
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a mocked response from OpenAI."
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
async def mock_embedding_service():
    """Mock embedding service for testing."""
    mock_service = AsyncMock()
    mock_service.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]
    mock_service.search_similar_chunks.return_value = []
    mock_service.search_selection_chunks.return_value = []
    return mock_service


@pytest.fixture
def sample_book_content():
    """Sample book content for testing."""
    return """
    # Introduction to RAG Systems

    Retrieval-Augmented Generation (RAG) systems combine the power of large language models with the precision of information retrieval. This approach allows AI systems to ground their responses in specific, relevant documents rather than relying solely on their pre-trained knowledge.

    The basic architecture of a RAG system involves two main components: a retriever and a generator. The retriever is responsible for finding relevant documents or passages from a knowledge base, while the generator creates a response based on the retrieved information and the original query.

    ## Benefits of RAG Systems

    RAG systems offer several advantages over traditional language models:

    1. Accuracy: Responses are grounded in specific documents
    2. Freshness: Can incorporate new information not in the original training data
    3. Transparency: Users can see which documents informed the response
    4. Control: Organizations can curate their own knowledge bases
    """


@pytest.fixture
def sample_query_request():
    """Sample query request for testing."""
    return {
        "question": "What are the benefits of RAG systems?",
        "session_token": "test_session_123"
    }


@pytest.fixture
def sample_selection_query_request():
    """Sample selection query request for testing."""
    return {
        "question": "Explain the benefits mentioned in this text?",
        "selected_text": "RAG systems offer several advantages over traditional language models: 1. Accuracy: Responses are grounded in specific documents 2. Freshness: Can incorporate new information not in the original training data",
        "session_token": "test_session_123"
    }


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing."""
    mock_limiter = AsyncMock()
    mock_limiter.is_allowed.return_value = True
    return mock_limiter