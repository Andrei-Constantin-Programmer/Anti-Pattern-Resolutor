"""
Antipattern scanner agent for detecting code smells and antipatterns
"""

from typing import Dict, Any, Optional
import json, re
from ..state import AgentState
from colorama import Fore, Style
from ..prompt import PromptManager


def _parse_json_block(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse the first JSON block (fenced or raw)."""
    if not isinstance(text, str):
        return None
    blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    for cand in blocks + [text]:
        cand = cand.strip()
        if not cand:
            continue
        try:
            val = json.loads(cand)
            if isinstance(val, dict):
                return val
        except Exception:
            continue
    return None


class AntipatternScanner:
    """Antipattern scanner agent"""

    def __init__(self, tool, model, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.tool = tool
        self.llm = model

    def retrieve_context(self, state: AgentState):
        print("Retrieving context from knowledge base...")
        try:
            if not self.tool:
                raise RuntimeError("Retriever tool unavailable")
            # Create search query based on code snippet
            snippet = state.get("code", "")[:80].replace("\n", " ")
            search_query = f"Java antipatterns code analysis: {snippet}"
            # Use retriever_tool to get relevant context
            context = self.tool.invoke({"query": search_query})
            state["context"] = context
            print(Fore.GREEN + "Successfully retrieved relevant context" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"Context retrieval skipped/failed: {e}" + Style.RESET_ALL)
            state["context"] = state.get("context") or "No additional context available."
        return state

    def analyze_antipatterns(self, state: AgentState):
        print("Analyzing code for antipatterns...")
        try:
            prompt_template = self.prompt_manager.get_prompt(self.prompt_manager.ANTIPATTERN_SCANNER)
            if prompt_template is None:
                raise RuntimeError("Prompt 'antipattern_scanner' not loaded")

            msgs = state.get("msgs", [])
            formatted_messages = prompt_template.format_messages(
                code=state.get("code", ""),
                context=state.get("context", ""),
                msgs=msgs,
            )

            response = self.llm.invoke(formatted_messages)
            raw = getattr(response, "content", None) or str(response)

            # Prefer parsed dict; fall back to raw string if parsing fails
            parsed = _parse_json_block(raw)
            state["antipatterns_scanner_results"] = parsed if parsed else raw

            print(Fore.GREEN + "Analysis completed successfully" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error during analysis: {e}" + Style.RESET_ALL)
            state["antipatterns_scanner_results"] = f"Error occurred during analysis: {e}"
        return state

    def display_antipatterns_results(self, state: AgentState):
        """Display the final analysis results"""
        print("\nANTIPATTERN ANALYSIS RESULTS")
        print("=" * 60)
        res = state.get("antipatterns_scanner_results", "No analysis results available.")
        if isinstance(res, dict):
            try:
                print(json.dumps(res, indent=2, ensure_ascii=False))
            except Exception:
                print(str(res))
        else:
            print(res)
        print("=" * 60)
        return state
