class AntipatternScanner:
    """
    Agent to analyze Java code and detect antipatterns.
    """

    def __init__(self, model):
        self.model = model  # WatsonXClient instance

    def analyze(self, code: str) -> str:
        print("Analyzing Java code for antipatterns...")

        prompt = (
          "You are an expert and pragmatic software developer. "
            "Analyze the provided Java code for significant software anti-patterns. "
            "Consider the code's complexity; ignore trivial issues in simple applications.\n\n"
            
            "*** RESPONSE FORMATTING ***\n"
            "You MUST format your response as a single JSON object. Do not include any text outside the JSON structure. "
            "The JSON object must have two top-level keys: 'status' and 'antipatterns'.\n\n"

            "1. If you find one or more significant anti-patterns:\n"
            "- Set the 'status' to 'ISSUES_FOUND'.\n"
            "- Populate the 'antipatterns' list with objects, each having these keys: 'name', 'location', 'description', 'severity'.\n"
            "Example with issues:\n"
            "{\n"
            '  "status": "ISSUES_FOUND",\n'
            '  "antipatterns": [\n'
            '    { "name": "God Class", "location": "Main", "description": "...", "severity": "High" }\n'
            '  ]\n'
            "}\n\n"

            "2. If you find no significant anti-patterns:\n"
            "- Set the 'status' to 'NO_ISSUES_FOUND'.\n"
            "- The 'antipatterns' list must be empty.\n"
            "Example with no issues:\n"
            "{\n"
            '  "status": "NO_ISSUES_FOUND",\n'
            '  "antipatterns": []\n'
            "}\n\n"

            f"Here is the Java code to analyze:\n```java\n{code}\n```\n\n"
            "Respond only with the JSON output:"
        )

        response = self.model.invoke(prompt)
        print("Analysis complete.\n")
        return response
