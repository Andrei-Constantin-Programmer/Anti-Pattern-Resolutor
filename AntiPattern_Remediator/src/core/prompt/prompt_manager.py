from typing import Dict
from .antipattern_prompts import ANTIPATTERN_SCANNER_PROMPT, ANTIPATTERN_SCANNER_KEY

class PromptManager:
    def __init__(self):
        self._prompts: Dict[str, str] = {}  # Dictionary to hold prompt templates
        self._load_prompts()
    
    def _load_prompts(self):
        """Loads predefined prompts from the antipattern prompts module"""
        self._prompts[ANTIPATTERN_SCANNER_KEY] = ANTIPATTERN_SCANNER_PROMPT

    def get_prompt(self, prompt_name: str) -> str:
        """Get a prompt template by name"""
        if prompt_name not in self._prompts:
            raise ValueError(f"Undefined prompt: {prompt_name}")
        return self._prompts[prompt_name]
    
    def list_prompts(self) -> Dict[str, str]:
        """List all available prompts"""
        return self._prompts.copy()
