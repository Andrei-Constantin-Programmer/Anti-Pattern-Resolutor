from ..state import AgentState
from ..prompt import PromptManager


class CodeReviewerAgent:
    """Code reviewer agent for managing code review tasks"""

    def __init__(self, model, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.llm = model

    def review_code(self, state: AgentState):
        print("Reviewing code...")
        times = state.get("code_review_times", 0) + 1
        try:
            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.CODE_REVIEWER)
            
            msgs = []

            formatted_messages = prompt_template.format_messages(
                original_code=state['code'],
                refactored_code=state['refactored_code'],
                refactoring_strategies=state['refactoring_strategy_results'],
                msgs=msgs
            )
            
            response = self.llm.invoke(formatted_messages)
            state["code_review_results"] = response.content if hasattr(response, 'content') else str(response)
            print("Code review completed successfully")
            state["code_review_times"] = times
            state["msgs"].append({
                "role": "assistant", 
                "content": state["code_review_results"]
            })
        except Exception as e:
            print(f"Error during code review: {e}")
            state["code_review_results"] = f"Error occurred during code review: {e}"
        return state

    def display_code_review_results(self, state: AgentState):
        """Display the code review results"""
        print("\nCODE REVIEW RESULTS")
        print("=" * 60)
        print(state.get("code_review_results", "No code review results available."))
        print("=" * 60)
        return state