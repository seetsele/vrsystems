"""
Compatibility shim: re-export canonical orchestrator implementation.

This module provides a small compatibility layer so older imports like
`from orchestration.langchain_master import LangChainMasterOrchestrator`
continue to work while the full implementation lives in
`orchestration.langchain.master_orchestrator`.
"""

from orchestration.langchain.master_orchestrator import LangChainMasterOrchestrator

__all__ = ["LangChainMasterOrchestrator"]
