from typing import List, Any, cast
from langchain_core.prompts import ChatPromptTemplate
from ..state import AgentState
from ..prompt import PromptManager
from colorama import Fore, Style


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
        self.retriever = retriever            # e.g., TinyDBManager or Chroma.as_retriever()
        self.retriever_tool = retriever_tool  # optional LangChain retriever tool

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
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

    def _trove_search(self, queries: List[str], cap: int = 8) -> str:
        """Query the Trove and return a compact, deduplicated text block."""
        docs = []

        for q in queries:
            try:
                if self.retriever and hasattr(self.retriever, "get_relevant_documents"):
                    docs.extend(self.retriever.get_relevant_documents(q))
                elif self.retriever and hasattr(self.retriever, "invoke"):
                    docs.extend(self.retriever.invoke(q))
                elif self.retriever_tool:
                    res = self.retriever_tool.invoke({"query": q})
                    if isinstance(res, list):
                        docs.extend(res)
                    else:
                        # Normalize to an object with page_content
                        docs.append(type("Doc", (), {"page_content": str(res)})())
            except Exception:
                # Retrieval shouldn't fail the whole step
                continue

        # De-duplicate and cap
        unique_chunks, seen = [], set()
        for d in docs:
            text = getattr(d, "page_content", str(d)).strip()
            if not text:
                continue
            sig = text[:160]
            if sig not in seen:
                seen.add(sig)
                unique_chunks.append(text)
            if len(unique_chunks) >= cap:
                break

        return "\n\n---\n\n".join(unique_chunks)

    # -------------------------------------------------------------------------
    # Pipeline steps
    # -------------------------------------------------------------------------
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

            # Build Trove queries from findings and fetch evidence
            queries = self._build_queries_from_findings(findings)
            trove_context = self._trove_search(queries) if queries else ""

            # Stash for later nodes / display
            state["trove_context"] = trove_context

            # IMPORTANT: pass exactly the variables your YAML declares
            messages = tmpl.format_messages(
                code=code,
                context=findings,
                trove_context=trove_context,
                msgs=state.get("msgs", []),  # satisfies MessagesPlaceholder if your PromptManager includes it
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
