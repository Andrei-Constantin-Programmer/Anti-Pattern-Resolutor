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
from ..prompt.antipattern_prompts import ANTIPATTERN_SCANNER_KEY

# Imports for LangSmith tracing
import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer

from ..prompt.refactoring_prompts import REFRACTOR_STRATEGIST_KEY
from ..prompt.code_transformer_prompt import CODE_TRANSFORMER_KEY

from colorama import Fore, Style

class CreateGraph:
    """Graph"""
    
    def __init__(self, db_manager, llm_model=None):
        llm_model = llm_model or settings.LLM_MODEL
        self.llm = LLMCreator.create_llm(
            provider=settings.LLM_PROVIDER,
            model_name=settings.LLM_MODEL
         )
                
        # LangSmith integration
        if settings.LLM_PROVIDER in ["ollama", "vllm"] and settings.LANGSMITH_ENABLED:
            try:
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                client = Client(
                    api_url=settings.LANGSMITH_ENDPOINT,
                api_key=settings.LANGSMITH_API_KEY,
                )
                tracer = LangChainTracer(
                    project_name=settings.LANGSMITH_PROJECT,
                    client=client
                )

                self.llm.callbacks = [tracer]
                print(Fore.GREEN + f"LangSmith tracing enabled for project: {settings.LANGSMITH_PROJECT} | provider - {settings.LLM_PROVIDER}" + Style.RESET_ALL)
            
            except Exception as e:
                print(Fore.RED + f"Error initializing LangSmith: {e}" + Style.RESET_ALL)
                self.llm.callbacks = []


        self.db_manager = db_manager
        self.prompt_manager = PromptManager()
        retriever = self.db_manager.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            name="retrieve_Java_antipatterns",
            description="Search for Java anti-patterns in the codebase",
        )
        analysis_prompt = self.prompt_manager.get_prompt(ANTIPATTERN_SCANNER_KEY)
        refactoring_prompt = self.prompt_manager.get_prompt(REFRACTOR_STRATEGIST_KEY)
        code_transformer_prompt = self.prompt_manager.get_prompt(CODE_TRANSFORMER_KEY)

         # Initialize agents
        self.agents = {
            'scanner': AntipatternScanner(retriever_tool, self.llm, analysis_prompt),
            'strategist': RefactorStrategist(self.llm, refactoring_prompt),
            'transformer': CodeTransformer(self.llm, code_transformer_prompt)
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
