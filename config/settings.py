"""
Configuration setti    # LLM configuration
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "granite3.3:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text"for Legacy Code Migration Tool
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """Configuration class for the Legacy Code Migration Tool"""
    
    # Base configuration
    PROJECT_NAME: str = "Legacy Code Migration"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "static"
    VECTOR_DB_DIR: Path = BASE_DIR / "static" / "vector_db"
    
    # LLM configuration
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "granite3.3:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    
    # Database configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # API configuration
    API_BASE_URL: Optional[str] = None
    API_KEY: Optional[str] = None
    
    def __post_init__(self):
        """Initialize configuration from environment variables if available"""
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", self.LLM_PROVIDER)
        self.LLM_MODEL = os.getenv("LLM_MODEL", self.LLM_MODEL)
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", self.EMBEDDING_MODEL)
        self.API_BASE_URL = os.getenv("API_BASE_URL", self.API_BASE_URL)
        self.API_KEY = os.getenv("API_KEY", self.API_KEY)
        
        self.DATA_DIR.mkdir(exist_ok=True)
        self.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()

LLM_PROVIDER = settings.LLM_PROVIDER
LLM_MODEL = settings.LLM_MODEL
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
VECTOR_DB_DIR = settings.VECTOR_DB_DIR
