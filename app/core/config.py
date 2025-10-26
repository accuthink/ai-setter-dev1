from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration loaded from environment variables.

    Create a local .env file (or export env vars) with the keys below.
    """

    # General
    ENV: str = "dev"
    API_PREFIX: str = "/api"

    # Telnyx
    TELNYX_API_KEY: str | None = None
    TELNYX_SIGNING_SECRET: str | None = None  # for webhook signature verification
    TELNYX_PUBLIC_KEY: str | None = None  # for webhook signature verification (if different)

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # or gpt-4o, gpt-4-turbo, etc.

    # AI Assistant Persona
    PERSONA_NAME: str = "default"  # Which persona to use (default, medical_clinic, salon_spa, etc.)
    BUSINESS_NAME: str = "Our Business"  # Business name for persona context

    # Security
    SECRET_KEY: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # singleton-style access
