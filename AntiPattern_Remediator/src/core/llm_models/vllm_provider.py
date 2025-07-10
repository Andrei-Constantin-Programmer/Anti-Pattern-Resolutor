from typing import Any
from .base_provider import BaseLLMProvider

class VLLMProvider(BaseLLMProvider):
    
    def create_llm(self, model_name: str, **kwargs) -> Any:
        pass
    
    def create_embedding(self, model_name: str, **kwargs) -> Any:
        pass
    
    def get_provider_name(self) -> str:
        return "vllm"
