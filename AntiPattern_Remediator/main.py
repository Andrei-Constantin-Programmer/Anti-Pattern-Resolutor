"""
Main entry point - Legacy Code Migration Tool
"""
from src.core.prompt import PromptManager
from config.settings import initialize_settings

from dotenv import load_dotenv
load_dotenv()
from colorama import Fore, Style


import json
import difflib
import textwrap
import re


def _print_section(title: str, body: str | None, color=Fore.CYAN):
    print("\n" + color + f"===== {title} =====" + Style.RESET_ALL)
    if body:
        print(body)
    else:
        print("(none)")


def _print_json_section(title: str, data):
    try:
        text = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        text = str(data)
    _print_section(title, text)


def _unified_diff(old: str, new: str, language_label="java"):
    old_lines = (old or "").splitlines(keepends=False)
    new_lines = (new or "").splitlines(keepends=False)
    diff = difflib.unified_diff(
        old_lines, new_lines, fromfile="original", tofile="refactored", lineterm=""
    )
    diff_text = "\n".join(diff)
    if not diff_text.strip():
        return "No differences."
    # Wrap in a fenced block so it’s readable in logs/terminals that support it
    return f"```diff\n{diff_text}\n```"

# add these helpers above main()

def _strip_code_fences(s: str) -> str:
    """Remove a single top-level fenced code block if present."""
    if not isinstance(s, str):
        return s
    m = re.match(r"^\s*```[a-zA-Z0-9]*\s*\n([\s\S]*?)\n```", s.strip())
    return m.group(1) if m else s

def _maybe_parse_json_block(s):
    """If s is a fenced JSON block or JSON string, return a dict; otherwise return s unchanged."""
    if isinstance(s, dict):
        return s
    if not isinstance(s, str):
        return s
    # Try fenced JSON first
    blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", s, flags=re.IGNORECASE)
    for cand in blocks + [s]:
        cand = cand.strip()
        if not cand:
            continue
        try:
            return json.loads(cand)
        except Exception:
            continue
    return s



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
    # Normalize context to a string to avoid prompt formatting issues
    initial_state = {
        "code": legacy_code,
        "context": "",
        "antipatterns_scanner_results": None,
        "refactoring_strategy_results": None,
        "refactored_code": None,
        "answer": None
    }

    # Setup Database
    if db_choice == "2":
        print("Seeding TinyDB with AntiPattern Dataset")
        try:
            seed_database.main()
        except Exception as e:
            print(Fore.YELLOW + f"Warning: seeding TinyDB failed: {e}" + Style.RESET_ALL)
        db_manager = TinyDBManager()
        print("Using TinyDB for knowledge retreival")
    else:
        vector_db = VectorDBManager()
        db_manager = vector_db.get_db()
        print("Using ChromaDB for knowledge retreival")

    langgraph = CreateGraph(db_manager, prompt_manager).workflow
    final_state = langgraph.invoke(initial_state)

    # ----- Summary -----
    print(Fore.GREEN + f"\nAnalysis Complete!" + Style.RESET_ALL)
    print(f"Final state keys: {list(final_state.keys())}")
    print(f"Context retrieved: {'Yes' if final_state.get('context') else 'No'}")
    print(f"Analysis completed: {'Yes' if final_state.get('antipatterns_scanner_results') else 'No'}")
    print(f"Refactored code: {'Yes' if final_state.get('refactored_code') else 'No'}")

        # ----- Detailed Output -----
    # 1) Scanner results
    scanner = _maybe_parse_json_block(final_state.get("antipatterns_scanner_results"))
    if scanner:
        if isinstance(scanner, dict):
            _print_json_section("Antipatterns Detected", scanner)
        else:
            _print_section("Antipatterns Detected", scanner)

    # 2) Refactoring strategy
    strategy = _maybe_parse_json_block(final_state.get("refactoring_strategy_results"))
    if strategy:
        if isinstance(strategy, (dict, list)):
            _print_json_section("Refactoring Strategy", strategy)
        else:
            _print_section("Refactoring Strategy", strategy)

    # 3) Refactored code
    refactored_raw = final_state.get("refactored_code")
    if refactored_raw:
        refactored_clean = _strip_code_fences(textwrap.dedent(refactored_raw).strip())
        _print_section("Refactored Code", f"```java\n{refactored_clean}\n```")

        # 3a) Unified diff (original -> refactored)
        diff_text = _unified_diff(initial_state.get("code", ""), refactored_clean, "java")
        _print_section("Unified Diff (original → refactored)", diff_text)

    # 4) Explainer output (JSON first, fallback to raw)
    explanation_json = _maybe_parse_json_block(final_state.get("explanation_json"))
    explanation_raw = final_state.get("explanation_response_raw")
    if isinstance(explanation_json, dict) and explanation_json:
        _print_json_section("Explanation (Structured)", explanation_json)
    elif explanation_raw:
        _print_section("Explanation (Raw)", explanation_raw)



if __name__ == "__main__":
    main()
