from typing import List, Any, cast
from langchain_core.prompts import ChatPromptTemplate
from ..state import AgentState
from ..prompt import PromptManager
from colorama import Fore, Style
from src.data import trove_search_context  # re-exported from src/data/__init__.py


class RefactorStrategist:
    """Refactor strategist agent for managing code refactoring tasks.

    - Builds search queries from scanner findings
    - Retrieves context from the Trove (TinyDB/Chroma) via retriever or retriever_tool
    - Feeds `code`, `context` (scanner findings), and `trove_context` into the prompt
    - Writes the final strategy to `state["refactoring_strategy_results"]`
    """

    def __init__(self, model, prompt_manager: PromptManager, retriever=None, retriever_tool=None):
        self.prompt_manager = prompt_manager
        self.llm = model
        self.retriever = retriever
        self.retriever_tool = retriever_tool


    def _build_queries_from_findings(self, findings: Any) -> List[str]:
        """Turn scanner findings into focused search queries."""
        if not findings:
            return []
        queries: List[str] = []

        # findings may be a list[dict]/list[str] or a str (JSON text)
        if isinstance(findings, list):
            for f in findings:
                if isinstance(f, dict):
                    for key in ("name", "antipattern", "label", "rule", "category"):
                        if f.get(key):
                            queries.append(str(f[key]))
                            break
                elif isinstance(f, str):
                    queries.append(f)
        elif isinstance(findings, str):
            # pass the whole blob; TinyDB keyword search or vector retriever will still try to match
            queries.append(findings)

        if not queries:
            queries = ["Java anti-patterns", "refactoring strategy"]
        return queries[:6]


    def strategize_refactoring(self, state: AgentState):
        print("Strategizing refactoring options...")
        try:
            tmpl = cast(
                ChatPromptTemplate,
                self.prompt_manager.get_prompt(self.prompt_manager.REFACTOR_STRATEGIST),
            )
            if tmpl is None:
                raise RuntimeError("Prompt 'refactor_strategist' not found or not loaded")

            findings = state.get("antipatterns_scanner_results")
            code = state.get("code", "")

            # Trove evidence (via tiny helper)
            queries = self._build_queries_from_findings(findings)
            trove_ctx = trove_search_context(
                queries,
                retriever=self.retriever,
                retriever_tool=self.retriever_tool,
                cap=8,
            ) if queries else ""

            # Stash for later nodes / display
            state["trove_context"] = trove_ctx

            messages = tmpl.format_messages(
                code=code,
                context=findings,
                trove_context=trove_ctx,
                msgs=state.get("msgs", []),  # keep if PromptManager includes a MessagesPlaceholder("msgs")
            )

            response = self.llm.invoke(messages)
            content = getattr(response, "content", str(response))
            state["refactoring_strategy_results"] = content

            print(Fore.GREEN + "Refactoring strategy created successfully" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error during strategizing: {e}" + Style.RESET_ALL)
            state["refactoring_strategy_results"] = f"Error occurred during strategizing: {e}"
        return state

    def display_refactoring_results(self, state: AgentState):
        """Display the final refactoring strategy results (and Trove context if available)."""
        print("\nREFACTORING STRATEGY RESULTS")
        print("=" * 60)

        if state.get("trove_context"):
            print(Fore.CYAN + "[Trove Context Retrieved]" + Style.RESET_ALL)
            print(state["trove_context"])
            print("-" * 60)

        print(state.get("refactoring_strategy_results", "No refactoring strategy available."))
        print("=" * 60)
        return state
