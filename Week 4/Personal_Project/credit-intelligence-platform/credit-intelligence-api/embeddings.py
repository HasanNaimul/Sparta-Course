import voyageai

from config import settings


client = voyageai.Client(api_key=settings.voyage_api_key)


def embed_texts(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    if not texts:
        return [], 0

    response = client.embed(texts, model=settings.voyage_embed_model, input_type=input_type)
    return response.embeddings, response.total_tokens