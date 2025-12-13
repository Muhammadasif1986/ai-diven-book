"""
RAG retrieval service for the chatbot system.
Handles retrieval of relevant content from the vector database.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.http import models

from src.core.embeddings import EmbeddingService
from src.utils.text_processor import default_text_processor


class RetrievalService:
    """Service for retrieving relevant content chunks for RAG."""

    def __init__(self, embedding_service: EmbeddingService, db_session: AsyncSession):
        self.embedding_service = embedding_service
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    async def retrieve_from_book(
        self,
        query: str,
        book_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant content chunks from the entire book.

        Args:
            query: The query to search for
            book_id: The ID of the book to search in
            limit: Maximum number of results to return

        Returns:
            List of relevant content chunks with metadata
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if len(query.strip()) < 3:
            raise ValueError("Query must be at least 3 characters long")

        try:
            # Search in the vector database
            results = await self.embedding_service.search_similar_chunks(
                query_text=query,
                book_id=book_id,
                limit=limit
            )

            # Format results
            formatted_results = []
            for result in results:
                payload = result.payload
                formatted_result = {
                    "text": payload.get("original_text", ""),
                    "score": result.score,
                    "source": {
                        "content_id": payload.get("content_id"),
                        "title": payload.get("title", ""),
                        "section": payload.get("section", ""),
                        "page_number": payload.get("page_number"),
                        "chunk_index": payload.get("chunk_index"),
                        "source_file": payload.get("source_file", ""),
                        "created_at": payload.get("created_at", "")
                    },
                    "metadata": payload.get("metadata", {})
                }
                formatted_results.append(formatted_result)

            self.logger.info(f"Retrieved {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Error retrieving from book: {e}")
            raise

    async def retrieve_from_selection(
        self,
        query: str,
        selected_text: str,
        book_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant content chunks based only on the selected text.

        Args:
            query: The query to search for
            selected_text: The text selected by the user
            book_id: The ID of the book to search in
            limit: Maximum number of results to return

        Returns:
            List of relevant content chunks with metadata
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not selected_text or not selected_text.strip():
            raise ValueError("Selected text cannot be empty")

        # Validate selection length
        is_valid, error_msg = default_text_processor.validate_selection_text(selected_text)
        if not is_valid:
            raise ValueError(error_msg)

        try:
            # Search in the vector database based on the selected text
            results = await self.embedding_service.search_selection_chunks(
                query_text=query,
                selected_text=selected_text,
                book_id=book_id,
                limit=limit
            )

            # Format results
            formatted_results = []
            for result in results:
                payload = result.payload
                formatted_result = {
                    "text": payload.get("original_text", ""),
                    "score": result.score,
                    "source": {
                        "content_id": payload.get("content_id"),
                        "title": payload.get("title", ""),
                        "section": payload.get("section", ""),
                        "page_number": payload.get("page_number"),
                        "chunk_index": payload.get("chunk_index"),
                        "source_file": payload.get("source_file", ""),
                        "created_at": payload.get("created_at", "")
                    },
                    "metadata": payload.get("metadata", {})
                }
                formatted_results.append(formatted_result)

            self.logger.info(f"Retrieved {len(formatted_results)} results for selection-based query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Error retrieving from selection: {e}")
            raise

    async def retrieve_context_with_citations(
        self,
        query: str,
        book_id: str,
        context_type: str = "full_book",
        selected_text: Optional[str] = None,
        limit: int = 5
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Retrieve context and generate citations.

        Args:
            query: The query to search for
            book_id: The ID of the book to search in
            context_type: Type of context ("full_book" or "selection")
            selected_text: Selected text for selection-based queries
            limit: Maximum number of results to return

        Returns:
            Tuple of (context_chunks, citations)
        """
        if context_type == "selection" and selected_text:
            results = await self.retrieve_from_selection(query, selected_text, book_id, limit)
        else:
            results = await self.retrieve_from_book(query, book_id, limit)

        # Generate citations from results
        citations = []
        for result in results:
            citation = {
                "title": result["source"]["title"],
                "section": result["source"]["section"],
                "page_number": result["source"]["page_number"],
                "relevance_score": result["score"],
                "text_preview": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
            }
            citations.append(citation)

        return results, citations

    async def validate_retrieval_input(self, query: str, book_id: str, selected_text: Optional[str] = None) -> bool:
        """
        Validate input for retrieval operations.

        Args:
            query: The query to validate
            book_id: The book ID to validate
            selected_text: Selected text to validate (if applicable)

        Returns:
            True if input is valid, False otherwise
        """
        if not query or len(query.strip()) < 3:
            return False

        if not book_id or len(book_id.strip()) == 0:
            return False

        if selected_text is not None:
            is_valid, _ = default_text_processor.validate_selection_text(selected_text)
            return is_valid

        return True