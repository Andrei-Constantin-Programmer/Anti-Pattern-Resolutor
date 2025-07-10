from abc import ABC, abstractmethod
from typing import Any

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def create_llm(self, model_name: str, **kwargs) -> Any:
        """Create and return an LLM instance"""
        pass
    
    @abstractmethod
    def create_embedding(self, model_name: str, **kwargs) -> Any:
        """Create and return an embedding model instance"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of the provider"""
        pass
