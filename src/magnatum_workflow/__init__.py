"""Sanitized MAGNATUM multi-agent opportunity workflow."""

from .providers import OpenAICompatibleAssistant
from .storage import SQLiteStore
from .workflow import WorkflowEngine

__all__ = ["OpenAICompatibleAssistant", "SQLiteStore", "WorkflowEngine"]

