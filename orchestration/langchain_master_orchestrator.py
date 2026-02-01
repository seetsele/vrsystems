"""
Compatibility shim: re-export canonical orchestrator implementation.

This module previously contained an alternative implementation. To avoid
duplication and drift, it now imports and re-exports the implementation from
`orchestration.langchain.master_orchestrator`.
"""

from orchestration.langchain.master_orchestrator import LangChainMasterOrchestrator

__all__ = ["LangChainMasterOrchestrator"]
