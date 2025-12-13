"""
RAG (Retrieval-Augmented Generation) service for the chatbot system.
Handles the complete RAG pipeline: retrieval + generation.
"""
from typing import List, Dict, Any, Optional
import logging
import time
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from src.core.config import openai_client, settings
from src.services.retrieval_service import RetrievalService
from src.services.chat_service import ChatService
from src.models.chat_models import UserQuerySession
from src.utils.validators import validate_query_input


class RAGService:
    """Service for handling the complete RAG pipeline."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        db_session: AsyncSession
    ):
        self.retrieval_service = retrieval_service
        self.db_session = db_session
        self.chat_service = ChatService()
        self.logger = logging.getLogger(__name__)

    async def query_book(
        self,
        question: str,
        book_id: str,
        session_token: str,
        context_type: str = "full_book",
        selected_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a query against the book content using RAG.

        Args:
            question: The question to answer
            book_id: The ID of the book to query
            session_token: Session identifier for the user
            context_type: Type of context ("full_book" or "selection")
            selected_text: Text selected by user (for selection-based queries)

        Returns:
            Dictionary containing the answer, citations, and metadata
        """
        start_time = time.time()

        # Validate inputs
        is_valid, error_msg = validate_query_input(question, context_type, selected_text)
        if not is_valid:
            raise ValueError(error_msg)

        try:
            # Retrieve relevant context
            context_chunks = []
            citations = []

            try:
                if context_type == "selection" and selected_text:
                    context_chunks, citations = await self.retrieval_service.retrieve_context_with_citations(
                        query=question,
                        book_id=book_id,
                        context_type="selection",
                        selected_text=selected_text
                    )
                else:
                    context_chunks, citations = await self.retrieval_service.retrieve_context_with_citations(
                        query=question,
                        book_id=book_id,
                        context_type="full_book"
                    )
            except Exception as retrieval_error:
                self.logger.error(f"Retrieval failed: {retrieval_error}")
                # Continue with empty context - the chat service will handle this gracefully

            # Generate answer using OpenAI
            try:
                if context_chunks:
                    # Combine context chunks into a single context string
                    context_text = "\n\n".join([chunk["text"] for chunk in context_chunks])
                    answer = await self.chat_service.generate_answer(
                        question=question,
                        context=context_text,
                        citations=citations
                    )
                else:
                    # If no context found or retrieval failed, generate a response indicating this
                    answer = await self.chat_service.generate_answer_no_context(question)
            except Exception as llm_error:
                self.logger.error(f"LLM generation failed: {llm_error}")
                # Provide a fallback response
                answer = "I'm sorry, but I'm currently experiencing difficulties processing your request. Please try again later."

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Store the query session in the database
            try:
                await self._store_query_session(
                    question=question,
                    answer=answer,
                    session_token=session_token,
                    context_type=context_type,
                    selected_text=selected_text,
                    retrieved_chunks=context_chunks,
                    citations=citations,
                    response_time_ms=response_time_ms,
                    book_id=book_id
                )
            except Exception as storage_error:
                self.logger.error(f"Failed to store query session: {storage_error}")
                # Don't fail the entire request just because storage failed

            # Prepare the response
            result = {
                "answer": answer,
                "citations": citations,
                "response_time_ms": response_time_ms,
                "context_type": context_type,
                "retrieved_chunks": [
                    {
                        "content": chunk["text"],
                        "score": chunk["score"],
                        "source": chunk["source"]
                    }
                    for chunk in context_chunks
                ] if context_chunks else []
            }

            self.logger.info(f"Query processed successfully. Response time: {response_time_ms}ms")
            return result

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            # Provide graceful degradation by returning helpful error message
            error_answer = "I'm sorry, but I encountered an error while processing your request. " \
                          "Please try rephrasing your question or check back later. " \
                          "If the problem persists, our technical team has been notified."

            # Store the error in the database as well
            try:
                await self._store_query_session(
                    question=question,
                    answer=error_answer,
                    session_token=session_token,
                    context_type=context_type,
                    selected_text=selected_text,
                    retrieved_chunks=[],
                    citations=[],
                    response_time_ms=int((time.time() - start_time) * 1000),
                    book_id=book_id
                )
            except Exception as storage_error:
                self.logger.error(f"Failed to store error query session: {storage_error}")

            # Return a graceful error response instead of raising
            return {
                "answer": error_answer,
                "citations": [],
                "response_time_ms": int((time.time() - start_time) * 1000),
                "context_type": context_type,
                "retrieved_chunks": [],
                "error": "SERVICE_TEMPORARILY_UNAVAILABLE"
            }

    async def _store_query_session(
        self,
        question: str,
        answer: str,
        session_token: str,
        context_type: str,
        selected_text: Optional[str],
        retrieved_chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        response_time_ms: int,
        book_id: str
    ):
        """Store the query session in the database."""
        try:
            # Create a new UserQuerySession record
            query_session = UserQuerySession(
                session_token=session_token,
                question=question,
                context_type=context_type,
                selected_text=selected_text,
                retrieved_chunks=retrieved_chunks,
                answer=answer,
                citations=citations,
                response_time_ms=response_time_ms
            )

            # Add to session and commit
            self.db_session.add(query_session)
            await self.db_session.commit()
            await self.db_session.refresh(query_session)

            self.logger.info(f"Query session stored with ID: {query_session.id}")
        except Exception as e:
            self.logger.error(f"Error storing query session: {e}")
            # Don't raise the error as it shouldn't affect the user experience
            # The query was processed successfully even if we couldn't store the session

    async def validate_context_availability(
        self,
        book_id: str,
        query: str,
        context_type: str = "full_book",
        selected_text: Optional[str] = None
    ) -> bool:
        """
        Validate that sufficient context is available for the query.

        Args:
            book_id: The ID of the book to check
            query: The query to validate context for
            context_type: Type of context ("full_book" or "selection")
            selected_text: Selected text for selection-based queries

        Returns:
            True if sufficient context is available, False otherwise
        """
        try:
            if context_type == "selection" and selected_text:
                results = await self.retrieval_service.retrieve_from_selection(
                    query=query,
                    selected_text=selected_text,
                    book_id=book_id,
                    limit=1  # Just check if we can get at least one result
                )
            else:
                results = await self.retrieval_service.retrieve_from_book(
                    query=query,
                    book_id=book_id,
                    limit=1  # Just check if we can get at least one result
                )

            return len(results) > 0
        except Exception as e:
            self.logger.warning(f"Error validating context availability: {e}")
            return False

    async def get_query_statistics(self, session_token: str) -> Dict[str, Any]:
        """
        Get statistics for a user's query history.

        Args:
            session_token: The session token to get statistics for

        Returns:
            Dictionary with query statistics
        """
        # This would typically query the database for user query history
        # For now, returning placeholder data
        return {
            "total_queries": 0,
            "avg_response_time_ms": 0,
            "most_common_topics": [],
            "last_query_time": None
        }