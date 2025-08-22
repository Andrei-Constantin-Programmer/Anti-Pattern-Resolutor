"""
ExplainerAgent — minimal version
- Delegates state handling to create_graph.py
- Only builds messages and parses JSON response
- Keeps code minimal and focused
"""
from __future__ import annotations

from typing import Dict, Any
import json

from langchain_core.language_models import BaseLanguageModel
from ..prompt import PromptManager
from src.core.utils import extract_first_json

PROMPT_KEY = "explainer"


class ExplainerAgent:
    def __init__(self, llm: BaseLanguageModel, prompt_manager: PromptManager):
        self.llm = llm
        self.prompt_manager = prompt_manager

    def explain_antipattern(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation JSON for detected antipatterns and refactor."""
        kwargs = dict(
            code=state.get("code", ""),
            language=state.get("language", "Java"),
            context=state.get("context", ""),
            refactored_code=state.get("refactored_code", ""),
            refactor_rationale=state.get("refactor_rationale", ""),
            antipattern_name=state.get("antipattern_name", "Unknown antipattern"),
            antipattern_description=state.get("antipattern_description", ""),
            antipatterns_json=json.dumps(state.get("antipatterns_json", []), ensure_ascii=False),
        )

        messages = self._build_messages(**kwargs)
        response = self.llm.invoke(messages)
        raw = getattr(response, "content", None) or str(response)
        state["explanation_response_raw"] = raw

        parsed = extract_first_json(raw)
        state["explanation_json"] = parsed if isinstance(parsed, dict) else {}
        return state

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("\n=== Explanation (raw) ===\n", state.get("explanation_response_raw", "N/A"))
        if state.get("explanation_json"):
            print("\n=== Explanation (JSON) ===\n", json.dumps(state["explanation_json"], indent=2, ensure_ascii=False))
        return state

    def _build_messages(self, **kwargs) -> Any:
        try:
            getp = getattr(self.prompt_manager, "get_prompt", None)
            if callable(getp):
                prompt = getp(PROMPT_KEY)
                if prompt is not None:
                    return prompt.format_messages(**kwargs)
        except Exception:
            pass

        schema = {
            "items": [{
                "antipattern_name": "",
                "antipattern_description": "",
                "impact": "",
                "why_it_is_bad": "",
                "how_we_fixed_it": "",
                "refactored_code": "",
                "summary": ""
            }],
            "what_changed": [],
            "why_better": [],
            "principles_applied": [],
            "trade_offs": [],
            "closing_summary": ""
        }
        content = (
            "Given inputs (JSON):\n" + json.dumps(kwargs, ensure_ascii=False) +
            "\nRespond with STRICT JSON using exactly this schema:\n" +
            json.dumps(schema, ensure_ascii=False)
        )
        return [
            {"role": "system", "content": "Return STRICT JSON only. No commentary."},
            {"role": "user", "content": content},
        ]
