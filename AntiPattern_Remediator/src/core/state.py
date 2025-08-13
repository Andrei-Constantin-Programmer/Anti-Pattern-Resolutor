"""
State definitions for the antipattern analysis workflow
"""

from typing import TypedDict, Optional, Dict, Any, Union

class AgentState(TypedDict, total=False):
    """State definition for passing data through the workflow"""

    # Inputs
    code: str
    context: Optional[str]
    language: Optional[str]

    # Scanner
    antipatterns_scanner_results: Optional[Union[Dict[str, Any], str]]
    antipattern_name: Optional[str]
    antipattern_description: Optional[str]

    # Strategist
    refactoring_strategy_results: Optional[Union[Dict[str, Any], str]]
    suggested_fix: Optional[str]

    # Transformer
    refactored_code: Optional[str]
    refactor_rationale: Optional[str]   # short bullet list / rationale

    # Explainer
    explanation_response_raw: Optional[str]
    explanation_json: Optional[Dict[str, Any]]

    # Misc
    answer: Optional[str]
