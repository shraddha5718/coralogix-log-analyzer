"""
Tool result model for API operation results.
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ToolResult(BaseModel):
    """
    Represents the result of a tool execution.
    
    Attributes:
        tool_name: Name of the tool that was executed
        success: Whether the tool execution was successful
        data: The result data from the tool
        error: Error message if the tool failed
        execution_time: Time taken to execute the tool
        timestamp: When the tool was executed
        metadata: Additional metadata about the execution
    """
    
    tool_name: str = Field(..., description="Name of the tool")
    success: bool = Field(..., description="Whether execution was successful")
    data: str = Field(default="", description="Result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def is_successful(self) -> bool:
        """Check if the tool execution was successful."""
        return self.success and not self.error
    
    def has_data(self) -> bool:
        """Check if the tool returned any data."""
        return bool(self.data and self.data.strip())
    
    def get_summary(self) -> str:
        """Get a summary of the tool result."""
        if self.is_successful():
            return f"✅ {self.tool_name}: {len(self.data)} characters of data"
        else:
            return f"❌ {self.tool_name}: {self.error or 'Unknown error'}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool result to dictionary."""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        } 