from langgraph.graph import StateGraph
from typing import TypedDict, Optional

class AgentState(TypedDict):
    code: str
    context: Optional[str]
    answer: Optional[str]

def build_pipeline(retriever_tool, analyzer_fn, llm):
    def retrieve_context(state: AgentState) -> AgentState:
        query = f"Java antipatterns code analysis: {state['code'][:50]}"
        try:
            state["context"] = retriever_tool.invoke({"query": query})
        except Exception:
            state["context"] = "No additional context available due to retrieval error."
        return state

    def analyze_antipatterns(state: AgentState) -> AgentState:
        state["answer"] = analyzer_fn(llm, state["code"], state.get("context", ""))
        return state

    def display_results(state: AgentState) -> AgentState:
        print("\n🎯 Final Report:\n" + "-" * 50)
        print(state["answer"])
        return state

    graph = StateGraph(AgentState)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("analyze_antipatterns", analyze_antipatterns)
    graph.add_node("display_results", display_results)

    graph.set_entry_point("retrieve_context")
    graph.add_edge("retrieve_context", "analyze_antipatterns")
    graph.add_edge("analyze_antipatterns", "display_results")

    return graph.compile()
