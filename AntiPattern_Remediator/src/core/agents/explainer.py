"""
ExplainerAgent — full-state returns, collision-safe
- Returns a full state dict but NEVER writes 'code' back to the graph.
- Uses PromptManager if available; otherwise falls back to an inline prompt.
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

    # Merge helper: return a FULL state but drop keys we must not rewrite.
    @staticmethod
    def _merge_return_state(state: Dict[str, Any], updates: Dict[str, Any], drop_keys=("code",)) -> Dict[str, Any]:
        merged = dict(state)
        # don't write to LastValue 'code' to avoid concurrent updates
        for k in drop_keys:
            if k in merged:
                merged.pop(k)
        merged.update(updates or {})
        return merged

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
            msgs=state.get("msgs", []),
        )

        messages = self._build_messages(**kwargs)

        try:
            response = self.llm.invoke(messages)
            raw = getattr(response, "content", None) or str(response)
        except Exception as e:
            raw = f"LLM error: {e}"

        # Robust parse
        try:
            parsed = extract_first_json(raw)
        except Exception:
            parsed = None

        if isinstance(parsed, dict):
            exp_json = parsed
        elif isinstance(parsed, list):
            exp_json = {"items": parsed}
        else:
            exp_json = self._fallback_payload(state)

        updates = {
            "explanation_response_raw": raw,
            "explanation_json": exp_json,
        }
        # ✅ Return FULL state but with 'code' removed to avoid LastValue collision
        return self._merge_return_state(state, updates, drop_keys=("code",))

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("\n=== Explanation (raw) ===\n", state.get("explanation_response_raw", "N/A"))
        if state.get("explanation_json"):
            print(
                "\n=== Explanation (JSON) ===\n",
                json.dumps(state["explanation_json"], indent=2, ensure_ascii=False),
            )
        # ✅ Return FULL state but again ensure 'code' isn't echoed back
        return self._merge_return_state(state, {}, drop_keys=("code",))

    def _build_messages(self, **kwargs) -> Any:
        if "msgs" not in kwargs or kwargs["msgs"] is None:
            kwargs = {**kwargs, "msgs": []}

        prompt = None
        getp = getattr(self.prompt_manager, "get_prompt", None)
        if callable(getp):
            prompt = getp(PROMPT_KEY)
        if prompt is not None:
            # Your YAML already has doubled braces for the literal JSON schema.
            # If a stray KeyError occurs, fall back to inline prompt.
            try:
                return prompt.format_messages(**kwargs)
            except KeyError:
                pass

        # Minimal inline fallback
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
            "Given inputs (JSON):\n"
            + json.dumps({k: v for k, v in kwargs.items() if k != "msgs"}, ensure_ascii=False)
            + "\nRespond with STRICT JSON using exactly this schema:\n"
            + json.dumps(schema, ensure_ascii=False)
        )
        fallback = ChatPromptTemplate.from_messages([
            ("system", "Return STRICT JSON only. No commentary."),
            ("user", content),
            MessagesPlaceholder("msgs"),
        ])
        return fallback.format_messages(**kwargs)

    @staticmethod
    def _fallback_payload(state: Dict[str, Any]) -> Dict[str, Any]:
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
