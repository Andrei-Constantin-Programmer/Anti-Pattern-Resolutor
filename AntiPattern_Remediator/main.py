
"""
Main entry point - Legacy Code Migration Tool
"""
from config.settings import initialize_settings
# from scripts import seed_database
from dotenv import load_dotenv
load_dotenv()
from colorama import Fore, Style
import os
from pathlib import Path
from full_repo_workflow import run_full_repo_workflow


def run_code_snippet_workflow(settings, db_manager, prompt_manager, langgraph):
    """Run the original workflow with a hardcoded Java code snippet."""
    print(Fore.BLUE + "\n=== Code Snippet Analysis Workflow ===" + Style.RESET_ALL)
    print("Analyzing the provided Java code snippet...")
    
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
        "answer": None
    }

    final_state = langgraph.invoke(initial_state)

    print(Fore.GREEN + f"\nAnalysis Complete!" + Style.RESET_ALL)
    print(f"Final state keys: {list(final_state.keys())}")
    print(f"Context retrieved: {'Yes' if final_state.get('context') else 'No'}")
    print(f"Analysis completed: {'Yes' if final_state.get('antipatterns_scanner_results') else 'No'}")
    print(f"Refactored code: {'Yes' if final_state.get('refactored_code') else 'No'}")
    print(f"Code review results: {final_state.get('code_review_times')}")


def main():
    """Main function: Choose between code snippet analysis or full repository run"""

    print(Fore.BLUE + "=== AntiPattern Remediator Tool ===" + Style.RESET_ALL)
    print("Choose your analysis mode:")
    print("1) Code Snippet Analysis - Analyze a sample Java code snippet")
    print("2) Full Repository Run - Process files with 100% test coverage from JaCoCo results")
    
    # Let user choose analysis mode
    mode_choice = input("\nSelect mode (1-2): ").strip()
    
    if mode_choice not in ["1", "2"]:
        print(Fore.RED + "Invalid choice. Defaulting to Code Snippet Analysis." + Style.RESET_ALL)
        mode_choice = "1"
    
    # Let user select provider
    print("\nAvailable providers: 1) ollama  2) ibm  3) vllm")
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

    # Run the selected workflow
    if mode_choice == "1":
        run_code_snippet_workflow(settings, db_manager, prompt_manager, langgraph)
    else:
        run_full_repo_workflow(settings, db_manager, prompt_manager, langgraph)

if __name__ == "__main__":
    main()
