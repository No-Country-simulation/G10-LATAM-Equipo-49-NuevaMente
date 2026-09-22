import pytest

from app.providers.gemini_provider import GeminiProvider


@pytest.mark.integration
def test_gemini_is_available():

    provider = GeminiProvider()

    response = provider.generate(
        "Responde solamente: OK"
    )

    assert response
    assert "OK" in response.upper()