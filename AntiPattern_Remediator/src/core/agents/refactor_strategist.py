from typing import List, Any, Optional
from ..state import AgentState
from ..prompt import PromptManager
from colorama import Fore, Style


class RefactorStrategist:
    """Refactor strategist agent for managing code refactoring tasks"""

    def __init__(self, model, prompt_manager: PromptManager, retriever=None, retriever_tool=None):
        self.prompt_manager = prompt_manager
        self.llm = model
        self.retriever = retriever          # e.g., TinyDBManager or Chroma.as_retriever()
        self.retriever_tool = retriever_tool  # optional: LangChain retriever tool

    # ---- helpers -------------------------------------------------------------

    def _build_queries_from_findings(self, findings: Any) -> List[str]:
        """Turn scanner findings into focused search queries."""
        if not findings:
            return []
        queries: List[str] = []

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
            queries.append(findings)

        # sensible fallbacks if nothing parsed cleanly
        if not queries:
            queries = ["Java anti-patterns", "refactoring strategy"]
        return queries[:6]

    def _trove_search(self, queries: List[str], cap: int = 8) -> str:
        """Query the Trove via retriever or tool and return a compact text block."""
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
                    elif isinstance(res, str):
                        # normalize to a doc-like object with page_content
                        docs.append(type("Doc", (), {"page_content": res})())
            except Exception:
                # never fail strategizing because retrieval hiccupped
                continue

        # de-dup + cap
        unique_chunks, seen = [], set()
        for d in docs:
            chunk = getattr(d, "page_content", str(d)).strip()
            if not chunk:
                continue
            sig = chunk[:160]
            if sig not in seen:
                seen.add(sig)
                unique_chunks.append(chunk)
            if len(unique_chunks) >= cap:
                break

        return "\n\n---\n\n".join(unique_chunks)

    # ---- pipeline steps ------------------------------------------------------

    def strategize_refactoring(self, state: AgentState):
        print("Strategizing refactoring options...")
        try:
            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.REFACTOR_STRATEGIST)

            findings = state.get("antipatterns_scanner_results")
            code = state.get("code", "")

            # Build queries from findings and fetch Trove evidence
            queries = self._build_queries_from_findings(findings)
            trove_context = self._trove_search(queries) if queries else ""

            # Stash for downstream nodes / debugging display
            state["trove_context"] = trove_context

            # IMPORTANT: your YAML now expects code, context (scanner findings), trove_context
            formatted_messages = prompt_template.format_messages(
                code=code,
                context=findings,
                trove_context=trove_context
            )

            response = self.llm.invoke(formatted_messages)
            content = response.content if hasattr(response, "content") else str(response)
            state["refactoring_strategy_results"] = content

            print(Fore.GREEN + "Refactoring strategy created successfully" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error during strategizing: {e}" + Style.RESET_ALL)
            state["refactoring_strategy_results"] = f"Error occurred during strategizing: {e}"
        return state

    def display_refactoring_results(self, state: AgentState):
        """Display the final refactoring strategy results"""
        print("\nREFACTORING STRATEGY RESULTS")
        print("=" * 60)

        # Show Trove context if it exists (useful for verifying retrieval)
        if state.get("trove_context"):
            print(Fore.CYAN + "[Trove Context Retrieved]" + Style.RESET_ALL)
            print(state["trove_context"])
            print("-" * 60)

        print(state.get("refactoring_strategy_results", "No refactoring strategy available."))
        print("=" * 60)
        return state
