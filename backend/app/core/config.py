from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --------------------------------------------------
    # Project
    # --------------------------------------------------

    PROJECT_NAME: str = "AutoDev AI"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # --------------------------------------------------
    # LLM Priority
    # --------------------------------------------------

    LLM_PRIORITY: str = "gemini,openai"

    # --------------------------------------------------
    # OpenAI
    # --------------------------------------------------

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # --------------------------------------------------
    # Gemini
    # --------------------------------------------------

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    DATABASE_URL: str = "sqlite:///./autodev.db"

    # --------------------------------------------------
    # Vector DB
    # --------------------------------------------------

    CHROMA_DB_PATH: str = "./chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()