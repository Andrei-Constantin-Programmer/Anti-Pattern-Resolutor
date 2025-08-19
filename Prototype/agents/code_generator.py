import re

class CodeGenerator:
    def __init__(self, model: any):
        self.model = model

    def generate_refactored_code(self, code: str, strategy: str) -> str:
        print("Code Generator")

        prompt = (
             "You are a Java expert. Given the following Java code and refactoring strategies, "
    "generate the fully refactored Java code.\n\n"

    "*** RESPONSE RULES ***\n"
    "ONLY return the updated Java code.\n"
    "DO NOT include:\n"
    "- Explanations\n"
    "- Comments\n"
    "- Markdown formatting (e.g., no ```java or ```)\n"
    "- Any introductory or descriptive text\n\n"

    "Preserve proper formatting, indentation, and line breaks so the code can be displayed and compiled directly.\n\n"

    f"Original Java Code:\n{code}\n\n"
    f"Refactoring Strategies:\n{strategy}\n\n"
    "Your response must begin directly with the Java code:"
        )

        try:
            response = self.model.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            print("RAW MODEL RESPONSE:\n", content)

            cleaned = re.sub(r"^```(?:java)?\n?", "", content.strip())
            cleaned = re.sub(r"\n?```$", "", cleaned)

            return cleaned.strip()
            # return content.strip()

        except Exception as e:
            print(f"Error in generating code: {e}")
            return f"[ERROR] Code gen failed: {e}"
