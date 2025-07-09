"""
Enhanced workflow management using LangGraph
"""

from langgraph.graph import StateGraph
from langchain.tools.retriever import create_retriever_tool

from config.settings import settings
from ..llm_models import LLMCreator
from ..state import AgentState
from ..agents import AntipatternScanner


class CreateGraph:
    """Graph"""
    
    # Analysis prompt template
    GENERATE_PROMPT = (
        "You are a senior Java code reviewer with deep experience in detecting software design antipatterns. "
        "Below is the code to analyze:\n"
        "{code}\n\n"
        "Here is additional context from the codebase:\n"
        "{context}\n\n"
        "Your task is to:\n"
        "- Carefully analyze the code for Java antipatterns and design smells.\n"
        "- Return your analysis in JSON format with the following structure:\n\n"
        '{{\n'
        '  "total_antipatterns_found": 0,\n'
        '  "antipatterns_detected": [\n'
        '    {{\n'
        '      "name": "<antipattern name>",\n'
        '      "location": "<class/method name/line number>",\n'
        '      "description": "<brief description>",\n'
        '      "problem_explanation": "<why it\'s a problem>",\n'
        '      "suggested_refactor": "<refactoring suggestion>"\n'
        '    }}\n'
        '  ]\n'
        '}}\n\n'
        "Be thorough but concise. Ensure the JSON is valid and properly formatted. "
        "If no antipatterns are found, set total_antipatterns_found to 0 and antipatterns_detected to an empty array."
    )
    
    def __init__(self, db_manager, llm_model=None):
        llm_model = llm_model or settings.LLM_MODEL
        self.llm = LLMCreator.create_llm(
            provider=settings.LLM_PROVIDER,
            model_name=settings.LLM_MODEL
         )
        self.db_manager = db_manager
        retriever = self.db_manager.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            name="retrieve_Java_antipatterns",
            description="Search for Java anti-patterns in the codebase",
        )
         # Initialize agents
        self.agents = {
            'scanner': AntipatternScanner(retriever_tool, self.llm, self.GENERATE_PROMPT),
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
