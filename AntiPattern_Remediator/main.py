"""
Main entry point - Legacy Code Migration Tool
"""
from config.settings import initialize_settings
from dotenv import load_dotenv
load_dotenv()
from colorama import Fore, Style


def main():
    """Main function: Run antipattern analysis"""

    # Let user select provider
    print("Available providers: 1) ollama  2) ibm  3) vllm")
    choice = input("Select provider (1-3): ").strip()

    provider_map = {"1": "ollama", "2": "ibm", "3": "vllm"}
    provider = provider_map.get(choice, "ollama")  # default to ollama

    # Let us choose which DB to interact with
    print("Choose your trove: 1) ChromaDB (VectorDB) 2) TinyDB (DocumentDB)")
    db_choice = input("Choose 1 or 2: ").strip()

    # Initialize global settings with selected provider
    settings = initialize_settings(provider)
    print(Fore.GREEN + f"Using {settings.LLM_PROVIDER} with model {settings.LLM_MODEL}" + Style.RESET_ALL)

    # Temporary Lazy Imports
    from src.core.graph import CreateGraph
    from src.data.database import VectorDBManager, TinyDBManager
    from src.core.prompt import PromptManager
    from scripts import seed_database

    # Initialize PromptManager
    print("Initializing PromptManager...")
    prompt_manager = PromptManager()

    # Example Java code
    legacy_code = """
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

        public void logEvent(String event) {
            logs.add(event);
        }

        public void printReport() {
            System.out.println("=== Users ===");
            for (String user : users) {
                System.out.println(user);
            }

            System.out.println("=== Logs ===");
            for (String log : logs) {
                System.out.println(log);
            }
        }

        public void backupData() {
            // Placeholder: pretend this backs up all data
            System.out.println("Backing up users and logs...");
        }
    }
    """

    # Initial workflow state
    initial_state = {
        "code": legacy_code,
        "context": None,
        "trove_context": None,
        "antipatterns_scanner_results": None,
        "refactoring_strategy_results": None,
        "refactored_code": None,
        "code_review_results": None,
        "code_review_times": 0,
        "msgs": [],
        "answer": None,

        # ExplainerAgent fields
        "explanation_response_raw": None,
        "explanation_json": None,
    }

    # Setup Database
    if db_choice == "2":
        print("Seeding TinyDB with AntiPattern Dataset")
        seed_database.main()
        db_manager = TinyDBManager()
        print("Using TinyDB for knowledge retrieval")
    else:
        vector_db = VectorDBManager()
        db_manager = vector_db.get_db()
        print("Using ChromaDB for knowledge retrieval")

    retriever = db_manager.as_retriever()
    langgraph = CreateGraph(db_manager, prompt_manager, retriever=retriever).workflow
    final_state = langgraph.invoke(initial_state)

    # Final results summary
    print(Fore.GREEN + f"\nAnalysis Complete!" + Style.RESET_ALL)
    print(f"Final state keys: {list(final_state.keys())}")
    print(f"Context retrieved: {'Yes' if final_state.get('context') else 'No'}")
    print(f"Analysis completed: {'Yes' if final_state.get('antipatterns_scanner_results') else 'No'}")
    print(f"Refactored code: {'Yes' if final_state.get('refactored_code') else 'No'}")
    print(f"Code review results: {final_state.get('code_review_times')}")

    # Show explanation from ExplainerAgent
    if final_state.get("explanation_json"):
        import json
        print(Fore.CYAN + "\n=== Explanation (JSON) ===" + Style.RESET_ALL)
        print(json.dumps(final_state["explanation_json"], indent=2, ensure_ascii=False))
    else:
        print(Fore.RED + "\nNo explanation was generated." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
