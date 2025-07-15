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
            "You are a senior software architect. Based on the following Java code and its anti-pattern analysis, "
    "generate specific, actionable refactoring strategies to resolve the identified issues.\n\n"

    "*** RESPONSE FORMATTING ***\n"
    "You MUST format your response as a single JSON object. Do not include any text outside the JSON structure. "
    "The JSON object must have two top-level keys: 'status' and 'refactorings'.\n\n"

    "1. If anti-patterns were found in the analysis:\n"
    "- Set the 'status' to 'REFACTORING_SUGGESTED'.\n"
    "- Populate the 'refactorings' list with objects, each having the following keys:\n"
    "  'issueName' (from the analysis),\n"
    "  'suggestion' (brief action to take),\n"
    "  'justification' (why it's important).\n"
    "Example with suggestions:\n"
    "{\n"
    '  "status": "REFACTORING_SUGGESTED",\n'
    '  "refactorings": [\n'
    '    {\n'
    '      "issueName": "God Class",\n'
    '      "suggestion": "Split the class into smaller, responsibility-focused classes.",\n'
    '      "justification": "Improves maintainability and adheres to the Single Responsibility Principle."\n'
    '    }\n'
    '  ]\n'
    "}\n\n"

    "2. If the analysis had no significant issues:\n"
    "- Set the 'status' to 'NO_REFACTORING_NEEDED'.\n"
    "- The 'refactorings' list must be empty.\n"
    "Example with no suggestions:\n"
    "{\n"
    '  "status": "NO_REFACTORING_NEEDED",\n'
    '  "refactorings": []\n'
    "}\n\n"

    f"Here is the Java code:\n```java\n{code}\n```\n\n"
    f"Antipattern Analysis:\n{analysis}\n\n"
    "Respond only with the JSON output:"

        )

        try:
            response = self.model.invoke(prompt)
            # return response.content if hasattr(response, "content") else str(response)
            result = getattr(response, "content", response)
            # print(result) #debugging
            return result
        except Exception as e:
            print(f"Error during strategy generation: {e}")
            return f"[ERROR] Strategy generation failed: {e}"
