from typing import Dict, Type
from .base_provider import BaseLLMProvider
from .ollama_provider import OllamaProvider
from .ibm_provider import IBMProvider
from .vllm_provider import VLLMProvider

class LLMCreator:
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "ollama": OllamaProvider,
        "ibm": IBMProvider,
        "vllm": VLLMProvider,
    }
    
    @staticmethod
    def create_llm(provider: str, model_name: str, **kwargs):
        provider_lower = provider.lower()
        if provider_lower not in LLMCreator._providers:
            raise ValueError(f"Unsupported provider: {provider}")
        provider_instance = LLMCreator._providers[provider_lower]()
        return provider_instance.create_llm(model_name, **kwargs)
    
    @staticmethod
    def get_supported_providers() -> list:
        return list(LLMCreator._providers.keys())