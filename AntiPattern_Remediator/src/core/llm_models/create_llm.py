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
        import os
        # from getpass import getpass
        # watsonx_api_key = os.environ.get("WATSONX_APIKEY")
        # if not watsonx_api_key:
        #     watsonx_api_key = getpass("Watson X API Key: ")
        #     os.environ["WATSONX_APIKEY"] = watsonx_api_key
        watsonx_api_key = "your_watsonx_api_key_here"  # Replace with your actual API key
        project_id = "0994b8ce-78cc-42ca-93fe-5112d16d0ec8"
        os.environ["WATSONX_APIKEY"] = watsonx_api_key
        parameters = {
            "decoding_method": "sample",
            "max_new_tokens": 100,
            "min_new_tokens": 1,
            "temperature": 0.5,
            "top_k": 50,
            "top_p": 1,
        }
        watsonx_llm = WatsonxLLM(
            model_id="ibm/granite-3-3-8b-instruct",
            url="https://us-south.ml.cloud.ibm.com",
            project_id=project_id,
            params=parameters,
        )
        return watsonx_llm
    
    @staticmethod
    def _create_vllm(model_name: str, **kwargs):
        try:
            pass
        except ImportError:
            raise ImportError("")