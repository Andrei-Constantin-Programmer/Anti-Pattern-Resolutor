"""
State definitions for the antipattern analysis workflow
"""

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """State definition for passing data through the workflow"""
    code: str                                # Code to be analyzed
    language: Optional[str]                  # Language of the code (used by ExplainerAgent)
    context: Optional[str]                   # Context retrieved from knowledge base (scanner)
    trove_context: Optional[str]             # Context retrieved from the Anti-Pattern Trove (TinyDB/Chroma)
    antipatterns_scanner_results: Optional[Dict[str, Any]]   # Scanner output (structured)
    antipatterns_json: Optional[List[Dict[str, Any]]]        # Normalized list used by ExplainerAgent
    refactoring_strategy_results: Optional[Any]  # Strategy can be dict/list/str depending on agent
    refactored_code: Optional[str]               # Code after refactoring
    code_review_results: Optional[str]           # Code review results
    code_review_times: int                       # Number of times code has been reviewed
    msgs: List[Any]                              # Conversation history (LangChain BaseMessages)
    answer: Optional[str]                        # Final/aggregated analysis result

    explanation_response_raw: Optional[str]      # Raw LLM output from explainer
    explanation_json: Optional[Dict[str, Any]]   # Parsed JSON explanation
