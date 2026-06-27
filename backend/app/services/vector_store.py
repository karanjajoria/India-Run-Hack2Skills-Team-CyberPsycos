from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from typing import List, Dict, Any, Optional
from app.core.config import settings

_client: Optional[QdrantClient] = None

# Fixed dimension for all-MiniLM-L6-v2 — avoids calling get_model() before it's ready
EMBEDDING_DIM = 384


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(path=settings.qdrant_path)
    return _client


def ensure_collection(collection_name: str = None):
    """Create collection if it doesn't exist."""
    name = collection_name or settings.collection_name
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if name not in existing:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def upsert_candidates(
    points: List[Dict[str, Any]],
    collection_name: str = None,
):
    """
    Upsert candidate vectors into Qdrant.
    Each point: {"id": str, "vector": List[float], "payload": dict}
    """
    name = collection_name or settings.collection_name
    client = get_client()
    ensure_collection(name)

    qdrant_points = [
        PointStruct(
            id=idx,
            vector=p["vector"],
            payload={**p["payload"], "_str_id": p["id"]},
        )
        for idx, p in enumerate(points)
    ]
    client.upsert(collection_name=name, points=qdrant_points)


def search_candidates(
    query_vector: List[float],
    top_k: int = 50,
    collection_name: str = None,
) -> List[Dict[str, Any]]:
    """Search for top-k candidates by vector similarity."""
    name = collection_name or settings.collection_name
    client = get_client()

    results = client.query_points(
        collection_name=name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return [
        {
            "id": r.payload.get("_str_id", str(r.id)),
            "score": r.score,
            "payload": r.payload,
        }
        for r in results.points
    ]


def clear_collection(collection_name: str = None):
    """Drop and recreate collection (for fresh session)."""
    name = collection_name or settings.collection_name
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if name in existing:
        client.delete_collection(name)
    # Recreate with fixed dim — no model needed
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )
