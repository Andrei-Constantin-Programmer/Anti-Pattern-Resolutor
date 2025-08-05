from ..state import AgentState
from ..prompt import PromptManager
from colorama import Fore, Style


class RefactorStrategist:
    """Refactor strategist agent for managing code refactoring tasks"""
    
    def __init__(self, model, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.llm = model

    def strategize_refactoring(self, state: AgentState):
        print("Strategizing refactoring options...")
        try:
            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.REFACTOR_STRATEGIST)
            
            # Get historical messages from state, or use empty list if none exist
            msgs = state.get('msgs', [])

            formatted_messages = prompt_template.format_messages(
                code=state['code'],
                context=state['antipatterns_scanner_results'],
                msgs=msgs
            )
            
            response = self.llm.invoke(formatted_messages)
            state["refactoring_strategy_results"] = response.content if hasattr(response, 'content') else str(response)
            print(Fore.GREEN + "Refactoring strategy created successfully" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error during strategizing: {e}" + Style.RESET_ALL)
            state["refactoring_strategy_results"] = f"Error occurred during strategizing: {e}"
        return state
    
    def display_refactoring_results(self, state: AgentState):
        """Display the final refactoring strategy results"""
        print("\nREFACTORING STRATEGY RESULTS")
        print("=" * 60)
        print(state.get("refactoring_strategy_results", "No refactoring strategy available."))
        print("=" * 60)
        return state