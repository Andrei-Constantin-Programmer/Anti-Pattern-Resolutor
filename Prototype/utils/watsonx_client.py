from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from settings import settings


class WatsonXClient:
    def __init__(self):
        self.model = ModelInference(
            model_id=settings.WATSONX_MODEL_ID,
            credentials={
                "url": settings.WATSONX_URL,
                "apikey": settings.WATSONX_APIKEY
            },
            project_id=settings.WATSONX_PROJECT_ID,
        )

        self.params = {
            GenParams.MAX_NEW_TOKENS: settings.MAX_NEW_TOKENS,
            GenParams.TEMPERATURE: settings.TEMPERATURE,
            GenParams.DECODING_METHOD: settings.DECODING_METHOD,
        }

    def invoke(self, prompt: str) -> str:
        try:
            response = self.model.generate(prompt=prompt, params=self.params)
            return response["results"][0]["generated_text"]
        except Exception as e:
            return f"❌ WatsonX inference failed: {e}"


if __name__ == "__main__":
    client = WatsonXClient()
    print(client.invoke("Explain the Liskov Substitution Principle in simple terms."))
