"""
Strategist Agent - Generates actionable refactoring strategies based on antipattern analysis
"""

from typing import Any

class StrategistAgent:
    def __init__(self, model: Any):
        self.model = model  # WatsonXClient instance

    def suggest_refactorings(self, code: str, analysis: str) -> str:
        print("\nGenerating Refactoring Strategies...")

        prompt = (
            "You are a senior software architect. Based on the following Java code and its antipattern analysis, "
            "provide specific, actionable refactoring strategies to resolve the issues.\n\n"
            f"Code:\n{code}\n\n"
            f"Antipattern Analysis:\n{analysis}\n\n"
            "Please output a bulleted list of clear, professional recommendations."
            "Keep over all answer short please"
        )

        try:
            response = self.model.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            print(f"Error during strategy generation: {e}")
            return f"[ERROR] Strategy generation failed: {e}"
