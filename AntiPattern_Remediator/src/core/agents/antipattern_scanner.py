"""
Antipattern scanner agent for detecting code smells and antipatterns
"""

from ..state import AgentState
from colorama import Fore, Style
from ..prompt import PromptManager


class AntipatternScanner:
    """Antipattern scanner agent"""
    
    def __init__(self, tool, model, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.tool = tool
        self.llm = model

    def retrieve_context(self, state: AgentState):
        print("Retrieving context from knowledge base...")
        try:
            # Create search query based on code snippet
            search_query = f"Java antipatterns code analysis: {state['code'][:50]}"
            # Use retriever_tool to get relevant context
            context = self.tool.invoke({"query": search_query})
            state["context"] = context
            print(Fore.GREEN + f"Successfully retrieved relevant context" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error retrieving context: {e}" + Style.RESET_ALL)
            state["context"] = "No additional context available due to retrieval error."
        return state

    def analyze_antipatterns(self, state: AgentState):
        print("Analyzing code for antipatterns...")
        try:
            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.ANTIPATTERN_SCANNER)
            
            # Get historical messages from state, or use empty list if none exist
            msgs = state.get('msgs', [])

            formatted_messages = prompt_template.format_messages(
                code=state['code'],
                context=state['context'],
                msgs=msgs
            )
            
            response = self.llm.invoke(formatted_messages)
            state["antipatterns_scanner_results"] = response.content if hasattr(response, 'content') else str(response)
            print(Fore.GREEN + "Analysis completed successfully" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error during analysis: {e}" + Style.RESET_ALL)
            state["antipatterns_scanner_results"] = f"Error occurred during analysis: {e}"
        return state
        
    def display_antipatterns_results(self, state: AgentState): 
        """Display the final analysis results"""
        print("\nANTIPATTERN ANALYSIS RESULTS")
        print("=" * 60)
        print(state.get("antipatterns_scanner_results", "No analysis results available."))
        print("=" * 60)
        return state
    
