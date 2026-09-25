from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.exceptions import LLMProviderError


class GeminiEmbeddingProvider:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMProviderError("GEMINI_API_KEY no configurada")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4))
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.models.embed_content(model=self.model, contents=texts)
        return [e.values for e in response.embeddings]

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4))
    def embed_query(self, text: str) -> list[float]:
        response = self.client.models.embed_content(model=self.model, contents=text)
        return response.embeddings[0].values
