"""
Agent responsible for refactoring code based on analysis.
"""
from ..state import AgentState
from colorama import Fore, Style


class CodeTransformer:
    """Code Transformer Agent"""

    def __init__(self, model, prompt: str):
        self.llm = model
        self.prompt = prompt

    def transform_code(self, state: AgentState) -> AgentState:
        print("--- TRANSFORMING CODE ---")
        original_code = state.get("code")
        strategy = state.get("refactoring_strategy_results")

        if not strategy:
            print("No valid strategy received. Skipping transformation.")
            state["refactored_code"] = "Transformation skipped due to missing strategy."
            return state

        print("Strategy received, proceeding with transformation.")

        try:
            formatted_prompt = self.prompt.format(
                strategy=strategy,
                code=original_code
            )
            
            response = self.llm.invoke(formatted_prompt)
            refactored_code = response.content.strip()

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
