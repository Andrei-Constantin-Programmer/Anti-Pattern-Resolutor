from typing import Any
from .base_provider import BaseLLMProvider
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from config.settings import settings

class VLLMProvider(BaseLLMProvider):
    
    def create_llm(self, model_name: str, **kwargs) -> Any:
        vLLM_model = ChatOpenAI(
            model=model_name,
            openai_api_base=settings.vLLM_URL,
            openai_api_key=settings.vLLM_API_KEY,
            # temperature=settings.parameters.get("temperature"),
            # max_tokens=settings.parameters.get("max_tokens"),
            # echo=settings.parameters.get("echo"),
            **kwargs
        )
        return vLLM_model
    
    def create_embedding(self, model_name: str, **kwargs) -> Any:
        vLLM_embeddings_model = OpenAIEmbeddings(
            model=model_name,
            openai_api_base=settings.vLLM_Embedding_URL,
            openai_api_key=settings.vLLM_API_KEY,
            **kwargs
        )

        return vLLM_embeddings_model

    
    def get_provider_name(self) -> str:
        return "vllm"
