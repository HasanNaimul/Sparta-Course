from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    voyage_api_key: str
    anthropic_model: str
    voyage_embed_model: str

    relevance_floor: float = 0.35
    rerank_floor: float = 2.0
    max_agent_iterations: int = 4
    financial_stale_days: int = 180
    chroma_path: str = "./chroma_store"

    azure_search_endpoint: str = ""
    azure_search_index: str = "credit-chunks-v1"
    semantic_config: str = "credit_semantic"
    exact_match_rule: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()