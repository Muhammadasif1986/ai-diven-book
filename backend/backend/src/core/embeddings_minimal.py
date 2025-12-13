"""
Minimal embeddings module to allow backend to start without heavy dependencies.
"""
import asyncio
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
import uuid


class EmbeddingService:
    """Minimal embedding service that doesn't require heavy dependencies."""

    def __init__(self):
        # Initialize Qdrant client
        from src.core.config import settings
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=False  # Use REST API
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        # Use a simple dense vector configuration instead of dense vector with specific model
        self.vector_size = 1536  # Standard for many embedding models

    async def initialize_collection(self):
        """Initialize the Qdrant collection."""
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with simple dense vectors
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
            else:
                print(f"Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate simple embeddings using a basic approach.
        In a real implementation, this would use a proper embedding model.
        For now, we'll return simple vectors based on text length and content.
        """
        embeddings = []
        for text in texts:
            # Create a simple deterministic "embedding" based on text content
            # This is just for testing purposes - not a real embedding
            text_hash = hash(text) % (10 ** 8)  # Get a hash of the text
            embedding = []
            for i in range(self.vector_size):
                # Create a pseudo-random value based on text hash and position
                val = ((text_hash * (i + 1)) % 10000) / 10000.0
                # Scale to be between -1 and 1
                val = (val * 2) - 1
                embedding.append(val)
            embeddings.append(embedding)
        return embeddings

    async def store_embeddings(self, texts: List[str], metadata: List[dict] = None):
        """Store embeddings in Qdrant."""
        embeddings = await self.generate_embeddings(texts)

        points = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            point_id = str(uuid.uuid4())
            payload = {
                "text": text,
                "chunk_id": i
            }
            if metadata and i < len(metadata):
                payload.update(metadata[i])

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )

        # Upload points to Qdrant
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return [p.id for p in points]

    async def search_similar(self, query_text: str, top_k: int = 5) -> List[dict]:
        """Search for similar embeddings."""
        query_embedding = (await self.generate_embeddings([query_text]))[0]

        search_results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )

        results = []
        for result in search_results:
            results.append({
                "text": result.payload.get("text", ""),
                "score": result.score,
                "metadata": result.payload
            })

        return results