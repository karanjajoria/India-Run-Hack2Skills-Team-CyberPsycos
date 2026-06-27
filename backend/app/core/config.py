from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    groq_api_key: str = ""
    qdrant_path: str = "./qdrant_storage"
    collection_name: str = "talentiq_candidates"
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k_retrieve: int = 50
    top_k_shortlist: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
