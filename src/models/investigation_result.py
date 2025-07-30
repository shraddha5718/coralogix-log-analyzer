"""
Investigation result model for analysis outcomes.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .failure_pattern import FailurePattern
from .tool_result import ToolResult


class InvestigationResult(BaseModel):
    """
    Represents the complete result of an investigation.
    
    Attributes:
        query: The original investigation query
        start_time: When the investigation started
        end_time: When the investigation completed
        duration: Duration of the investigation in seconds
        failure_patterns: List of detected failure patterns
        tool_results: List of tool execution results
        summary: Summary of the investigation
        recommendations: List of recommendations
        metadata: Additional metadata about the investigation
    """
    
    query: str = Field(..., description="Original investigation query")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Investigation start time")
    end_time: Optional[datetime] = Field(None, description="Investigation end time")
    duration: float = Field(default=0.0, description="Duration in seconds")
    failure_patterns: List[FailurePattern] = Field(default_factory=list, description="Detected failure patterns")
    tool_results: List[ToolResult] = Field(default_factory=list, description="Tool execution results")
    summary: str = Field(default="", description="Investigation summary")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def add_failure_pattern(self, pattern: FailurePattern) -> None:
        """Add a failure pattern to the investigation result."""
        self.failure_patterns.append(pattern)
    
    def add_tool_result(self, result: ToolResult) -> None:
        """Add a tool result to the investigation result."""
        self.tool_results.append(result)
    
    def complete(self, summary: str, recommendations: List[str]) -> None:
        """Mark the investigation as complete."""
        self.end_time = datetime.utcnow()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.summary = summary
        self.recommendations = recommendations
    
    def get_critical_patterns(self) -> List[FailurePattern]:
        """Get all critical failure patterns."""
        return [pattern for pattern in self.failure_patterns if pattern.is_critical()]
    
    def get_error_count(self) -> int:
        """Get total number of error log entries across all patterns."""
        return sum(pattern.get_error_count() for pattern in self.failure_patterns)
    
    def get_warning_count(self) -> int:
        """Get total number of warning log entries across all patterns."""
        return sum(pattern.get_warning_count() for pattern in self.failure_patterns)
    
    def get_successful_tools(self) -> List[ToolResult]:
        """Get all successfully executed tools."""
        return [result for result in self.tool_results if result.is_successful()]
    
    def get_failed_tools(self) -> List[ToolResult]:
        """Get all failed tool executions."""
        return [result for result in self.tool_results if not result.is_successful()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the investigation."""
        return {
            "query": self.query,
            "duration_seconds": self.duration,
            "total_patterns": len(self.failure_patterns),
            "critical_patterns": len(self.get_critical_patterns()),
            "total_errors": self.get_error_count(),
            "total_warnings": self.get_warning_count(),
            "successful_tools": len(self.get_successful_tools()),
            "failed_tools": len(self.get_failed_tools()),
            "recommendations_count": len(self.recommendations),
            "affected_pods": list(set(
                pod for pattern in self.failure_patterns 
                for pod in pattern.affected_pods
            )),
            "affected_namespaces": list(set(
                ns for pattern in self.failure_patterns 
                for ns in pattern.affected_namespaces
            ))
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert investigation result to dictionary."""
        return {
            "query": self.query,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "failure_patterns": [pattern.get_summary() for pattern in self.failure_patterns],
            "tool_results": [result.to_dict() for result in self.tool_results],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "statistics": self.get_statistics(),
            "metadata": self.metadata
        } 