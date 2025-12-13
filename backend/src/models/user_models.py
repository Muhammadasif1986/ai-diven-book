"""
User-related database models for the RAG chatbot system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class UserSession(Base):
    """Model for storing user sessions."""
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token = Column(String(255), nullable=False, unique=True)  # Anonymous session identifier
    is_authenticated = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True))  # For authenticated users
    created_at = Column(DateTime, server_default=func.now())
    last_activity_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)  # Must be in the future


class APIMetric(Base):
    """Model for storing API usage metrics."""
    __tablename__ = "api_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token = Column(String(255))  # Anonymous session identifier
    endpoint = Column(String(100), nullable=False)  # '/query', '/query/selection', '/ingest', '/health'
    request_data = Column(Text)  # Request payload (anonymized)
    response_time_ms = Column(Integer)  # Response time in milliseconds (positive)
    status_code = Column(Integer)  # HTTP status code
    rate_limited = Column(Boolean, default=False)  # Whether request was rate limited
    created_at = Column(DateTime, server_default=func.now())