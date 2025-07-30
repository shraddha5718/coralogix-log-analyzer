"""
Log entry model for Coralogix log data.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class LogEntry(BaseModel):
    """
    Represents a log entry from Coralogix.
    
    Attributes:
        timestamp: ISO format timestamp of the log entry
        message: The log message content
        level: Log level (INFO, WARNING, ERROR)
        pod_name: Kubernetes pod name (optional)
        namespace: Kubernetes namespace (optional)
        container: Kubernetes container name (optional)
        metadata: Additional metadata from the log entry
    """
    
    timestamp: str = Field(..., description="ISO format timestamp")
    message: str = Field(..., description="Log message content")
    level: str = Field(default="INFO", description="Log level")
    pod_name: Optional[str] = Field(None, description="Kubernetes pod name")
    namespace: Optional[str] = Field(None, description="Kubernetes namespace")
    container: Optional[str] = Field(None, description="Kubernetes container name")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('level')
    def validate_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
        if v.upper() not in valid_levels:
            return "INFO"  # Default to INFO if invalid
        return v.upper()
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if not v or v.strip() == "":
            raise ValueError("Timestamp cannot be empty")
        
        try:
            # Handle various timestamp formats
            if v.endswith('Z'):
                # ISO format with Z suffix
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            elif '+' in v or '-' in v[-6:]:
                # ISO format with timezone offset
                datetime.fromisoformat(v)
            else:
                # Try parsing as ISO format without timezone
                datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {v}")
    
    def to_dict(self) -> dict:
        """Convert log entry to dictionary format."""
        return {
            "timestamp": self.timestamp,
            "message": self.message,
            "level": self.level,
            "pod_name": self.pod_name,
            "namespace": self.namespace,
            "container": self.container,
            "metadata": self.metadata
        }
    
    def is_error(self) -> bool:
        """Check if this is an error log entry."""
        return self.level in ["ERROR", "CRITICAL"]
    
    def is_warning(self) -> bool:
        """Check if this is a warning log entry."""
        return self.level == "WARNING"
    
    def contains_pattern(self, pattern: str) -> bool:
        """Check if the log message contains a specific pattern."""
        return pattern.lower() in self.message.lower() 