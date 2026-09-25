from src.core.config import settings
from src.embeddings.provider_gemini import GeminiEmbeddingProvider
from src.embeddings.provider_mock import MockEmbeddingProvider


def get_embedding_provider():
    if settings.EMBEDDING_PROVIDER == "gemini":
        return GeminiEmbeddingProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_EMBEDDING_MODEL,
        )
    return MockEmbeddingProvider()
