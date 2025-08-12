from typing import Dict, Any, List
import json
import re
from langchain_core.language_models import BaseLanguageModel
from ..prompt import PromptManager


class ExplainerAgent:
    def __init__(self, llm: BaseLanguageModel, prompt_manager: PromptManager):
        self.llm = llm
        self.prompt_manager = prompt_manager

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
        messages = self.prompt_manager.render(
            self.prompt_manager.EXPLAINER_AGENT,
            code=state.get("code", ""),
            antipattern_name=state.get("antipattern_name", "Unknown antipattern"),
            antipattern_description=state.get("antipattern_description", ""),
            suggested_fix=state.get("suggested_fix", ""),
            language=state.get("language", "Java"),
            context=state.get("context", ""),
            refactored_code=state.get("refactored_code", ""),
            refactor_rationale=state.get("refactor_rationale", ""),
        )
        if not messages:
            state["explanation_response_raw"] = "Explainer prompt missing."
            state["explanation_json"] = {}
            return state

        response = self.llm.invoke(messages)
        raw = getattr(response, "content", None) or str(response)
        state["explanation_response_raw"] = raw

        # Try to parse the JSON block from the model response
        parsed = self._safe_parse_json(raw)
        state["explanation_json"] = parsed if isinstance(parsed, dict) else {}

        return state

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """(Optional) Print the structured explanation."""
        print("\n=== Explanation (raw) ===\n", state.get("explanation_response_raw", "N/A"))
        if state.get("explanation_json"):
            print("\n=== Explanation (JSON) ===\n", json.dumps(state["explanation_json"], indent=2))
        return state

    # -------------------------
    # Helpers
    # -------------------------
    def _safe_parse_json(self, text: str):
        """
        Extract and parse the first JSON block from text, tolerating code fences.
        Returns dict/list on success, or None on failure.
        """
        # Try fenced JSON first
        fenced = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
        candidates: List[str] = []
        candidates.extend(fenced)
        candidates.append(text)  # fall back to whole text

        for cand in candidates:
            cand = cand.strip()
            if not cand:
                continue
            try:
                return json.loads(cand)
            except Exception:
                continue
        return None
