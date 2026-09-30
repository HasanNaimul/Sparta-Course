from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    voyage_api_key: str

    anthropic_model: str
    voyage_embed_model: str

    relevance_floor: float = 0.30
    max_agent_iterations: int = 4
    financial_stale_days: int = 180
    chroma_path: str = "./chroma_store"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()