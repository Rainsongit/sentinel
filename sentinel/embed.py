from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sentinel.config import EMBED_MODEL


@lru_cache(maxsize=1)
def model() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL)


def encode(texts: list[str]):
    return model().encode(texts, normalize_embeddings=True)
