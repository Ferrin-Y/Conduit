from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CONDUIT_", env_file=".env")

    database_url: str = "sqlite+aiosqlite:///./conduit.db"
    chroma_persist_dir: str = "./chroma_data"
    chunk_size: int = 500
    chunk_overlap: int = 50


settings = Settings()
