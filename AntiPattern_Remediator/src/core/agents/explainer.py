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
from langchain_core.prompts import PromptTemplate
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
        print("Preparing to Explain...")
        kwargs = dict(
            code=state.get("code", ""),
            context=state.get("context", ""),
            refactored_code=state.get("refactored_code", ""),
            refactoring_strategy=state.get("refactoring_strategy_results", ""),
            antipattern_name=state.get("antipatterns_scanner_results", "Unknown antipattern"),
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
        # Return FULL state but with 'code' removed to avoid LastValue collision
        return self._merge_return_state(state, updates, drop_keys=("code",))

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("\n=== Explanation (raw) ===\n", state.get("explanation_response_raw", "N/A"))
        if state.get("explanation_json"):
            print(
                "\n=== Explanation (JSON) ===\n",
                json.dumps(state["explanation_json"], indent=2, ensure_ascii=False),
            )
        # Return FULL state but again ensure 'code' isn't echoed back
        return self._merge_return_state(state, {}, drop_keys=("code",))

    def _build_messages(self, **kwargs) -> Any:
        """
        Build a list of messages for the LLM.
        Uses the user‑supplied prompt if available; otherwise falls back to an
        inline prompt that safely injects JSON strings via placeholders.
        """
        if "msgs" not in kwargs or kwargs["msgs"] is None:
            kwargs = {**kwargs, "msgs": []}

        # Try to get a prompt from the PromptManager
        prompt = None
        getp = getattr(self.prompt_manager, "get_prompt", None)
        if callable(getp):
            prompt = getp(PROMPT_KEY)

        if prompt is not None:
            # The prompt from PromptManager should already be a PromptTemplate
            # or a string that can be formatted safely.
            try:
                return prompt.format_messages(**kwargs)
            except KeyError:
                # Fall back if the prompt contains unexpected placeholders
                pass

        # ------------------------------------------------------------------
        # Inline fallback – use direct string template instead of nested PromptTemplate
        # ------------------------------------------------------------------
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

        # Prepare the JSON strings that will be inserted via placeholders
        json_input = json.dumps(
            {k: v for k, v in kwargs.items() if k != "msgs"},
            ensure_ascii=False
        )
        json_schema = json.dumps(schema, ensure_ascii=False)

        # Create the ChatPromptTemplate directly with string templates
        fallback = ChatPromptTemplate.from_messages([
            ("system", "Return STRICT JSON only. No commentary."),
            ("user", "Given inputs (JSON):\n{json_input}\nRespond with STRICT JSON using exactly this schema:\n{json_schema}"),
            MessagesPlaceholder("msgs"),
        ])

        # Format the messages with the prepared JSON strings
        return fallback.format_messages(
            json_input=json_input,
            json_schema=json_schema,
            msgs=kwargs["msgs"]
        )

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
