"""
MCP server implementation for Coralogix Log Analyzer.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

from ..config.environment import load_environment
from ..core.coralogix_client import CoralogixClient
from ..core.analyzer import BasicAnalyzer, LLMAnalyzer
from ..core.llm_client import LLMClient
from ..models.investigation_result import InvestigationResult
from .tools import CoralogixTools

logger = logging.getLogger(__name__)


class CoralogixMCPServer:
    """
    MCP server for Coralogix Log Analyzer.
    
    Provides tools for log analysis and failure detection through the MCP protocol.
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("coralogix-log-analyzer")
        self.settings = None
        self.coralogix_client = None
        self.basic_analyzer = None
        self.llm_analyzer = None
        self.tools = CoralogogixTools()
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="coralogix_analyze_logs",
                        description="Analyze Coralogix logs for failure patterns using basic pattern detection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "namespace": {
                                    "type": "string",
                                    "description": "Kubernetes namespace to analyze"
                                },
                                "pod_name": {
                                    "type": "string",
                                    "description": "Optional specific pod name"
                                },
                                "hours_back": {
                                    "type": "integer",
                                    "description": "Number of hours to look back",
                                    "default": 1
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Investigation query"
                                }
                            },
                            "required": ["namespace", "query"]
                        }
                    ),
                    Tool(
                        name="coralogix_investigate_logs",
                        description="Perform LLM-driven investigation of Coralogix logs",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "namespace": {
                                    "type": "string",
                                    "description": "Kubernetes namespace to analyze"
                                },
                                "pod_name": {
                                    "type": "string",
                                    "description": "Optional specific pod name"
                                },
                                "hours_back": {
                                    "type": "integer",
                                    "description": "Number of hours to look back",
                                    "default": 1
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Investigation query"
                                },
                                "max_iterations": {
                                    "type": "integer",
                                    "description": "Maximum LLM iterations",
                                    "default": 5
                                }
                            },
                            "required": ["namespace", "query"]
                        }
                    ),
                    Tool(
                        name="coralogix_fetch_logs",
                        description="Fetch logs from Coralogix for a namespace and optional pod",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "namespace": {
                                    "type": "string",
                                    "description": "Kubernetes namespace"
                                },
                                "pod_name": {
                                    "type": "string",
                                    "description": "Optional specific pod name"
                                },
                                "hours_back": {
                                    "type": "integer",
                                    "description": "Number of hours to look back",
                                    "default": 1
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of log entries",
                                    "default": 1000
                                }
                            },
                            "required": ["namespace"]
                        }
                    ),
                    Tool(
                        name="coralogix_search_errors",
                        description="Search for specific error patterns in logs",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "namespace": {
                                    "type": "string",
                                    "description": "Kubernetes namespace"
                                },
                                "search_pattern": {
                                    "type": "string",
                                    "description": "Pattern to search for"
                                },
                                "hours_back": {
                                    "type": "integer",
                                    "description": "Number of hours to look back",
                                    "default": 1
                                }
                            },
                            "required": ["namespace", "search_pattern"]
                        }
                    ),
                    Tool(
                        name="coralogix_get_pod_status",
                        description="Get pod status information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "namespace": {
                                    "type": "string",
                                    "description": "Kubernetes namespace"
                                },
                                "pod_name": {
                                    "type": "string",
                                    "description": "Optional specific pod name"
                                }
                            },
                            "required": ["namespace"]
                        }
                    ),
                    Tool(
                        name="coralogix_health_check",
                        description="Check Coralogix API connectivity",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            try:
                # Initialize components if not already done
                if not self.settings:
                    await self._initialize_components()
                
                # Route to appropriate tool handler
                if name == "coralogix_analyze_logs":
                    result = await self._analyze_logs(arguments)
                elif name == "coralogix_investigate_logs":
                    result = await self._investigate_logs(arguments)
                elif name == "coralogix_fetch_logs":
                    result = await self._fetch_logs(arguments)
                elif name == "coralogix_search_errors":
                    result = await self._search_errors(arguments)
                elif name == "coralogix_get_pod_status":
                    result = await self._get_pod_status(arguments)
                elif name == "coralogix_health_check":
                    result = await self._health_check(arguments)
                else:
                    result = {
                        "error": f"Unknown tool: {name}",
                        "success": False
                    }
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=self._format_result(result)
                        )
                    ]
                )
                
            except Exception as e:
                logger.error(f"Error in tool call {name}: {str(e)}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error: {str(e)}"
                        )
                    ]
                )
    
    async def _initialize_components(self):
        """Initialize Coralogix components."""
        try:
            self.settings = load_environment()
            self.coralogix_client = CoralogixClient(self.settings.coralogix)
            self.basic_analyzer = BasicAnalyzer(self.coralogix_client, self.settings)
            
            # Initialize LLM analyzer if OpenAI is configured
            if self.settings.llm.api_key:
                llm_client = LLMClient(self.settings.llm)
                self.llm_analyzer = LLMAnalyzer(self.coralogix_client, llm_client, self.settings)
            
            logger.info("MCP server components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    async def _analyze_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze logs using basic pattern detection."""
        try:
            query = arguments.get("query", "Check for errors")
            namespace = arguments["namespace"]
            pod_name = arguments.get("pod_name")
            hours_back = arguments.get("hours_back", 1)
            
            result = self.basic_analyzer.analyze(query, namespace, pod_name, hours_back)
            
            return {
                "success": True,
                "result": result.to_dict(),
                "summary": f"Analysis completed: {len(result.failure_patterns)} patterns detected"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _investigate_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Investigate logs using LLM-driven analysis."""
        try:
            if not self.llm_analyzer:
                return {
                    "success": False,
                    "error": "LLM analyzer not available. Please configure OpenAI API key."
                }
            
            query = arguments.get("query", "Why is my app failing?")
            namespace = arguments["namespace"]
            pod_name = arguments.get("pod_name")
            hours_back = arguments.get("hours_back", 1)
            max_iterations = arguments.get("max_iterations", 5)
            
            # Update max iterations
            self.settings.llm.max_iterations = max_iterations
            
            result = self.llm_analyzer.investigate(query, namespace, pod_name, hours_back)
            
            return {
                "success": True,
                "result": result.to_dict(),
                "summary": f"LLM investigation completed: {len(result.tool_results)} tools executed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fetch_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch logs from Coralogix."""
        try:
            namespace = arguments["namespace"]
            pod_name = arguments.get("pod_name")
            hours_back = arguments.get("hours_back", 1)
            limit = arguments.get("limit", 1000)
            
            logs = self.coralogix_client.fetch_logs(namespace, pod_name, hours_back, limit)
            
            return {
                "success": True,
                "logs_count": len(logs),
                "logs": [log.to_dict() for log in logs],
                "summary": f"Retrieved {len(logs)} log entries from namespace '{namespace}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_errors(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search for error patterns in logs."""
        try:
            namespace = arguments["namespace"]
            search_pattern = arguments["search_pattern"]
            hours_back = arguments.get("hours_back", 1)
            
            logs = self.coralogix_client.search_errors(namespace, search_pattern, hours_back)
            
            return {
                "success": True,
                "logs_count": len(logs),
                "logs": [log.to_dict() for log in logs],
                "summary": f"Found {len(logs)} logs matching pattern '{search_pattern}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_pod_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get pod status information."""
        try:
            namespace = arguments["namespace"]
            pod_name = arguments.get("pod_name")
            
            status = self.coralogix_client.get_pod_status(namespace, pod_name)
            
            return {
                "success": True,
                "status": status,
                "summary": f"Pod status retrieved for namespace '{namespace}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _health_check(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Check Coralogix API health."""
        try:
            is_healthy, message = self.coralogix_client.health_check()
            
            return {
                "success": True,
                "healthy": is_healthy,
                "message": message,
                "summary": f"Health check: {message}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_result(self, result: Dict[str, Any]) -> str:
        """Format result for MCP response."""
        if not result.get("success", False):
            return f"❌ Error: {result.get('error', 'Unknown error')}"
        
        # Format based on result type
        if "result" in result:
            # Analysis result
            analysis_result = result["result"]
            stats = analysis_result.get("statistics", {})
            
            formatted = f"✅ {result.get('summary', 'Analysis completed')}\n\n"
            formatted += f"📊 Summary:\n"
            formatted += f"  • Query: {stats.get('query', 'N/A')}\n"
            formatted += f"  • Duration: {stats.get('duration_seconds', 0):.2f} seconds\n"
            formatted += f"  • Patterns detected: {stats.get('total_patterns', 0)}\n"
            formatted += f"  • Critical patterns: {stats.get('critical_patterns', 0)}\n"
            formatted += f"  • Total errors: {stats.get('total_errors', 0)}\n"
            formatted += f"  • Total warnings: {stats.get('total_warnings', 0)}\n"
            
            # Add failure patterns
            failure_patterns = analysis_result.get("failure_patterns", [])
            if failure_patterns:
                formatted += f"\n🚨 Failure Patterns:\n"
                for i, pattern in enumerate(failure_patterns, 1):
                    formatted += f"  {i}. {pattern.get('pattern_name', 'Unknown')}\n"
                    formatted += f"     Severity: {pattern.get('severity', 'Unknown')}\n"
                    formatted += f"     Log entries: {pattern.get('total_entries', 0)}\n"
            
            # Add recommendations
            recommendations = analysis_result.get("recommendations", [])
            if recommendations:
                formatted += f"\n💡 Recommendations:\n"
                for i, rec in enumerate(recommendations, 1):
                    formatted += f"  {i}. {rec}\n"
            
            return formatted
        
        elif "logs" in result:
            # Log fetch result
            logs_count = result.get("logs_count", 0)
            return f"✅ {result.get('summary', f'Retrieved {logs_count} log entries')}"
        
        elif "status" in result:
            # Pod status result
            status = result["status"]
            return f"✅ {result.get('summary', 'Pod status retrieved')}\n\n{str(status)}"
        
        elif "healthy" in result:
            # Health check result
            healthy = result.get("healthy", False)
            message = result.get("message", "Unknown")
            status = "✅ Healthy" if healthy else "❌ Unhealthy"
            return f"{status}: {message}"
        
        else:
            return f"✅ {result.get('summary', 'Operation completed successfully')}"
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="coralogix-log-analyzer",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


async def main():
    """Main entry point for the MCP server."""
    server = CoralogixMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 