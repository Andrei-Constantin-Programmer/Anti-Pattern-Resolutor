"""
Configuration settings for Legacy Code Migration Tool
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Settings:
    # Base configuration
    PROJECT_NAME: str = "AntiPattern Remediator"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "static"
    VECTOR_DB_DIR: Path = BASE_DIR / "static" / "vector_db"
    
    # LLM configuration
    LLM_PROVIDER: str = ""
    LLM_MODEL: str = ""
    EMBEDDING_MODEL: str = ""
    
    # Database configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # API configuration
    API_BASE_URL: Optional[str] = None
    API_KEY: Optional[str] = None
    
    # IBM specific configuration
    watsonx_api_key: Optional[str] = None
    project_id: Optional[str] = None
    url: Optional[str] = None
    parameters: Optional[Dict] = None

    def __post_init__(self):
        #Initialize configuration from environment variables if available
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", self.LLM_PROVIDER)
        self.LLM_MODEL = os.getenv("LLM_MODEL", self.LLM_MODEL)
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", self.EMBEDDING_MODEL)
        
        # Initialize IBM specific settings if provider is IBM
        if self.LLM_PROVIDER == "ibm":
            self.watsonx_api_key = os.getenv("WATSONX_APIKEY") or os.getenv("IBM_WATSONX_API_KEY")
            self.project_id = os.getenv("WATSONX_PROJECT_ID") or os.getenv("IBM_PROJECT_ID")
            self.url = os.getenv("WATSONX_URL", self.url)
        
        self.DATA_DIR.mkdir(exist_ok=True)
        self.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)


# Provider settings mapping
_PROVIDER_SETTINGS: Dict = {}

def load_provider_settings():
    #Load provider settings from JSON file
    global _PROVIDER_SETTINGS
    settings_path = Path(__file__).parent.parent / "provider_settings.json"
    with open(settings_path) as f:
        _PROVIDER_SETTINGS = json.load(f)

def get_settings(provider: str = "") -> Settings:
    #Get settings instance based on provider
    if not _PROVIDER_SETTINGS:
        load_provider_settings()
    
    settings_instance = Settings()
    provider_config = _PROVIDER_SETTINGS.get(provider, {})
    
    for key, value in provider_config.items():
        setattr(settings_instance, key.upper(), value)
    
    print(f"Using {provider or 'default'} settings")
    if provider == "ibm":
        print(f"Model: {settings_instance.LLM_MODEL}")
    
    return settings_instance

# Global settings instance
settings = None

def initialize_settings(provider: str) -> Settings:
    #Initialize global settings with selected provider
    global settings
    settings = get_settings(provider)
    return settings

# Initialize with default provider
settings = get_settings("")