"""
Enhanced workflow management using LangGraph
"""

from langgraph.graph import StateGraph, END
from langchain.tools.retriever import create_retriever_tool

from config.settings import settings
from src.core.prompt.prompt_manager import PromptManager
from .conditional_edges import ConditionalEdges
from ..llm_models import LLMCreator
from ..state import AgentState
from ..agents import AntipatternScanner
from ..agents import RefactorStrategist
from ..agents import CodeTransformer
from ..agents import CodeReviewerAgent

# Imports for LangSmith tracing
import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer

from colorama import Fore, Style


class CreateGraph:
    """Graph"""

    def __init__(self, db_manager, prompt_manager: PromptManager, retriever=None, llm_model=None):
        # LLM init
        llm_model = llm_model or settings.LLM_MODEL
        self.llm = LLMCreator.create_llm(
            provider=settings.LLM_PROVIDER,
            model_name=settings.LLM_MODEL,
            **settings.parameters
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
                print(
                    Fore.GREEN
                    + f"LangSmith tracing enabled for project: {settings.LANGSMITH_PROJECT} | provider - {settings.LLM_PROVIDER}"
                    + Style.RESET_ALL
                )
            except Exception as e:
                print(Fore.RED + f"Error initializing LangSmith: {e}" + Style.RESET_ALL)
                self.llm.callbacks = []

        # Trove plumbing
        self.db_manager = db_manager
        self.prompt_manager = prompt_manager
        self.conditional_edges = ConditionalEdges()
        retriever = self.db_manager.as_retriever()
        retriever_tool = create_retriever_tool(
            self.retriever,
            name="retrieve_Java_antipatterns",
            description="Search the Anti-Pattern Trove (Chroma/TinyDB) for Java anti-pattern definitions, symptoms, and refactoring guidance.",
        )

        # Agents
        self.agents = {
            'scanner': AntipatternScanner(retriever_tool, self.llm, self.prompt_manager),
            'strategist': RefactorStrategist(self.llm, self.prompt_manager),
            'transformer': CodeTransformer(self.llm, self.prompt_manager),
            'reviewer': CodeReviewerAgent(self.llm, self.prompt_manager),
        }

        # Build the LangGraph workflow
        self.workflow = self._build_graph()

    def _build_graph(self):
        """Build LangGraph workflow"""
        graph = StateGraph(AgentState)

        # Scanner: retrieve + analyze
        graph.add_node("retrieve_context", self.agents["scanner"].retrieve_context)
        graph.add_node("analyze_antipatterns", self.agents["scanner"].analyze_antipatterns)
        graph.add_node("display_antipatterns_results", self.agents["scanner"].display_antipatterns_results)

        graph.add_node("review_code", self.agents['reviewer'].review_code)
        graph.add_node("display_code_review_results", self.agents['reviewer'].display_code_review_results)

        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "analyze_antipatterns")
        graph.add_edge("analyze_antipatterns", "display_antipatterns_results")
        graph.add_edge("display_antipatterns_results", "strategize_refactoring")
        graph.add_edge("strategize_refactoring", "display_refactoring_results")
        graph.add_edge("display_refactoring_results", "transform_code")
        graph.add_edge("transform_code", "display_transformed_code")
        graph.add_edge("display_transformed_code", "review_code")
        graph.add_conditional_edges(
            "review_code",
            self.conditional_edges.code_review_condition,
            {
                "transform_code": "transform_code",
                "pass": "display_code_review_results",
            },
        )
        graph.add_edge("display_code_review_results", END)

        return graph.compile()
