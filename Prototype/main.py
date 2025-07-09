"""
Main entrypoint for prototype: Antipattern Detection and Refactoring Strategy Generator
"""

from agents.antipattern_scanner import AntipatternScanner
from agents.strategist_agent import StrategistAgent
from utils.watsonx_client import WatsonXClient
import time


def main():
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

        public void backupData() {
            System.out.println("Backing up users and logs...");
        }
    }
    """

    #Modify code to read file, GET 

    model = WatsonXClient()

    # Antipattern analysis
    scanner = AntipatternScanner(model)
    analysis = scanner.analyze(code)
    print("\nAntipattern Analysis:\n" + "="*60)
    print(analysis) #POST Analysis
    
    time.sleep(5)

    # Refactoring strategy
    strategist = StrategistAgent(model)
    strategy = strategist.suggest_refactorings(code, analysis)
    print("\nRefactoring Strategy:\n" + "="*60)
    print(strategy) #POST Strategy


if __name__ == "__main__":
    main()
