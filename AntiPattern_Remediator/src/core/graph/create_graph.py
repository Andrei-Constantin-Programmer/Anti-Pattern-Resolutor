"""
Enhanced workflow management using LangGraph
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain.tools.retriever import create_retriever_tool

from config.settings import settings
from ..llm_models import LLMCreator
from ..state import AgentState
from ..agents import AntipatternScanner, RefactorStrategist, CodeTransformer, ExplainerAgent
from ..prompt import PromptManager

# Imports for LangSmith tracing
import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer

from colorama import Fore, Style


class CreateGraph:
    """Graph"""

    def __init__(self, db_manager, prompt_manager: PromptManager, llm_model: Optional[str] = None):
        model_name = llm_model or settings.LLM_MODEL  # <-- use the arg if provided
        self.llm = LLMCreator.create_llm(
            provider=settings.LLM_PROVIDER,
            model_name=model_name
        )

        # LangSmith integration (best-effort)
        if settings.LLM_PROVIDER in ["ollama", "vllm"] and getattr(settings, "LANGSMITH_ENABLED", False):
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
                # Some LangChain models accept callbacks on init; we set it directly here.
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

        # --- Defensive retriever tool creation ---
        retriever_tool = None
        try:
            retriever = self.db_manager.as_retriever()
            retriever_tool = create_retriever_tool(
                retriever,
                name="retrieve_Java_antipatterns",
                description="Search for Java anti-patterns in the codebase",
            )
        except Exception as e:
            print(Fore.YELLOW + f"Warning: could not create retriever tool ({e}). Scanner will run without retrieval." + Style.RESET_ALL)

        self.agents = {
            "scanner": AntipatternScanner(retriever_tool, self.llm, self.prompt_manager),
            "strategist": RefactorStrategist(self.llm, self.prompt_manager),
            "transformer": CodeTransformer(self.llm, self.prompt_manager),
            "explainer": ExplainerAgent(self.llm, self.prompt_manager),
        }
        self.workflow = self._build_graph()

    # Local node fns (tiny utilities)
    def _prepare_explainer_inputs(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure explainer always has the fields it needs."""
        state.setdefault("language", "Java")
        state.setdefault("context", "")

        # From scanner JSON (pick the first antipattern as headline)
        scan = state.get("antipatterns_scanner_results")
        if isinstance(scan, dict):
            ap_list = scan.get("antipatterns_detected") or []
            if ap_list and isinstance(ap_list, list) and isinstance(ap_list[0], dict):
                head = ap_list[0]
                state.setdefault("antipattern_name", head.get("name", "Unknown antipattern") or "Unknown antipattern")
                state.setdefault("antipattern_description", head.get("description", "") or "")

        # From strategy text (use as a suggested_fix / rationale)
        strat = state.get("refactoring_strategy_results")
        if strat and not state.get("suggested_fix"):
            # Hand the whole plan as a suggestion/rationale to the explainer
            state["suggested_fix"] = str(strat)

        # Normalize code fields
        state.setdefault("code", state.get("original_code", state.get("code", "")) or "")
        state.setdefault("refactored_code", state.get("refactored_code", "") or "")

        # Rationale (if transformer didn’t set it)
        state.setdefault("refactor_rationale", state.get("refactor_summary", "") or "")

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

        # Route to explainer before END (linear path only to avoid concurrent writes)
        graph.add_edge("display_transformed_code", "prepare_explainer_inputs")
        graph.add_edge("prepare_explainer_inputs", "explain_antipattern")
        # (removed) graph.add_edge("display_transformed_code", "explain_antipattern")
        graph.add_edge("explain_antipattern", "display_explanation")
        graph.add_edge("display_explanation", END)

        return graph.compile()
