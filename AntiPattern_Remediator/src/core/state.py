"""
State definitions for the antipattern analysis workflow
"""

from typing import TypedDict, Optional


class AgentState(TypedDict):
    """State definition for passing data through the workflow"""
    code: str                    # Code to be analyzed
    context: Optional[str]       # Context retrieved from knowledge base
    answer: Optional[str]        # Analysis result
