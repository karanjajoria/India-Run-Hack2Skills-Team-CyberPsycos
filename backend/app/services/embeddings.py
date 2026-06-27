from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings

_model: SentenceTransformer = None

# Dimension for all-MiniLM-L6-v2 (used as fallback constant)
EMBEDDING_DIM = 384


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_text(text: str) -> List[float]:
    """Embed a single text string."""
    model = get_model()
    vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return vec.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed multiple texts in batch."""
    model = get_model()
    vecs = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    )
    return vecs.tolist()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two unit vectors."""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np))


def get_embedding_dim() -> int:
    return get_model().get_sentence_embedding_dimension()
