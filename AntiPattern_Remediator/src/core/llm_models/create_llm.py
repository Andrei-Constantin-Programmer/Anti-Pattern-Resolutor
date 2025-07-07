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
        try:
            pass
        except ImportError:
            raise ImportError("")
    
    @staticmethod
    def _create_vllm(model_name: str, **kwargs):
        try:
            pass
        except ImportError:
            raise ImportError("")