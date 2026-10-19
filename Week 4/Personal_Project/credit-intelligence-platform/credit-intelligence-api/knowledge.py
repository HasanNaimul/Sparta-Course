"""Voyage embeddings used by Credit Intelligence retrieval."""

import voyageai

from config import settings

EMBED_MODEL = settings.voyage_embed_model
voyage = voyageai.Client(api_key=settings.voyage_api_key)


def embed_texts(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    """Embed texts and return vectors plus token usage."""
    if not texts:
        return [], 0

    result = voyage.embed(texts, model=EMBED_MODEL, input_type=input_type)
    return result.embeddings, result.total_tokens