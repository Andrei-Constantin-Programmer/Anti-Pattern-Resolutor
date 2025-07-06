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
        )

        try:
            response = self.model.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            print(f"Error during strategy generation: {e}")
            return f"[ERROR] Strategy generation failed: {e}"


if __name__ == "__main__":
    from watsonx_client import WatsonXClient
    from antipattern_scanner import AntipatternScanner

    code = """
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
    analysis = scanner.analyze(code)

    strategist = StrategistAgent(model)
    strategy = strategist.suggest_refactorings(code, analysis)
    print("\n📋 Suggested Strategies:")
    print(strategy)

