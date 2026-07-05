from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "AutoDev AI"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # AI
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # Database
    DATABASE_URL: str = "sqlite:///./autodev.db"

    # Vector Database
    CHROMA_DB_PATH: str = "./chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()