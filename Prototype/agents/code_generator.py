class CodeGenerator:
    def __init__(self, model: any):
        self.model = model

    def generate_refactored_code(self, code: str, strategy: str) -> str:
        print("Code Generator")

        prompt = (
            "You are a Java expert. Given the following Java code and suggested refactoring strategies, "
            "return the complete, refactored Java code. "
            "DO NOT include any explanations or markdown formatting. Just return the code as plain text.\n\n"
            f"Java Code:\n{code}\n\n"
            f"Refactoring Strategies:\n{strategy}\n\n"
            "Output:"
        )

        try:
            response = self.model.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            print("RAW MODEL RESPONSE:\n", content)
            return content.strip()

        except Exception as e:
            print(f"Error in generating code: {e}")
            return f"[ERROR] Code gen failed: {e}"
