"""
Antipattern scanner agent for detecting code smells and antipatterns
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from ..state import AgentState
from colorama import Fore, Style
from ..prompt import PromptManager
from sonarqube_tool import SonarQubeAPI


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
            api = SonarQubeAPI()
            issues = api.get_issues_for_file(project_key="commons-collections", file_path="src/main/java/org/apache/commons/collections4/collection/SynchronizedCollection.java")
            solutions = []
            for issue in issues["issues"]:
                solutions.append(api.get_rules_and_fix_method(rule_key=issue['rule']))
            state["context"] = {"sonarqube_issues": issues, "search_context": context, "solutions": solutions}
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
                context=state['context'].get('search_context', ''),
                sonarqube_issues=state['context'].get('solutions', ''),
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
    
