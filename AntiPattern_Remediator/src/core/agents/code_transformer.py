"""
Agent responsible for refactoring code based on analysis.
"""
from ..state import AgentState
from colorama import Fore, Style
from ..prompt import PromptManager
import re


class CodeTransformer:
    """Code Transformer Agent"""

    def __init__(self, model, prompt_manager: PromptManager):
        self.llm = model
        self.prompt_manager = prompt_manager
    
    def extract_java(s: str) -> str:
        
        # Strip common wrappers
        fences = [
            (r"^```[a-zA-Z0-9]*\n(.*?)\n```$", re.DOTALL),
            (r'^"""\s*\n?(.*?)\n?"""$',       re.DOTALL),
            (r"^'''\s*\n?(.*?)\n?'''$",       re.DOTALL),
        ]
        for pat, flg in fences:
            m = re.match(pat, s, flags=flg)
            if m:
                s = m.group(1).strip()
                break

        # Also remove stray leading/trailing fence lines if any
        s = re.sub(r"^```[a-zA-Z0-9]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
        s = re.sub(r'^"""\n?', "", s)
        s = re.sub(r'\n?"""$', "", s)
        s = re.sub(r"^'''\n?", "", s)
        s = re.sub(r"\n?'''$", "", s)

        return s.strip()

    def transform_code(self, state: AgentState) -> AgentState:
        print("--- TRANSFORMING CODE ---")
        try:
            original_code = state.get("code")
            strategy = state.get("refactoring_strategy_results")
            msgs = state.get('msgs', [])
            
            if not strategy:
                print("No valid strategy received. Skipping transformation.")
                state["refactored_code"] = "Transformation skipped due to missing strategy."
                raise ValueError("No valid strategy received for code transformation.")
            else:
                print("Strategy received, proceeding with transformation.")
            if msgs != []:
                print(f"{len(msgs)} Code Review messages received, proceeding with transformation.")

            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.CODE_TRANSFORMER)

            formatted_messages = prompt_template.format_messages(
                strategy=strategy,
                code=original_code,
                msgs=msgs
            )
            
            response = self.llm.invoke(formatted_messages)
            if response.content is None or response.content == "":
                print(Fore.RED + "Error: No valid response received from LLM." + Style.RESET_ALL)
                print(formatted_messages)
                state["refactored_code"] = "Error: No valid response received from LLM."
                raise ValueError("No valid response received from LLM.")
            refactored_code = response.content.strip()
            refactored_code = CodeTransformer.extract_java(refactored_code)

            print(Fore.GREEN + "Code transformation complete." + Style.RESET_ALL)
            state["refactored_code"] = refactored_code
            
        except Exception as e:
            print(Fore.RED + f"Error during code transformation: {e}" + Style.RESET_ALL)
            state["refactored_code"] = f"Error during transformation: {e}"
            
        return state

    def display_transformed_code(self, state: AgentState) -> AgentState:
        """
        Displays the refactored code.
        Args:
            state (AgentState): The current state of the workflow.
        Returns:
            AgentState: The state after displaying the code.
        """
        print("\nREFACTORED CODE")
        print("=" * 60)
        print(state.get("refactored_code", "No refactored code available."))
        print("=" * 60)
        return state
