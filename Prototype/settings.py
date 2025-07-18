import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass

# Load .env from project root (one level above)
load_dotenv()

@dataclass
class Settings:
    PROJECT_NAME: str = "WatsonX Anti-Pattern Remediator"
    VERSION: str = "0.1.0"
    
    # WatsonX-specific
    WATSONX_URL: str = os.getenv("WATSONX_URL", "")
    WATSONX_APIKEY: str = os.getenv("WATSONX_APIKEY", "")
    WATSONX_PROJECT_ID: str = os.getenv("WATSONX_PROJECT_ID", "")
    WATSONX_MODEL_ID: str = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-3-8b-instruct")

     # Ollama-specific
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")  
    OLLAMA_MODEL_ID: str = os.getenv("OLLAMA_MODEL_ID", "granite3.3:8b")

    # LLM inference settings
    MAX_NEW_TOKENS: int = 500
    TEMPERATURE: float = 0.1
    DECODING_METHOD: str = "greedy"

# Global instance
settings = Settings()
