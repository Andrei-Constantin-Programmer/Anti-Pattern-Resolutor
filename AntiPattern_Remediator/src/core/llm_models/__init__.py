"""
LLM Models module

Simple factory pattern for creating LLM instances from different providers.
"""

from .create_llm import LLMCreator
from .create_embedding import EmbeddingCreator

__all__ = ["LLMCreator", "EmbeddingCreator"]