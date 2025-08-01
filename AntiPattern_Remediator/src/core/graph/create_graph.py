"""
Enhanced workflow management using LangGraph
"""

from langgraph.graph import StateGraph, END
from langchain.tools.retriever import create_retriever_tool

from config.settings import settings
from ..llm_models import LLMCreator
from ..state import AgentState
from ..agents import AntipatternScanner
from ..agents import RefactorStrategist
from ..agents import CodeTransformer
from ..prompt import PromptManager


class CreateGraph:
    """Graph"""
    
    def __init__(self, db_manager, prompt_manager, llm_model=None):
        llm_model = llm_model or settings.LLM_MODEL
        self.llm = LLMCreator.create_llm(
            provider=settings.LLM_PROVIDER,
            model_name=settings.LLM_MODEL
         )
        self.db_manager = db_manager
        self.prompt_manager = prompt_manager
        retriever = self.db_manager.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            name="retrieve_Java_antipatterns",
            description="Search for Java anti-patterns in the codebase",
        )

        self.agents = {
            'scanner': AntipatternScanner(retriever_tool, self.llm, self.prompt_manager),
            'strategist': RefactorStrategist(self.llm, self.prompt_manager),
            'transformer': CodeTransformer(self.llm, self.prompt_manager)
        }
        self.workflow = self._build_graph()
    
    
    def _build_graph(self):
        """Build LangGraph workflow"""
            
        graph = StateGraph(AgentState)
        
        graph.add_node("retrieve_context", self.agents['scanner'].retrieve_context)
        graph.add_node("analyze_antipatterns", self.agents['scanner'].analyze_antipatterns)
        graph.add_node("display_antipatterns_results", self.agents['scanner'].display_antipatterns_results)

        graph.add_node("strategize_refactoring", self.agents['strategist'].strategize_refactoring)
        graph.add_node("display_refactoring_results", self.agents['strategist'].display_refactoring_results)
        
        graph.add_node("transform_code", self.agents['transformer'].transform_code)
        graph.add_node("display_transformed_code", self.agents['transformer'].display_transformed_code)

        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "analyze_antipatterns")
        graph.add_edge("analyze_antipatterns", "display_antipatterns_results")
        graph.add_edge("display_antipatterns_results", "strategize_refactoring")
        graph.add_edge("strategize_refactoring", "display_refactoring_results")
        graph.add_edge("display_refactoring_results", "transform_code")
        graph.add_edge("transform_code", "display_transformed_code")
        graph.add_edge("display_transformed_code", END)

        return graph.compile()
