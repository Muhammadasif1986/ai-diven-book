"""
Ingestion service for the RAG chatbot system.
Handles the ingestion of book content into the system.
"""
from typing import Dict, Any, List
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.embeddings import EmbeddingService, ContentChunk
from src.models.content_models import BookMetadata, ContentEmbedding
from src.utils.text_processor import default_text_processor


class IngestionService:
    """Service for ingesting book content into the RAG system."""

    def __init__(self, embedding_service: EmbeddingService, db_session: AsyncSession):
        self.embedding_service = embedding_service
        self.db_session = db_session

    async def ingest_book_content(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingest book content into the system.

        Args:
            book_data: Dictionary containing book information
                      Expected keys: book_id, title, content, author (optional)

        Returns:
            Dictionary with ingestion results
        """
        book_id = book_data.get("book_id")
        title = book_data.get("title")
        content = book_data.get("content")
        author = book_data.get("author", "")
        chunk_size = book_data.get("chunk_size", 512)  # Default chunk size

        if not book_id or not title or not content:
            raise ValueError("book_id, title, and content are required")

        # Update book metadata in database
        book_metadata = await self._update_book_metadata(book_id, title, author, content)

        # Chunk the content
        text_chunks = default_text_processor.chunk_text(
            content,
            source_file=book_id,
            title=title
        )

        # Create content chunks for embedding
        content_chunks = []
        for i, chunk in enumerate(text_chunks):
            content_chunk = ContentChunk(
                content_id=f"{book_id}_chunk_{i}",
                book_id=book_id,
                title=title,
                section=f"chunk_{i}",
                chunk_index=i,
                original_text=chunk.text,
                source_file=book_id,
                created_at=datetime.now().isoformat()
            )
            content_chunks.append(content_chunk)

        # Upsert to vector database
        await self.embedding_service.upsert_content_chunks(content_chunks)

        # Update content embedding records in SQL database
        await self._store_content_embeddings(content_chunks, book_metadata.id)

        # Update book metadata with chunk count
        book_metadata.total_chunks = len(content_chunks)
        book_metadata.ingestion_status = "completed"
        book_metadata.ingestion_completed_at = datetime.now()

        await self.db_session.commit()

        return {
            "status": "success",
            "message": f"Book '{title}' content ingested successfully",
            "total_chunks": len(content_chunks),
            "processing_time_ms": 0  # Placeholder - in real implementation, measure actual time
        }

    async def _update_book_metadata(self, book_id: str, title: str, author: str, content: str) -> BookMetadata:
        """Update or create book metadata record."""
        # Check if book already exists
        result = await self.db_session.execute(
            select(BookMetadata).where(BookMetadata.id == book_id)
        )
        book_metadata = result.scalar_one_or_none()

        if book_metadata:
            # Update existing record
            book_metadata.title = title
            book_metadata.author = author
            book_metadata.ingestion_status = "in_progress"
            book_metadata.ingestion_started_at = datetime.now()
        else:
            # Create new record
            book_metadata = BookMetadata(
                id=book_id,
                title=title,
                author=author,
                ingestion_status="in_progress",
                ingestion_started_at=datetime.now(),
                word_count=len(content.split())
            )
            self.db_session.add(book_metadata)

        await self.db_session.flush()  # Ensure the record is flushed to get the ID
        return book_metadata

    async def _store_content_embeddings(self, content_chunks: List[ContentChunk], book_db_id: str):
        """Store content embedding records in the SQL database."""
        for chunk in content_chunks:
            # Check if content embedding already exists
            result = await self.db_session.execute(
                select(ContentEmbedding).where(ContentEmbedding.content_id == chunk.content_id)
            )
            existing_embedding = result.scalar_one_or_none()

            if existing_embedding:
                # Update existing record
                existing_embedding.chunk_text = chunk.original_text
                existing_embedding.chunk_title = chunk.title
                existing_embedding.chunk_section = chunk.section
                existing_embedding.chunk_index = chunk.chunk_index
                existing_embedding.source_file = chunk.source_file
                existing_embedding.embedding_status = "processed"
            else:
                # Create new record
                content_embedding = ContentEmbedding(
                    content_id=chunk.content_id,
                    book_id=book_db_id,
                    chunk_text=chunk.original_text,
                    chunk_title=chunk.title,
                    chunk_section=chunk.section,
                    chunk_index=chunk.chunk_index,
                    source_file=chunk.source_file,
                    embedding_status="processed"
                )
                self.db_session.add(content_embedding)

        await self.db_session.flush()