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
from ..agents import ExplainerAgent
from ..prompt import PromptManager

# Imports for LangSmith tracing
import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer

from colorama import Fore, Style


class CreateGraph:
    """Graph"""

    def __init__(self, db_manager, prompt_manager: PromptManager, llm_model=None):
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
                print(
                    Fore.GREEN
                    + f"LangSmith tracing enabled for project: {settings.LANGSMITH_PROJECT} | provider - {settings.LLM_PROVIDER}"
                    + Style.RESET_ALL
                )
            except Exception as e:
                print(Fore.RED + f"Error initializing LangSmith: {e}" + Style.RESET_ALL)
                self.llm.callbacks = []

        self.db_manager = db_manager
        self.prompt_manager = prompt_manager

        retriever = self.db_manager.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            name="retrieve_Java_antipatterns",
            description="Search for Java anti-patterns in the codebase",
        )

        self.agents = {
            "scanner": AntipatternScanner(retriever_tool, self.llm, self.prompt_manager),
            "strategist": RefactorStrategist(self.llm, self.prompt_manager),
            "transformer": CodeTransformer(self.llm, self.prompt_manager),
            "explainer": ExplainerAgent(self.llm, self.prompt_manager),
        }
        self.workflow = self._build_graph()

    # Local node fns (tiny utilities)
    def _prepare_explainer_inputs(self, state: AgentState) -> AgentState:
        """
        Normalize/ensure keys for the ExplainerAgent to avoid KeyErrors and
        to provide best-effort defaults.
        """
        state.setdefault("language", "Java")
        state.setdefault("context", "")
        # If transformer provided a summary under a different key, normalize:
        if "refactor_summary" in state and not state.get("refactor_rationale"):
            state["refactor_rationale"] = state["refactor_summary"]

        # Ensure we have both original and refactored code fields present (even if empty)
        state.setdefault("code", state.get("original_code", ""))
        state.setdefault("refactored_code", state.get("transformed_code", state.get("refactored_code", "")))

        return state


    def _build_graph(self):
        """Build LangGraph workflow"""

        graph = StateGraph(AgentState)

        # Scanner
        graph.add_node("retrieve_context", self.agents["scanner"].retrieve_context)
        graph.add_node("analyze_antipatterns", self.agents["scanner"].analyze_antipatterns)
        graph.add_node("display_antipatterns_results", self.agents["scanner"].display_antipatterns_results)

        # Strategist
        graph.add_node("strategize_refactoring", self.agents["strategist"].strategize_refactoring)
        graph.add_node("display_refactoring_results", self.agents["strategist"].display_refactoring_results)

        # Transformer
        graph.add_node("transform_code", self.agents["transformer"].transform_code)
        graph.add_node("display_transformed_code", self.agents["transformer"].display_transformed_code)

        # Explainer
        graph.add_node("prepare_explainer_inputs", self._prepare_explainer_inputs)
        graph.add_node("explain_antipattern", self.agents["explainer"].explain_antipattern)
        graph.add_node("display_explanation", self.agents["explainer"].display_explanation)

        # Edges
        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "analyze_antipatterns")
        graph.add_edge("analyze_antipatterns", "display_antipatterns_results")
        graph.add_edge("display_antipatterns_results", "strategize_refactoring")
        graph.add_edge("strategize_refactoring", "display_refactoring_results")
        graph.add_edge("display_refactoring_results", "transform_code")
        graph.add_edge("transform_code", "display_transformed_code")

        # NEW: route to explainer before END
        graph.add_edge("display_transformed_code", "prepare_explainer_inputs")
        graph.add_edge("prepare_explainer_inputs", "explain_antipattern")
        graph.add_edge("explain_antipattern", "display_explanation")
        graph.add_edge("display_explanation", END)

        return graph.compile()
