"""
Agent responsible for refactoring code based on analysis.
"""
from ..state import AgentState
from ..prompt import PromptManager


class CodeTransformer:
    """Code Transformer Agent"""

    def __init__(self, model, prompt_manager: PromptManager):
        self.llm = model
        self.prompt_manager = prompt_manager

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
            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.CODE_TRANSFORMER)
            
            # Get historical messages from state, or use empty list if none exist
            msgs = state.get('msgs', [])

            formatted_messages = prompt_template.format_messages(
                strategy=strategy,
                code=original_code,
                msgs=msgs
            )
            
            response = self.llm.invoke(formatted_messages)
            refactored_code = response.content.strip()
            
            print("Code transformation complete.")
            state["refactored_code"] = refactored_code
            
        except Exception as e:
            print(f"Error during code transformation: {e}")
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
