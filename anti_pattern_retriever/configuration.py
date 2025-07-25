import os
import platform
from dotenv import load_dotenv, set_key, unset_key
from pathlib import Path

import keyring

def _get_default_env_path() -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "ConfluenceExporter" / ".env"
    else:
        base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        return base / "confluence-exporter" / ".env"

ENV_PATH = _get_default_env_path()
ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
load_dotenv(dotenv_path=ENV_PATH, override=True)

KEYRING_SERVICE = "ConfluenceExporter"
KEYRING_KEY = "API_TOKEN"

class Settings:
    def __init__(self):
        load_dotenv(dotenv_path=ENV_PATH, override=True)

        self.confluence_base_url = os.getenv("CONFLUENCE_BASE_URL")
        self.api_username = os.getenv("CONFLUENCE_API_USERNAME")
        self.api_token = keyring.get_password(KEYRING_SERVICE, KEYRING_KEY)
        self.space_key = os.getenv("CONFLUENCE_SPACE_KEY")
        self.output_dir = os.getenv("OUTPUT_DIR", "out")
        self.page_limit = int(os.getenv("PAGE_LIMIT", "100"))

        if not self.output_dir:
            self.output_dir = "out"
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)


def _set_or_remove_env(key: str, value: str | None):
    if not ENV_PATH.exists():
        ENV_PATH.touch()
    if value is None:
        unset_key(str(ENV_PATH), key)
    else:
        set_key(str(ENV_PATH), key, value)

def set_confluence_base_url(value: str | None):
    _set_or_remove_env("CONFLUENCE_BASE_URL", value)

def set_api_username(value: str | None):
    _set_or_remove_env("CONFLUENCE_API_USERNAME", value)

def set_api_token(value: str | None):
    if value is None:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_KEY)
    else:
        keyring.set_password(KEYRING_SERVICE, KEYRING_KEY, value)

def set_space_key(value: str | None):
    _set_or_remove_env("CONFLUENCE_SPACE_KEY", value)

def set_output_dir(value: str | None):
    _set_or_remove_env("OUTPUT_DIR", value)

def set_page_limit(value: str | None):
    _set_or_remove_env("PAGE_LIMIT", value)
