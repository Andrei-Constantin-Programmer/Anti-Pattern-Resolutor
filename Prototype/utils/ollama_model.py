from ollama import Client as OllamaClient
from settings import settings


class OllamaModelClient:
    def __init__(self):
        self.client = OllamaClient(host=settings.OLLAMA_URL)
        self.model_id = settings.OLLAMA_MODEL_ID
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_NEW_TOKENS  # Ollama uses `num_predict`, not `max_new_tokens`

    def invoke(self, prompt: str) -> str:
        try:
            response = self.client.chat(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Ollama inference failed: {e}"


if __name__ == "__main__":
    client = OllamaModelClient()
    print(client.invoke("Explain the Liskov Substitution Principle in simple terms."))
