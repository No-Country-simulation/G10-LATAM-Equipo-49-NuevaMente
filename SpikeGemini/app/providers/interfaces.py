from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
    ) -> str:
        """
        Genera una respuesta a partir de un prompt.
        """
        raise NotImplementedError


class EmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """
        Genera un vector embedding para el texto recibido.
        """
        raise NotImplementedError
