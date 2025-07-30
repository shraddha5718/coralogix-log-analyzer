"""
Data models for the Coralogix Log Analyzer.
"""

from .log_entry import LogEntry
from .failure_pattern import FailurePattern
from .tool_result import ToolResult
from .investigation_result import InvestigationResult

__all__ = ["LogEntry", "FailurePattern", "ToolResult", "InvestigationResult"] 