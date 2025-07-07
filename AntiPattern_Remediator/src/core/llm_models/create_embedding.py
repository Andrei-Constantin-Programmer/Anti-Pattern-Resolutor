class EmbeddingCreator:
    @staticmethod
    def create_embedding(provider: str, model_name: str):
        if provider == "ibm":
            return EmbeddingCreator._create_ibm(model_name)
        elif provider == "ollama":
            return EmbeddingCreator._create_ollama(model_name)
        elif provider == "vllm":
            return EmbeddingCreator._create_vllm(model_name)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def _create_ibm(model_name: str):
        pass

    @staticmethod
    def _create_ollama(model_name: str):
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=model_name)

    @staticmethod
    def _create_vllm(model_name: str):
        pass