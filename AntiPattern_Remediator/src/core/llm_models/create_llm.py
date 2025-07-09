class LLMCreator:
    @staticmethod
    def create_llm(provider: str, model_name: str, **kwargs):
        if provider.lower() == "ollama":
            return LLMCreator._create_ollama(model_name)
        elif provider.lower() == "ibm":
            return LLMCreator._create_ibm(model_name, **kwargs)
        elif provider.lower() == "vllm":
            return LLMCreator._create_vllm(model_name, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _create_ollama(model_name: str):
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model_name)
    
    @staticmethod
    def _create_ibm(model_name: str, **kwargs):
        from langchain_ibm import WatsonxLLM
        from AntiPattern_Remediator.config.settings import settings
        watsonx_llm = WatsonxLLM(
            model_id=settings.LLM_MODEL,
            url=settings.url,
            project_id=settings.project_id,
            params=settings.parameters,
        )
        return watsonx_llm
    
    @staticmethod
    def _create_vllm(model_name: str, **kwargs):
        try:
            pass
        except ImportError:
            raise ImportError("")