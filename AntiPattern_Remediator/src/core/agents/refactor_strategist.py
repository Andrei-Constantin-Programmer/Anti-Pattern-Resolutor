from typing import List, Any, Callable, cast, Optional
from langchain_core.prompts import ChatPromptTemplate
from ..state import AgentState
from ..prompt import PromptManager
from colorama import Fore, Style


class RefactorStrategist:
    """Refactor strategist agent for managing code refactoring tasks.

    - Builds search queries from scanner findings
    - Retrieves context from the Trove (TinyDB/Chroma) via a unified `invoke`-style callable
    - Feeds `code`, `context` (scanner findings), and `trove_context` into the prompt
    - Writes the final strategy to `state["refactoring_strategy_results"]`
    """

    def __init__(
        self,
        model,
        prompt_manager: PromptManager,
        retriever: Optional[object] = None,
        *,
        max_queries: int = 5,   # configurable fan-out (replaces magic 6)
        top_k: int = 8,         # how many doc chunks to keep in trove_context
    ):
        self.prompt_manager = prompt_manager
        self.llm = model
        self.max_queries = max_queries
        self.top_k = top_k

        # --- normalize retriever to a single callable: self._search(query) -> List[Document] ---
        self._search: Callable[[str], List[Any]]
        if retriever is None:
            # no-op search to keep pipeline resilient
            self._search = lambda _q: []
        elif hasattr(retriever, "invoke"):
            # Many LC retrievers are Runnable and support .invoke(str) -> List[Document]
            self._search = lambda q: retriever.invoke(q)  # type: ignore[attr-defined]
        elif hasattr(retriever, "get_relevant_documents"):
            self._search = lambda q: retriever.get_relevant_documents(q)  # type: ignore[attr-defined]
        else:
            raise TypeError("retriever must implement .invoke(str) or .get_relevant_documents(str)")

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

        # bound the fan-out to control latency and prompt size
        return (queries or ["Java anti-patterns", "refactoring strategy"])[: self.max_queries]

    def _gather_trove_context(self, queries: List[str]) -> str:
        """Run searches and build a compact, deduplicated context block."""
        docs: List[Any] = []
        for q in queries:
            q = (q or "").strip()
            if not q:
                continue
            try:
                docs.extend(self._search(q))
            except Exception:
                continue

        # De-duplicate + cap
        unique_chunks: List[str] = []
        seen: set[str] = set()
        for d in docs:
            text = getattr(d, "page_content", str(d)).strip()
            if not text:
                continue
            sig = text[:160]
            if sig in seen:
                continue
            seen.add(sig)
            unique_chunks.append(text)
            if len(unique_chunks) >= self.top_k:
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

            # Trove evidence
            queries = self._build_queries_from_findings(findings)
            trove_ctx = self._gather_trove_context(queries) if queries else ""

            # Stash for later nodes / display
            state["trove_context"] = trove_ctx

            # Pass exactly the variables your YAML declares
            messages = tmpl.format_messages(
                code=code,
                context=findings,
                trove_context=trove_ctx,
                msgs=state.get("msgs", []),  # keep if PromptManager includes MessagesPlaceholder("msgs")
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
