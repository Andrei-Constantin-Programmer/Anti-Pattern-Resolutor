
"""
Main entry point - Legacy Code Migration Tool
"""
from src.core.graph import CreateGraph
from src.data.database import VectorDBManager
from config.settings import initialize_settings
from dotenv import load_dotenv
load_dotenv()

def main():
    """Main function: Run antipattern analysis"""
    
    # Let user select provider
    print("Available providers: 1) ollama  2) ibm  3) vllm")
    choice = input("Select provider (1-3): ").strip()
    
    provider_map = {"1": "ollama", "2": "ibm", "3": "vllm"}
    provider = provider_map.get(choice, "ollama")  # default to ollama
    
    # Initialize global settings with selected provider
    settings = initialize_settings(provider)
    print(f"Using {settings.LLM_PROVIDER} with model {settings.LLM_MODEL}")
    
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
        "answer": None
    }
    
    vector_db = VectorDBManager()
    langgraph = CreateGraph(db_manager=vector_db.get_db()).workflow
    final_state = langgraph.invoke(initial_state)
    
    print(f"\n🎉 Analysis Complete!")
    print(f"📝 Final state keys: {list(final_state.keys())}")
    print(f"📄 Context retrieved: {'Yes' if final_state.get('context') else 'No'}")
    print(f"📋 Analysis completed: {'Yes' if final_state.get('answer') else 'No'}")


if __name__ == "__main__":
    main()
