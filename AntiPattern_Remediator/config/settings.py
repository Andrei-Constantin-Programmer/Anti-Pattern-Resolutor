"""
Configuration settings for Legacy Code Migration Tool
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    # Base configuration
    PROJECT_NAME: str = "Legacy Code Migration"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "static"
    PROMPT_DIR: Path = DATA_DIR / "prompt"
    VECTOR_DB_DIR: Path = DATA_DIR / "vector_db"

    # LLM configuration (defaults)
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = ""
    EMBEDDING_MODEL: str = ""
    parameters: Optional[dict] = None

    # Database configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # API configuration
    API_BASE_URL: Optional[str] = None
    API_KEY: Optional[str] = None

    # IBM WatsonX-specific config
    watsonx_api_key: Optional[str] = None
    project_id: Optional[str] = None
    url: Optional[str] = None

    def __post_init__(self):
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", self.LLM_PROVIDER)
        self.LLM_MODEL = os.getenv("LLM_MODEL", self.LLM_MODEL)
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", self.EMBEDDING_MODEL)

        if self.LLM_PROVIDER == "ibm":
            self.watsonx_api_key = os.getenv("WATSONX_APIKEY") or os.getenv("IBM_WATSONX_API_KEY")
            self.project_id = os.getenv("WATSONX_PROJECT_ID") or os.getenv("IBM_PROJECT_ID")
            self.url = os.getenv("WATSONX_URL", self.url)

        self.DATA_DIR.mkdir(exist_ok=True)
        self.PROMPT_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = None


def load_provider_config(provider: str) -> dict:
    """Load provider-specific values from provider_settings.json"""
    project_root = Path(__file__).resolve().parent.parent
    settings_file = project_root / "provider_settings.json"

    with open(settings_file, "r") as f:
        all_settings = json.load(f)

    return all_settings.get(provider, {})


def initialize_settings(provider: str = "ollama") -> Settings:
    """Initialize and return the Settings instance based on the provider"""
    global settings
    provider_config = load_provider_config(provider)

    settings = Settings(
        LLM_PROVIDER=provider,
        LLM_MODEL=provider_config.get("LLM_MODEL", ""),
        EMBEDDING_MODEL=provider_config.get("EMBEDDING_MODEL", ""),
        parameters=provider_config.get("parameters")
    )
    print(f"Loaded settings for provider: {provider}")
    return settings


# Default initialization
settings = initialize_settings(os.getenv("LLM_PROVIDER", "ollama"))
