from typing import Any
from .base_provider import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    
    def create_llm(self, model_name: str, **kwargs) -> Any:
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model_name, **kwargs)
    
    def create_embedding(self, model_name: str, **kwargs) -> Any:
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=model_name, **kwargs)
    
    def get_provider_name(self) -> str:
        return "ollama"
