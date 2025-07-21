from typing import Dict


class PromptManager:
    def __init__(self):
        self._prompts = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Loads predefined prompts from the antipattern prompts module"""
        from .antipattern_prompts import ANTIPATTERN_ANALYSIS_PROMPT
        
        self._prompts["antipattern_analysis"] = ANTIPATTERN_ANALYSIS_PROMPT
    
    def get_prompt(self, prompt_name: str) -> str:
        """Get a prompt template by name"""
        if prompt_name not in self._prompts:
            raise ValueError(f"Undefined prompt: {prompt_name}")
        return self._prompts[prompt_name]
    
    def list_prompts(self) -> Dict[str, str]:
        """List all available prompts"""
        return self._prompts.copy()
