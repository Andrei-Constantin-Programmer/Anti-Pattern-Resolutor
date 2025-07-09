"""
Configuration settings for Legacy Code Migration Tool
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


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
        self.API_BASE_URL = os.getenv("API_BASE_URL", self.API_BASE_URL)
        self.API_KEY = os.getenv("API_KEY", self.API_KEY)
        
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

    watsonx_api_key: str = "DumEQrFTlzIBAS0NFBREVGqDpv0mdez8B861Z1zkB_7e"
    project_id: str = "0994b8ce-78cc-42ca-93fe-5112d16d0ec8"
    url: str = "https://us-south.ml.cloud.ibm.com"
    
    # IBM LLM parameters
    parameters: dict = None
    
    def __post_init__(self):
        """Initialize IBM specific configuration"""
        super().__post_init__()
        
        os.environ["WATSONX_APIKEY"] = self.watsonx_api_key

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


# Provider selection logic
def get_settings(provider: str = "ibm") -> Settings:
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
        print("⚠️  Using default settings")
    
    return settings_instance


# Initialize with selected provider
provider = "ibm"  # Change this to switch providers: "ollama", "ibm", "vllm"
settings = get_settings(provider)