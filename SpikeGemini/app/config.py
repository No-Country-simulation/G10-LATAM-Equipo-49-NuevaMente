import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    EMBEDDING_PROVIDER: str = os.getenv(
        "EMBEDDING_PROVIDER",
        "gemini",
    )

    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    GEMINI_GENERATION_MODEL: str = os.getenv(
        "GEMINI_GENERATION_MODEL",
        "gemini-3.6-flash",
    )

    GEMINI_EMBEDDING_MODEL: str | None = os.getenv(
        "GEMINI_EMBEDDING_MODEL"
    )

    GEMINI_TIMEOUT_SECONDS: int = int(
        os.getenv("GEMINI_TIMEOUT_SECONDS", "30")
    )

    FIDELITY_THRESHOLD: float = float(
        os.getenv("FIDELITY_THRESHOLD", "0.9")
    )

    MAX_FILE_SIZE_MB: int = int(
        os.getenv("MAX_FILE_SIZE_MB", "10")
    )


settings = Settings()
