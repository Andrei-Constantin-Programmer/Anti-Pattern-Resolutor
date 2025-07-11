from typing import Any
from .base_provider import BaseLLMProvider

class IBMProvider(BaseLLMProvider):
    
    def create_llm(self, model_name: str, **kwargs) -> Any:
        from langchain_ibm import WatsonxLLM
        from config.settings import settings
        
        watsonx_llm = WatsonxLLM(
            model_id=model_name,
            url=settings.url,
            project_id=settings.project_id,
            params=settings.parameters,
            **kwargs
        )
        return watsonx_llm
    
    def create_embedding(self, model_name: str, **kwargs) -> Any:
        from langchain_ibm import WatsonxEmbeddings
        from config.settings import settings
        # TODO Need someone to check if this is correct
        watsonx_embeddings = WatsonxEmbeddings(
            model_id=model_name,
            url=settings.url,
            project_id=settings.project_id,
            **kwargs
        )
        return watsonx_embeddings
    
    def get_provider_name(self) -> str:
        """Return the provider name"""
        return "ibm"
