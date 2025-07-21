"""
Enhanced workflow management using LangGraph
"""

from langgraph.graph import StateGraph
from langchain.tools.retriever import create_retriever_tool

from config.settings import settings
from ..llm_models import LLMCreator
from ..state import AgentState
from ..agents import AntipatternScanner
from ..prompt import PromptManager
from ..prompt.antipattern_prompts import ANTIPATTERN_SCANNER_KEY


class CreateGraph:
    """Graph"""
    
    def __init__(self, db_manager, llm_model=None):
        llm_model = llm_model or settings.LLM_MODEL
        self.llm = LLMCreator.create_llm(
            provider=settings.LLM_PROVIDER,
            model_name=settings.LLM_MODEL
         )
        self.db_manager = db_manager
        self.prompt_manager = PromptManager()
        retriever = self.db_manager.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            name="retrieve_Java_antipatterns",
            description="Search for Java anti-patterns in the codebase",
        )
        analysis_prompt = self.prompt_manager.get_prompt(ANTIPATTERN_SCANNER_KEY)
         # Initialize agents
        self.agents = {
            'scanner': AntipatternScanner(retriever_tool, self.llm, analysis_prompt),
        }
        self.workflow = self._build_graph()
    
    
    def _build_graph(self):
        """Build LangGraph workflow"""
            
        graph = StateGraph(AgentState)
        
        graph.add_node("retrieve_context", self.agents['scanner'].retrieve_context)
        graph.add_node("analyze_antipatterns", self.agents['scanner'].analyze_antipatterns)
        graph.add_node("display_results", self.agents['scanner'].display_results)
        
        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "analyze_antipatterns")
        graph.add_edge("analyze_antipatterns", "display_results")
        
        return graph.compile()
