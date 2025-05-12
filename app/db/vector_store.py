from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict, Any

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.collection_name = "context_embeddings"
        self.vector_size = 384  # MiniLM-L6-v2 embedding size

    def init_collection(self):
        """Initialize the vector collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )

    def store_context(self, context_id: str, context_text: str, metadata: Dict[str, Any]):
        """Store context with its embedding"""
        embedding = self.model.encode(context_text)
        point = PointStruct(
            id=context_id,
            vector=embedding.tolist(),
            payload={"text": context_text, **metadata}
        )
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def find_similar_contexts(self, query_text: str, limit: int = 5):
        """Find similar contexts based on semantic similarity"""
        query_vector = self.model.encode(query_text)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [
            {
                "id": hit.id,
                "text": hit.payload["text"],
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
                "score": hit.score
            }
            for hit in results
        ]

    def delete_context(self, context_id: str):
        """Delete a context by ID"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[context_id]
        ) 