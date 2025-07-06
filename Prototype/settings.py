import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass

# Load .env from project root (one level above)
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

@dataclass
class Settings:
    PROJECT_NAME: str = "WatsonX Anti-Pattern Remediator"
    VERSION: str = "0.1.0"
    
    # WatsonX-specific
    WATSONX_URL: str = os.getenv("WATSONX_URL", "")
    WATSONX_APIKEY: str = os.getenv("WATSONX_APIKEY", "")
    WATSONX_PROJECT_ID: str = os.getenv("WATSONX_PROJECT_ID", "")
    WATSONX_MODEL_ID: str = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-3-8b-instruct")

    # LLM inference settings
    MAX_NEW_TOKENS: int = 300
    TEMPERATURE: float = 0.5
    DECODING_METHOD: str = "greedy"

# Global instance
settings = Settings()
