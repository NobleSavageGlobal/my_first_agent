"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Agent Puller"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://agent_puller:agent_puller_secret@localhost:5432/agent_puller_db"
    
    # SEC EDGAR
    sec_api_key: str = ""
    max_results: int = 100
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Analysis Settings
    min_growth_ratio: float = 2.0
    max_growth_ratio: float = 3.5
    min_new_segment_pct: float = 15.0
    max_new_segment_pct: float = 25.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
