"""
Chat-related database models for the RAG chatbot system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class UserQuerySession(Base):
    """Model for storing user query sessions."""
    __tablename__ = "user_query_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token = Column(String(255))  # Anonymous session identifier
    user_id = Column(UUID(as_uuid=True))  # For authenticated users (optional)
    question = Column(Text, nullable=False)  # User's original question (10-2000 chars)
    context_type = Column(String(20), nullable=False)  # 'full_book', 'chapter', 'selection'
    selected_text = Column(Text)  # Text selected by user (if applicable), max 5000 chars
    retrieved_chunks = Column(JSONB)  # Retrieved context chunks with scores
    answer = Column(Text, nullable=False)  # AI-generated answer
    citations = Column(JSONB)  # Source citations for the answer
    response_time_ms = Column(Integer)  # Time taken to generate response (positive)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SelectionQueryRequest:
    """Request model for selection-based queries (not a DB model, used for validation)."""
    def __init__(self, question: str, selected_text: str, session_token: str):
        self.question = question
        self.selected_text = selected_text
        self.session_token = session_token


class SelectionQueryRequestModel:
    """Pydantic model for selection-based query requests for validation."""
    def __init__(self, question: str, selected_text: str, session_token: str):
        self.question = question
        self.selected_text = selected_text
        self.session_token = session_token

    @classmethod
    def validate(cls, data: dict):
        """Validate the selection query request data."""
        required_fields = ['question', 'selected_text', 'session_token']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate question length
        if len(data['question']) < 3:
            raise ValueError("Question must be at least 3 characters long")

        if len(data['question']) > 2000:
            raise ValueError("Question must be no more than 2000 characters long")

        # Validate selected text length
        if len(data['selected_text']) > 5000:  # Max length from requirements
            raise ValueError(f"Selected text too long. Maximum 5000 characters allowed, got {len(data['selected_text'])}")

        # Validate session token
        if len(data['session_token']) < 5:
            raise ValueError("Session token must be at least 5 characters long")

        return cls(
            question=data['question'],
            selected_text=data['selected_text'],
            session_token=data['session_token']
        )