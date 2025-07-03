"""
Antipattern scanner agent for detecting code smells and antipatterns
"""

from ..state import AgentState


class AntipatternScanner:
    """Antipattern scanner agent"""
    
    def __init__(self, tool, model, prompt):
        self.prompt = prompt
        self.tool = tool
        self.model = model  # Remove bind_tools call that's causing issues
        self.llm = model  # Add missing llm attribute

    def retrieve_context(self, state: AgentState):
        print("Retrieving context from knowledge base...")
        try:
            # Create search query based on code snippet
            search_query = f"Java antipatterns code analysis: {state['code'][:50]}"
            # Use retriever_tool to get relevant context
            context = self.tool.invoke({"query": search_query})
            state["context"] = context
            print(f"   ✅ Successfully retrieved relevant context")
        except Exception as e:
            print(f"   ❌ Error retrieving context: {e}")
            state["context"] = "No additional context available due to retrieval error."
        return state

    def analyze_antipatterns(self, state: AgentState):
        print("Analyzing code for antipatterns...")
        try:
            # Format the prompt with code and context
            formatted_prompt = self.prompt.format(
                code=state.get('code', ''),
                context=state.get('context', 'No context available')
            )
            response = self.llm.invoke(formatted_prompt)
            state["answer"] = response.content if hasattr(response, 'content') else str(response)
            print("   ✅ Analysis completed successfully")  
        except Exception as e:
            print(f"   ❌ Error during analysis: {e}")
            state["answer"] = f"Error occurred during analysis: {e}"
        return state
        
    def display_results(self, state: AgentState): 
        """Display the final analysis results"""
        print("\n📋 ANTIPATTERN ANALYSIS RESULTS")
        print("=" * 60)
        print(state.get("answer", "No analysis results available."))
        print("=" * 60)
        return state
    
