from typing import Dict, Any
from langchain_core.language_models import BaseLanguageModel
from ..prompt import PromptManager


class ExplainerAgent:
    def __init__(self, llm: BaseLanguageModel, prompt_manager: PromptManager):
        self.llm = llm
        self.prompt_manager = prompt_manager

    def explain_antipattern(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an explanation for the detected antipattern.
        Expects `state` to contain:
            - code
            - antipattern_name
            - antipattern_description
            - suggested_fix
            - language
            - context
        """
        prompt_template = self.prompt_manager.get_prompt("explainer_agent")

        # Prepare prompt with inputs
        user_prompt = prompt_template["user"].format(
            code=state["code"],
            antipattern_name=state["antipattern_name"],
            antipattern_description=state["antipattern_description"],
            suggested_fix=state["suggested_fix"],
            language=state.get("language", "Java"),
            context=state.get("context", "")
        )

        system_prompt = prompt_template["system"]

        response = self.llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        state["explanation_response"] = response.content
        return state

    def display_explanation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """(Optional) Displays or logs the explanation output"""
        print("\nExplanation:\n", state.get("explanation_response", "No explanation available."))
        return state
