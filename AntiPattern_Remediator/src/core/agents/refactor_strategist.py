from ..state import AgentState


class RefactorStrategist:
    """Refactor strategist agent for managing code refactoring tasks"""
    
    def __init__(self, model, prompt):
        self.prompt = prompt
        self.llm = model  # Add missing llm attribute

    def strategize_refactoring(self, state: AgentState):
        print("Strategizing refactoring options...")
        try:
            # Format the prompt with code and context
            formatted_prompt = self.prompt.format(
                code=state.get('code', ''),
                context=state.get('antipatterns_scanner_results', 'No antipatterns found')
            )
            response = self.llm.invoke(formatted_prompt)
            state["refactoring_strategy_results"] = response.content if hasattr(response, 'content') else str(response)
            print("   ✅ Refactoring strategy created successfully")  
        except Exception as e:
            print(f"   ❌ Error during strategizing: {e}")
            state["refactoring_strategy_results"] = f"Error occurred during strategizing: {e}"
        return state
    
    def display_refactoring_results(self, state: AgentState):
        """Display the final refactoring strategy results"""
        print("\n📋 REFACTORING STRATEGY RESULTS")
        print("=" * 60)
        print(state.get("refactoring_strategy_results", "No refactoring strategy available."))
        print("=" * 60)
        return state