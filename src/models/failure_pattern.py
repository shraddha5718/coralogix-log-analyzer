"""
Failure pattern model for detected issues in log analysis.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .log_entry import LogEntry


class FailurePattern(BaseModel):
    """
    Represents a detected failure pattern in log analysis.
    
    Attributes:
        pattern_name: Name of the failure pattern
        severity: Severity level (ERROR, WARNING, INFO)
        description: Detailed description of the pattern
        log_entries: List of log entries that match this pattern
        remediation_suggestions: List of suggested remediation actions
        confidence_score: Confidence score for this pattern (0.0 to 1.0)
        affected_pods: List of affected pod names
        affected_namespaces: List of affected namespaces
    """
    
    pattern_name: str = Field(..., description="Name of the failure pattern")
    severity: str = Field(..., description="Severity level")
    description: str = Field(..., description="Detailed description")
    log_entries: List[LogEntry] = Field(default_factory=list, description="Matching log entries")
    remediation_suggestions: List[str] = Field(default_factory=list, description="Remediation suggestions")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score")
    affected_pods: List[str] = Field(default_factory=list, description="Affected pod names")
    affected_namespaces: List[str] = Field(default_factory=list, description="Affected namespaces")
    
    def add_log_entry(self, log_entry: LogEntry) -> None:
        """Add a log entry to this failure pattern."""
        self.log_entries.append(log_entry)
        
        # Update affected pods and namespaces
        if log_entry.pod_name and log_entry.pod_name not in self.affected_pods:
            self.affected_pods.append(log_entry.pod_name)
        
        if log_entry.namespace and log_entry.namespace not in self.affected_namespaces:
            self.affected_namespaces.append(log_entry.namespace)
    
    def get_error_count(self) -> int:
        """Get the count of error log entries."""
        return len([log for log in self.log_entries if log.is_error()])
    
    def get_warning_count(self) -> int:
        """Get the count of warning log entries."""
        return len([log for log in self.log_entries if log.is_warning()])
    
    def get_total_count(self) -> int:
        """Get the total count of log entries."""
        return len(self.log_entries)
    
    def is_critical(self) -> bool:
        """Check if this is a critical failure pattern."""
        return self.severity == "ERROR" and self.get_error_count() > 0
    
    def get_summary(self) -> dict:
        """Get a summary of this failure pattern."""
        return {
            "pattern_name": self.pattern_name,
            "severity": self.severity,
            "description": self.description,
            "total_entries": self.get_total_count(),
            "error_count": self.get_error_count(),
            "warning_count": self.get_warning_count(),
            "confidence_score": self.confidence_score,
            "affected_pods": self.affected_pods,
            "affected_namespaces": self.affected_namespaces,
            "remediation_count": len(self.remediation_suggestions)
        } 