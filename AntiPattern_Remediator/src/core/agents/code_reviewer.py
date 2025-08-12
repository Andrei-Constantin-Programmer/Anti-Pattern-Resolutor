import difflib
from colorama import Fore, Style
from ..state import AgentState
from ..prompt import PromptManager
from langchain_core.messages import HumanMessage


class CodeReviewerAgent:
    """Code reviewer agent for managing code review tasks"""

    def __init__(self, model, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.llm = model

    def review_code(self, state: AgentState) -> AgentState:
        print("Reviewing code...")
        times = state.get("code_review_times", 0) + 1
        try:
            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.CODE_REVIEWER)
            
            msgs = []
            original_code=state['code']
            refactored_code=state['refactored_code']
            diff = difflib.unified_diff(
                original_code.splitlines(), 
                refactored_code.splitlines(), 
                fromfile='original', 
                tofile='modified',
                lineterm=""
            )
            diff_result = "\n".join(diff).__str__()
            formatted_messages = prompt_template.format_messages(
                diff_result=diff_result,
                refactoring_strategies=state['refactoring_strategy_results'],
                msgs=msgs
            )
            
            response = self.llm.invoke(formatted_messages)
            state["code_review_results"] = response.content if hasattr(response, 'content') else str(response)
            print(Fore.GREEN + "Code review completed successfully" + Style.RESET_ALL)
            review_feedback = f"Code Review Feedback (Round {times}): {state['code_review_results']}"
            state["msgs"].append(HumanMessage(content=review_feedback))
        except Exception as e:
            print(Fore.RED + f"Error during code review: {e}" + Style.RESET_ALL)
            state["code_review_results"] = f"Error occurred during code review: {e}"
        return state

    def display_code_review_results(self, state: AgentState) -> AgentState:
        """Display the code review results"""
        print("\nCODE REVIEW RESULTS")
        print("=" * 60)
        print(state.get("code_review_results", "No code review results available."))
        print("=" * 60)
        return state