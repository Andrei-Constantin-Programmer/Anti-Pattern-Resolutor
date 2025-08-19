# src/core/agents/explainer.py
from typing import Dict, Any, List
import json
from langchain_core.language_models import BaseLanguageModel
from ..prompt import PromptManager
from src.core.utils import extract_first_json

try:
    from config.settings import settings
    MAX_EXPLAINER_BULLETS = getattr(settings, "MAX_EXPLAINER_BULLETS", 8)
    MAX_SUGGESTED_FIX_SNIPPET = getattr(settings, "MAX_SUGGESTED_FIX_SNIPPET", 240)
except Exception:
    # Fallback defaults for tests / minimal envs
    MAX_EXPLAINER_BULLETS = 8
    MAX_SUGGESTED_FIX_SNIPPET = 240


class ExplainerAgent:
    def __init__(self, llm: BaseLanguageModel, prompt_manager: PromptManager):
        self.llm = llm
        self.prompt_manager = prompt_manager

    def explain_antipattern(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a structured explanation for the detected antipatterns and refactor.
        Expects in state (best-effort): code, antipatterns_scanner_results, refactoring_strategy_results,
        suggested_fix, language, context, refactored_code.
        """
        self._prepare_inputs(state)  # <-- moved from graph; low coupling

        # Build prompt variables from prepared state
        kwargs = dict(
            code=state.get("code", ""),
            language=state.get("language", "Java"),
            context=state.get("context", ""),
            refactored_code=state.get("refactored_code", ""),
            refactor_rationale=state.get("refactor_rationale", ""),
            antipattern_name=state.get("antipattern_name", "Unknown antipattern"),
            antipattern_description=state.get("antipattern_description", ""),
            antipatterns_json=json.dumps(state.get("antipatterns_json", []), ensure_ascii=False),
            suggested_fix=state.get("suggested_fix", ""),
            msgs=state.get("msgs", []),
        )

        messages = self.prompt_manager.render(self.prompt_manager.EXPLAINER_AGENT, **kwargs)
        if not messages:
            state["explanation_response_raw"] = "Explainer prompt missing."
            state["explanation_json"] = self._coerce_minimal_json(state)
            return state

        response = self.llm.invoke(messages)
        raw = getattr(response, "content", None) or str(response)
        state["explanation_response_raw"] = raw

        parsed = extract_first_json(raw)
        state["explanation_json"] = parsed if isinstance(parsed, dict) else self._coerce_minimal_json(state)
        return state

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("\n=== Explanation (raw) ===\n", state.get("explanation_response_raw", "N/A"))
        if state.get("explanation_json"):
            print("\n=== Explanation (JSON) ===\n", json.dumps(state["explanation_json"], indent=2, ensure_ascii=False))
        return state

    # ---------- internal prep moved from graph ----------
    def _prepare_inputs(self, state: Dict[str, Any]) -> None:
        """Normalize and derive explainer inputs from current state."""
        state.setdefault("language", "Java")
        state.setdefault("context", "")
        state.setdefault("code", state.get("original_code", state.get("code", "")) or "")
        state.setdefault("refactored_code", state.get("refactored_code", "") or "")

        # Build antipatterns list & headline
        headline_name = "Unknown antipattern"
        headline_desc = ""
        all_items: List[Dict[str, Any]] = []

        scan = state.get("antipatterns_scanner_results")
        if isinstance(scan, dict):
            items = scan.get("antipatterns_detected") or []
            if isinstance(items, list):
                # normalize minimal shape
                for it in items:
                    if isinstance(it, dict):
                        all_items.append({
                            "name": it.get("name", ""),
                            "location": it.get("location", ""),
                            "description": it.get("description", ""),
                        })
                if all_items:
                    headline_name = all_items[0].get("name") or headline_name
                    headline_desc = all_items[0].get("description", "")

        state.setdefault("antipattern_name", headline_name)
        state.setdefault("antipattern_description", headline_desc)
        state["antipatterns_json"] = all_items  # pass the full list to the prompt

        # Rationale: prefer strategist output, fallback to suggested_fix
        strategy = state.get("refactoring_strategy_results")
        if strategy:
            state["refactor_rationale"] = str(strategy)
        elif state.get("suggested_fix"):
            state["refactor_rationale"] = str(state["suggested_fix"])
        else:
            state.setdefault("refactor_rationale", "")

    # ---------- unchanged: minimal JSON coercion ----------
    def _coerce_minimal_json(self, state: Dict[str, Any]) -> dict:
        what_changed: List[str] = []
        why_better: List[str] = []
        principles: List[str] = []

        rationale = (state.get("refactor_rationale") or "").strip()
        if rationale:
            for line in rationale.splitlines():
                line = line.strip().lstrip("•-*").strip()
                if line:
                    what_changed.append(line)

        suggested_fix = state.get("suggested_fix", "")
        if suggested_fix and not what_changed:
            what_changed.append(str(suggested_fix)[:MAX_SUGGESTED_FIX_SNIPPET])

        ap = (state.get("antipattern_name") or "").lower()
        if "srp" in ap or "single responsibility" in ap:
            principles.append("Single Responsibility Principle (SRP)")
            why_better.append("Reduces reasons to change; improves cohesion and maintainability.")
        if "exception" in ap or "error" in ap:
            principles.append("Fail Fast / Explicit Exceptions")
            why_better.append("Improves debuggability and correctness via explicit error handling.")
        if not principles:
            principles.append("Refactoring best practices")

        if not why_better:
            why_better.append("Improves maintainability, testability, and clarity.")

        return {
            "what_changed": (what_changed[:MAX_EXPLAINER_BULLETS] or ["Refactored according to suggested plan."]),
            "why_better":   why_better[:MAX_EXPLAINER_BULLETS],
            "principles_applied": sorted(set(principles)),
            "trade_offs": [],
            "closing_summary": "Refactoring removes the antipattern and aligns the code with core design principles.",
        }
