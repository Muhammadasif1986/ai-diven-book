"""
Content-related database models for the RAG chatbot system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class BookMetadata(Base):
    """Model for storing book metadata."""
    __tablename__ = "book_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    author = Column(String(250))
    description = Column(Text)
    version = Column(String(20))
    total_chunks = Column(Integer, default=0)
    total_pages = Column(Integer)
    word_count = Column(Integer)
    ingestion_status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    ingestion_started_at = Column(DateTime)
    ingestion_completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ContentEmbedding(Base):
    """Model for storing content embedding records."""
    __tablename__ = "content_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, unique=True)  # Matches Qdrant payload content_id
    book_id = Column(UUID(as_uuid=True), ForeignKey("book_metadata.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)  # Original text chunk
    chunk_title = Column(String(500))
    chunk_section = Column(String(200))
    chunk_index = Column(Integer, nullable=False)  # Must be non-negative
    source_file = Column(String(500))
    embedding_status = Column(String(20), default='pending')  # pending, processed, failed
    vector_id = Column(String(255))  # Qdrant point ID
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())