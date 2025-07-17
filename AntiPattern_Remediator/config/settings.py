"""
Configuration settings for Legacy Code Migration Tool
"""

import os
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
        
        self.DATA_DIR.mkdir(exist_ok=True)
        self.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class OllamaSettings(Settings):
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "granite3.3:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"


@dataclass
class IBMSettings(Settings):
    LLM_PROVIDER: str = "ibm"
    LLM_MODEL: str = "ibm/granite-3-3-8b-instruct"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest" # This is a placeholder, IBM does not have a specific embedding model

    # IBM Watson X configuration - these will be loaded from environment variables
    watsonx_api_key: Optional[str] = None
    project_id: Optional[str] = None
    url: Optional[str] = None
    
    # IBM LLM parameters
    parameters: dict = None
    
    def __post_init__(self):
        """Initialize IBM specific configuration from environment variables"""
        super().__post_init__()
        
        # Load sensitive information from environment variables
        self.watsonx_api_key = os.getenv("WATSONX_APIKEY") or os.getenv("IBM_WATSONX_API_KEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID") or os.getenv("IBM_PROJECT_ID")
        self.url = os.getenv("WATSONX_URL", self.url)

        if self.parameters is None:
            self.parameters = {
                "decoding_method": "sample",
                "max_new_tokens": 4000,
                "min_new_tokens": 1,
                "temperature": 0.5,
                "top_k": 50,
                "top_p": 1,
            }


@dataclass  
class VLLMSettings(Settings):
    pass


# Global settings instance
settings = None

# Provider selection logic
def get_settings(provider: str) -> Settings:
    """Get settings instance based on provider"""
    if provider == "ollama":
        settings_instance = OllamaSettings()
        print("✅ Using Ollama settings")
    elif provider == "ibm":
        settings_instance = IBMSettings()
        print("✅ Using IBM Watson X settings")
        print(f"📝 Model: {settings_instance.LLM_MODEL}")
    elif provider == "vllm":
        settings_instance = VLLMSettings()
        print("✅ Using vLLM settings")
    else:
        settings_instance = Settings()
        print("⚠️ Using default settings")
    
    return settings_instance


def initialize_settings(provider: str) -> Settings:
    """Initialize global settings with selected provider"""
    global settings
    settings = get_settings(provider)
    return settings


# Initialize with default provider
settings = get_settings("")