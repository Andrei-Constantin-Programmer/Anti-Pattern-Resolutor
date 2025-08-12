import yaml
from config.settings import settings
from typing import Optional
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


class PromptManager:
    """Manager for handling prompt templates and configurations."""
    def __init__(self):
        # Prompt key constants, **same as YAML filenames**
        self.ANTIPATTERN_SCANNER = "antipattern_scanner"
        self.REFACTOR_STRATEGIST = "refactor_strategist" 
        self.CODE_TRANSFORMER = "code_transformer"
        self.EXPLAINER_AGENT = "explainer_agent"

        self.prompt_directory = settings.PROMPT_DIR
        # Initialize storage for prompt templates
        self._prompt_cache = {}
        # Load prompts on initialization
        self._load_all_prompts()
    
    def _load_all_prompts(self) -> None:
        """Load all prompt configurations from YAML files."""
        try:
            # Get all prompt constants and load corresponding files
            prompt_constants = [
                self.ANTIPATTERN_SCANNER,
                self.REFACTOR_STRATEGIST,
                self.CODE_TRANSFORMER,
            ]
            
            for prompt_key in prompt_constants:
                filename = f"{prompt_key}.yaml"
                self._load_prompt_from_yaml(filename, prompt_key)
            
            print(f"Successfully loaded {len(self._prompt_cache)} prompts")
            print("=" * 60)
        except Exception as e:
            print(f"Error loading prompts: {e}")
    
    def _load_prompt_from_yaml(self, filename: str, prompt_key: str) -> None:
        """Load a prompt configuration from a YAML file."""
        yaml_path = self.prompt_directory / filename
        
        if not yaml_path.exists():
            print(f"Warning: Prompt file {yaml_path} not found")
            return
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            if prompt_key not in config:
                print(f"Warning: Section '{prompt_key}' not found in {filename}")
                return
            
            prompt_config = config[prompt_key]
            # Create ChatPromptTemplate
            self._prompt_cache[prompt_key] = ChatPromptTemplate([
                ("system", prompt_config.get('system', '')),
                ("user", prompt_config.get('user', '')),
                MessagesPlaceholder("msgs")
            ])
            print(f"Loaded prompt '{prompt_key}' from {filename}")
            
        except Exception as e:
            print(f"Error loading prompt from {filename}: {e}")
    
    def get_prompt(self, prompt_key: str) -> Optional[ChatPromptTemplate]:
        if prompt_key not in self._prompt_cache:
            print(f"Warning: Prompt '{prompt_key}' not found in cache")
            return None
        
        return self._prompt_cache[prompt_key]