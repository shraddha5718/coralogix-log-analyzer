"""
MCP tools implementation for Coralogix Log Analyzer.
"""

from typing import Dict, Any, List
from ..models.log_entry import LogEntry
from ..models.failure_pattern import FailurePattern
from ..models.investigation_result import InvestigationResult
from datetime import datetime


class CoralogixTools:
    """
    Tools for Coralogix Log Analyzer MCP server.
    
    Provides utility functions for tool operations and data processing.
    """
    
    def __init__(self):
        """Initialize the tools."""
        pass
    
    def format_log_entries(self, logs: List[LogEntry]) -> str:
        """
        Format log entries for display.
        
        Args:
            logs: List of log entries
            
        Returns:
            Formatted string representation
        """
        if not logs:
            return "No log entries found."
        
        formatted = f"Found {len(logs)} log entries:\n\n"
        
        for i, log in enumerate(logs[:10], 1):  # Show first 10 entries
            formatted += f"{i}. [{log.level}] {log.timestamp}\n"
            formatted += f"   Pod: {log.pod_name or 'N/A'}\n"
            formatted += f"   Message: {log.message[:200]}{'...' if len(log.message) > 200 else ''}\n\n"
        
        if len(logs) > 10:
            formatted += f"... and {len(logs) - 10} more entries\n"
        
        return formatted
    
    def format_failure_patterns(self, patterns: List[FailurePattern]) -> str:
        """
        Format failure patterns for display.
        
        Args:
            patterns: List of failure patterns
            
        Returns:
            Formatted string representation
        """
        if not patterns:
            return "No failure patterns detected."
        
        formatted = f"Detected {len(patterns)} failure patterns:\n\n"
        
        for i, pattern in enumerate(patterns, 1):
            formatted += f"{i}. {pattern.pattern_name}\n"
            formatted += f"   Severity: {pattern.severity}\n"
            formatted += f"   Description: {pattern.description}\n"
            formatted += f"   Log entries: {pattern.get_total_count()}\n"
            formatted += f"   Errors: {pattern.get_error_count()}\n"
            formatted += f"   Warnings: {pattern.get_warning_count()}\n"
            
            if pattern.remediation_suggestions:
                formatted += f"   Remediation:\n"
                for suggestion in pattern.remediation_suggestions:
                    formatted += f"     • {suggestion}\n"
            
            formatted += "\n"
        
        return formatted
    
    def format_investigation_result(self, result: InvestigationResult) -> str:
        """
        Format investigation result for display.
        
        Args:
            result: Investigation result
            
        Returns:
            Formatted string representation
        """
        stats = result.get_statistics()
        
        formatted = f"Investigation Results\n"
        formatted += f"=" * 50 + "\n\n"
        formatted += f"Query: {stats['query']}\n"
        formatted += f"Duration: {stats['duration_seconds']:.2f} seconds\n"
        formatted += f"Total patterns: {stats['total_patterns']}\n"
        formatted += f"Critical patterns: {stats['critical_patterns']}\n"
        formatted += f"Total errors: {stats['total_errors']}\n"
        formatted += f"Total warnings: {stats['total_warnings']}\n"
        formatted += f"Successful tools: {stats['successful_tools']}\n"
        formatted += f"Failed tools: {stats['failed_tools']}\n\n"
        
        # Add failure patterns
        if result.failure_patterns:
            formatted += self.format_failure_patterns(result.failure_patterns)
        
        # Add summary
        if result.summary:
            formatted += f"Summary:\n{result.summary}\n\n"
        
        # Add recommendations
        if result.recommendations:
            formatted += f"Recommendations:\n"
            for i, rec in enumerate(result.recommendations, 1):
                formatted += f"{i}. {rec}\n"
        
        return formatted
    
    def validate_arguments(self, arguments: Dict[str, Any], required: List[str]) -> bool:
        """
        Validate tool arguments.
        
        Args:
            arguments: Tool arguments
            required: List of required argument names
            
        Returns:
            True if valid, False otherwise
        """
        for arg in required:
            if arg not in arguments:
                return False
        return True
    
    def sanitize_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize and validate tool arguments.
        
        Args:
            arguments: Raw tool arguments
            
        Returns:
            Sanitized arguments
        """
        sanitized = {}
        
        # Copy string arguments
        for key in ["namespace", "pod_name", "query", "search_pattern"]:
            if key in arguments and arguments[key]:
                sanitized[key] = str(arguments[key]).strip()
        
        # Copy and validate integer arguments
        for key in ["hours_back", "limit", "max_iterations"]:
            if key in arguments:
                try:
                    value = int(arguments[key])
                    if value > 0:
                        sanitized[key] = value
                except (ValueError, TypeError):
                    pass
        
        return sanitized
    
    def create_error_response(self, error: str) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            error: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_success_response(self, data: Any, summary: str) -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            data: Response data
            summary: Summary message
            
        Returns:
            Success response dictionary
        """
        return {
            "success": True,
            "data": data,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        } 