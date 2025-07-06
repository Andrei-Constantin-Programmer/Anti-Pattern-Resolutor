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
            "- Suggested refactoring strategy\n\n"
            f"Java Code:\n{code}\n\n"
            "Antipattern Report:"
        )

        response = self.model.invoke(prompt)
        print("Analysis complete.\n")
        return response

if __name__ == "__main__":
    from watsonx_client import WatsonXClient

    sample_code = """
    public class ApplicationManager {
        private List<String> users = new ArrayList<>();
        private List<String> logs = new ArrayList<>();

        public void addUser(String user) {
            users.add(user);
            logs.add("User added: " + user);
        }

        public void removeUser(String user) {
            users.remove(user);
            logs.add("User removed: " + user);
        }

        public void printReport() {
            System.out.println("Users: " + users);
            System.out.println("Logs: " + logs);
        }
    }
    """

    model = WatsonXClient()
    scanner = AntipatternScanner(model)
    report = scanner.analyze(sample_code)
    print(report)
