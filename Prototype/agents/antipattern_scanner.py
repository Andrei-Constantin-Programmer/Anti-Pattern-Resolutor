class AntipatternScanner:
    """
    Agent to analyze Java code and detect antipatterns.
    """

    def __init__(self, model):
        self.model = model  # WatsonXClient instance

    def analyze(self, code: str) -> str:
        print("Analyzing Java code for antipatterns...")

        prompt = (
            "You are an expert in software architecture. "
            "Analyze the following Java code and identify common antipatterns. "
            "For each antipattern, provide:\n"
            "- Name of the antipattern\n"
            "- Location (class/method)\n"
            "- Brief description\n"
            "- Why it's a problem\n"
            "- Keep your answers short and precise"
            "Antipattern Report:"
        )

        response = self.model.invoke(prompt)
        print("Analysis complete.\n")
        return response
