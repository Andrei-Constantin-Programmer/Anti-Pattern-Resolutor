"""
ExplainerAgent — minimal version
- Delegates state handling to create_graph.py
- Uses PromptManager if available; otherwise a tiny inline fallback prompt
- Always passes msgs; always returns a non-empty explanation_json
"""
from __future__ import annotations

from typing import Dict, Any
import json

from langchain_core.language_models import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
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
            msgs=state.get("msgs", []),  # ensure MessagesPlaceholder is satisfied
        )

        messages = self._build_messages(**kwargs)

        try:
            response = self.llm.invoke(messages)
            raw = getattr(response, "content", None) or str(response)
        except Exception as e:
            raw = f"LLM error: {e}"

        state["explanation_response_raw"] = raw

        # Robust parse: accept dict, wrap list, or emit a minimal fallback
        try:
            parsed = extract_first_json(raw)
        except Exception:
            parsed = None

        if isinstance(parsed, dict):
            state["explanation_json"] = parsed
        elif isinstance(parsed, list):
            state["explanation_json"] = {"items": parsed}
        else:
            state["explanation_json"] = self._fallback_payload(state)

        return state

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("\n=== Explanation (raw) ===\n", state.get("explanation_response_raw", "N/A"))
        if state.get("explanation_json"):
            print("\n=== Explanation (JSON) ===\n",
                  json.dumps(state["explanation_json"], indent=2, ensure_ascii=False))
        return state

    def _build_messages(self, **kwargs) -> Any:
        # Always ensure msgs exists
        if "msgs" not in kwargs or kwargs["msgs"] is None:
            kwargs = {**kwargs, "msgs": []}

        # 1) Try preloaded template from PromptManager
        prompt = None
        getp = getattr(self.prompt_manager, "get_prompt", None)
        if callable(getp):
            prompt = getp(PROMPT_KEY)
        if prompt is not None:
            return prompt.format_messages(**kwargs)

        # 2) Minimal inline fallback
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
            "Given inputs (JSON):\n" + json.dumps({k: v for k, v in kwargs.items() if k != "msgs"}, ensure_ascii=False) +
            "\nRespond with STRICT JSON using exactly this schema:\n" +
            json.dumps(schema, ensure_ascii=False)
        )
        fallback = ChatPromptTemplate.from_messages([
            ("system", "Return STRICT JSON only. No commentary."),
            ("user", content),
            MessagesPlaceholder("msgs"),
        ])
        return fallback.format_messages(**kwargs)

    @staticmethod
    def _fallback_payload(state: Dict[str, Any]) -> Dict[str, Any]:
        """Tiny fallback so downstream never breaks if parsing fails."""
        return {
            "items": [{
                "antipattern_name": state.get("antipattern_name", "Unknown antipattern"),
                "antipattern_description": state.get("antipattern_description", ""),
                "impact": "",
                "why_it_is_bad": "",
                "how_we_fixed_it": state.get("refactor_rationale", ""),
                "refactored_code": state.get("refactored_code", ""),
                "summary": "Auto-generated minimal explanation (parser fallback)."
            }],
            "what_changed": [],
            "why_better": [],
            "principles_applied": [],
            "trade_offs": [],
            "closing_summary": ""
        }
