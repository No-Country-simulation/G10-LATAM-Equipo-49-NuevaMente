from app.providers.interfaces import LLMProvider


class MockProvider(LLMProvider):

    def __init__(self, response: str = "MOCK_RESPONSE"):
        self.response = response

    def generate(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
    ) -> str:
        return self.response
