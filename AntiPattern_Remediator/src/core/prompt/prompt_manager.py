from typing import Optional, List
import yaml
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from config.settings import settings

class PromptManager:
    def __init__(self):
        self.ANTIPATTERN_SCANNER = "antipattern_scanner"
        self.REFACTOR_STRATEGIST = "refactor_strategist"
        self.CODE_TRANSFORMER = "code_transformer"
        self.EXPLAINER_AGENT = "explainer_agent"   # <-- NEW

        self.prompt_directory = settings.PROMPT_DIR
        self._prompt_cache = {}
        self._load_all_prompts()

    def _load_all_prompts(self) -> None:
        prompt_constants = [
            self.ANTIPATTERN_SCANNER,
            self.REFACTOR_STRATEGIST,
            self.CODE_TRANSFORMER,
            self.EXPLAINER_AGENT,  # <-- NEW
        ]
        for prompt_key in prompt_constants:
            filename = f"{prompt_key}.yaml"
            self._load_prompt_from_yaml(filename, prompt_key)
        print(f"Successfully loaded {len(self._prompt_cache)} prompts")
        print("=" * 60)

    def _load_prompt_from_yaml(self, filename: str, prompt_key: str) -> None:
        yaml_path = self.prompt_directory / filename
        if not yaml_path.exists():
            print(f"Warning: Prompt file {yaml_path} not found")
            return

        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if prompt_key not in config:
            print(f"Warning: Section '{prompt_key}' not found in {filename}")
            return

        prompt_config = config[prompt_key]

        # IMPORTANT: use from_messages(...)
        template = ChatPromptTemplate.from_messages([
            ("system", prompt_config.get("system", "")),
            ("user",   prompt_config.get("user", "")),
            MessagesPlaceholder("msgs"),
        ])
        self._prompt_cache[prompt_key] = template
        print(f"Loaded prompt '{prompt_key}' from {filename}")

    def get_prompt(self, prompt_key: str) -> Optional[ChatPromptTemplate]:
        if prompt_key not in self._prompt_cache:
            print(f"Warning: Prompt '{prompt_key}' not found in cache")
            return None
        return self._prompt_cache[prompt_key]

    # <-- NEW helper used by ExplainerAgent
    def render(self, prompt_key: str, **kwargs) -> list[dict]:
        tmpl = self.get_prompt(prompt_key)
        if tmpl is None:
            return []
        if "msgs" not in kwargs:
            kwargs["msgs"] = []
        return tmpl.format_messages(**kwargs)