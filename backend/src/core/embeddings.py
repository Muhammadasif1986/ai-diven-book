"""
Embedding utilities and Qdrant configuration for the RAG chatbot system.
"""
import asyncio
from typing import List, Optional
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http import models
from pydantic import BaseModel

from src.core.config import settings

# Try to import sentence transformers, fall back to basic implementation if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence_transformers not available, using basic embeddings")


class ContentChunk(BaseModel):
    """Model for content chunks to be stored in Qdrant."""
    content_id: str
    book_id: str
    title: str
    section: str
    page_number: Optional[int] = None
    chunk_index: int
    original_text: str
    source_file: str
    created_at: str
    metadata: Optional[dict] = None


class EmbeddingService:
    """Service for handling embeddings and Qdrant operations."""

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=10
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.vector_size = 384  # Size of all-MiniLM-L6-v2 embeddings
        else:
            # Use a simple approach when sentence_transformers is not available
            self.model = None
            self.vector_size = 1536  # Standard size for compatibility

    async def initialize_collection(self):
        """Initialize the Qdrant collection with proper configuration."""
        try:
            # Check if collection exists
            collections = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_collections
            )
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with vector configuration
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=models.VectorParams(
                            size=self.vector_size,  # Use the appropriate size
                            distance=models.Distance.COSINE
                        )
                    )
                )

                # Create payload index for book_id for efficient filtering
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="book_id",
                        field_schema=models.PayloadSchemaType.KEYWORD
                    )
                )

                print(f"Collection '{self.collection_name}' created successfully")
            else:
                print(f"Collection '{self.collection_name}' already exists")

        except Exception as e:
            print(f"Error initializing Qdrant collection: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.model is not None:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        else:
            # Return simple deterministic "embeddings" when sentence_transformers is not available
            import hashlib
            embeddings = []
            for text in texts:
                embedding = []
                # Create a deterministic vector based on the text content
                text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
                for i in range(self.vector_size):
                    # Generate pseudo-random values based on text and position
                    val = ((text_hash * (i + 1)) % 1000000) / 1000000.0
                    # Scale to be between -1 and 1
                    val = (val * 2) - 1
                    embedding.append(val)
                embeddings.append(embedding)
            return embeddings

    async def generate_and_store_embeddings(
        self,
        chunks: List[ContentChunk],
        collection_name: str = None
    ) -> List[str]:
        """
        Generate embeddings for content chunks and store them in Qdrant.

        Args:
            chunks: List of ContentChunk objects to generate embeddings for
            collection_name: Name of the collection to store embeddings in (uses default if not provided)

        Returns:
            List of IDs of the stored embeddings
        """
        if collection_name is None:
            collection_name = self.collection_name

        # Extract text content from chunks
        texts = [chunk.original_text for chunk in chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings(texts)

        # Create Qdrant points
        points = []
        ids = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid4())
            ids.append(point_id)

            point = models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content_id": chunk.content_id,
                    "book_id": chunk.book_id,
                    "title": chunk.title,
                    "section": chunk.section,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "original_text": chunk.original_text,
                    "source_file": chunk.source_file,
                    "created_at": chunk.created_at,
                    "metadata": chunk.metadata or {}
                }
            )
            points.append(point)

        # Store in Qdrant
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.upsert(
                collection_name=collection_name,
                points=points
            )
        )

        return ids

    async def search_similar_content(
        self,
        query_text: str,
        book_id: str,
        limit: int = 5,
        threshold: float = 0.3
    ) -> List[models.ScoredPoint]:
        """
        Search for similar content in the vector database.

        Args:
            query_text: The query text to search for
            book_id: The book ID to filter results by
            limit: Maximum number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of scored points matching the query
        """
        # Generate embedding for the query
        query_embedding = self.generate_embeddings([query_text])[0]

        # Search in Qdrant with filtering
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="book_id",
                            match=models.MatchValue(value=book_id)
                        )
                    ]
                ),
                limit=limit,
                score_threshold=threshold
            )
        )

        return results

    async def upsert_content_chunks(self, chunks: List[ContentChunk]):
        """Upsert content chunks to Qdrant collection."""
        points = []

        for chunk in chunks:
            # Generate embedding for the content
            embedding = self.generate_embeddings([chunk.original_text])[0]

            # Create Qdrant point
            point = models.PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "content_id": chunk.content_id,
                    "book_id": chunk.book_id,
                    "title": chunk.title,
                    "section": chunk.section,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "original_text": chunk.original_text,
                    "source_file": chunk.source_file,
                    "created_at": chunk.created_at,
                    "metadata": chunk.metadata or {}
                }
            )
            points.append(point)

        # Upsert points to Qdrant
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        )

    async def search_similar_chunks(
        self,
        query_text: str,
        book_id: str,
        limit: int = 5
    ) -> List[models.ScoredPoint]:
        """Search for similar content chunks in Qdrant."""
        query_embedding = self.generate_embeddings([query_text])[0]

        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="book_id",
                            match=models.MatchValue(value=book_id)
                        )
                    ]
                ),
                limit=limit
            )
        )

        return results

    async def search_selection_chunks(
        self,
        query_text: str,
        selected_text: str,
        book_id: str,
        limit: int = 5
    ) -> List[models.ScoredPoint]:
        """Search for similar content chunks based only on selected text."""
        query_embedding = self.generate_embeddings([query_text])[0]
        selected_embedding = self.generate_embeddings([selected_text])[0]

        # For selection-based search, we'll use the selected text as context
        # and search for similar content within the selected text context
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="book_id",
                            match=models.MatchValue(value=book_id)
                        ),
                        models.FieldCondition(
                            key="original_text",
                            match=models.MatchText(text=selected_text[:100])  # Use first 100 chars as filter
                        )
                    ]
                ),
                limit=limit
            )
        )

        return results