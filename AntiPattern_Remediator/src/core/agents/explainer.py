from typing import Dict, Any
import json
from langchain_core.language_models import BaseLanguageModel
from ..prompt import PromptManager
from src.core.utils import extract_first_json


class ExplainerAgent:
    def __init__(self, llm: BaseLanguageModel, prompt_manager: PromptManager):
        self.llm = llm
        self.prompt_manager = prompt_manager

    # -------------------------
    # Public nodes
    # -------------------------
    def explain_antipattern(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a structured explanation for the detected antipattern and refactor.

        Expected (best effort) inputs in state:
            - code: str
            - antipattern_name: str
            - antipattern_description: str
            - suggested_fix: str
            - language: str (default: "Java")
            - context: str
            - refactored_code: str
            - refactor_rationale: str

        Outputs into state:
            - explanation_response_raw: str (raw LLM text)
            - explanation_json: dict (parsed JSON with what_changed / why_better / principles_applied / trade_offs / closing_summary)
        """
        messages = self._build_messages(state)
        if not messages:
            state["explanation_response_raw"] = "Explainer prompt missing."
            state["explanation_json"] = self._coerce_minimal_json(state)
            return state

        # Invoke LLM
        response = self.llm.invoke(messages)
        raw = getattr(response, "content", None) or str(response)
        state["explanation_response_raw"] = raw

        # Try to parse JSON block; fall back to a minimal structure if needed
        parsed = extract_first_json(raw)
        state["explanation_json"] = parsed if isinstance(parsed, dict) else self._coerce_minimal_json(state)

        return state

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """(Optional) Print the structured explanation."""
        print("\n=== Explanation (raw) ===\n", state.get("explanation_response_raw", "N/A"))
        if state.get("explanation_json"):
            print("\n=== Explanation (JSON) ===\n", json.dumps(state["explanation_json"], indent=2, ensure_ascii=False))
        return state

    # -------------------------
    # Helpers
    # -------------------------
    def _build_messages(self, state: Dict[str, Any]):
        """Build chat messages using PromptManager.render if available, otherwise format_messages directly."""
        # Try render(...) first (recommended path)
        if hasattr(self.prompt_manager, "render"):
            try:
                return self.prompt_manager.render(
                    self.prompt_manager.EXPLAINER_AGENT,
                    code=state.get("code", ""),
                    antipattern_name=state.get("antipattern_name", "Unknown antipattern"),
                    antipattern_description=state.get("antipattern_description", ""),
                    suggested_fix=state.get("suggested_fix", ""),
                    language=state.get("language", "Java"),
                    context=state.get("context", ""),
                    refactored_code=state.get("refactored_code", ""),
                    refactor_rationale=state.get("refactor_rationale", ""),
                    msgs=[],  # for MessagesPlaceholder
                )
            except Exception:
                pass

        # Fallback to get_prompt(...).format_messages(...)
        tmpl = self.prompt_manager.get_prompt(self.prompt_manager.EXPLAINER_AGENT)
        if tmpl is None:
            return None
        return tmpl.format_messages(
            code=state.get("code", ""),
            antipattern_name=state.get("antipattern_name", "Unknown antipattern"),
            antipattern_description=state.get("antipattern_description", ""),
            suggested_fix=state.get("suggested_fix", ""),
            language=state.get("language", "Java"),
            context=state.get("context", ""),
            refactored_code=state.get("refactored_code", ""),
            refactor_rationale=state.get("refactor_rationale", ""),
            msgs=[],  # ensure placeholder is satisfied
        )

    def _coerce_minimal_json(self, state: Dict[str, Any]) -> dict:
        """
        Build a minimal, useful JSON payload from the available state so downstream code
        always has something structured to work with.
        """
        what_changed = []
        why_better = []
        principles = []

        # Heuristics from refactor rationale / suggested fix
        rationale = state.get("refactor_rationale", "") or ""
        if rationale:
            for line in rationale.splitlines():
                line = line.strip("•- ").strip()
                if line:
                    what_changed.append(line)

        suggested_fix = state.get("suggested_fix", "")
        if suggested_fix and not what_changed:
            what_changed.append(str(suggested_fix)[:240])

        # Map antipattern to likely principles (very light heuristic)
        ap = (state.get("antipattern_name") or "").lower()
        if "srp" in ap or "single responsibility" in ap:
            principles.append("Single Responsibility Principle (SRP)")
            why_better.append("Reduces reasons to change; improves cohesion and maintainability.")
        if "exception" in ap:
            principles.append("Fail Fast / Explicit Exceptions")
            why_better.append("Improves debuggability and correctness with explicit error handling.")
        if not principles:
            principles.append("Refactoring best practices")

        if not why_better:
            why_better.append("Improves maintainability, testability, and clarity.")

        closing = "Refactoring removes the antipattern and aligns the code with core design principles."

        return {
            "what_changed": what_changed[:8] or ["Refactored according to suggested plan."],
            "why_better": why_better[:8],
            "principles_applied": sorted(set(principles)),
            "trade_offs": [],
            "closing_summary": closing,
        }
