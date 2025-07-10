import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the AntiPattern_Remediator directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.llm_models.ollama_provider import OllamaProvider

@pytest.fixture
def provider():
    return OllamaProvider()


def test_get_provider_name(provider):
    assert provider.get_provider_name() == "ollama"


@patch('langchain_ollama.ChatOllama')
def test_create_llm(mock_chat_ollama, provider):
    mock_instance = MagicMock()
    mock_chat_ollama.return_value = mock_instance
    
    result = provider.create_llm("granite3.3:8b")
    
    mock_chat_ollama.assert_called_once_with(model="granite3.3:8b")
    assert result == mock_instance


@patch('langchain_ollama.OllamaEmbeddings')
def test_create_embedding(mock_embeddings, provider):
    mock_instance = MagicMock()
    mock_embeddings.return_value = mock_instance
    
    result = provider.create_embedding("nomic-embed-text:latest")
    
    mock_embeddings.assert_called_once_with(model="nomic-embed-text:latest")
    assert result == mock_instance
