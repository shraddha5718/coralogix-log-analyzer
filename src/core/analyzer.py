"""
Analysis engines for the Coralogix Log Analyzer.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..config.settings import Settings
from ..models.log_entry import LogEntry
from ..models.failure_pattern import FailurePattern
from ..models.investigation_result import InvestigationResult
from ..models.tool_result import ToolResult
from .coralogix_client import CoralogixClient
from .llm_client import LLMClient


logger = logging.getLogger(__name__)


class BasicAnalyzer:
    """
    Basic pattern-based analyzer for log analysis.
    
    Provides fast, predictable analysis using predefined patterns.
    """
    
    def __init__(self, coralogix_client: CoralogixClient, settings: Settings):
        """
        Initialize the basic analyzer.
        
        Args:
            coralogix_client: Coralogix API client
            settings: Application settings
        """
        self.client = coralogix_client
        self.settings = settings
    
    def analyze(self, 
                query: str, 
                namespace: str, 
                pod_name: Optional[str] = None,
                hours_back: int = 1) -> InvestigationResult:
        """
        Perform basic pattern-based analysis.
        
        Args:
            query: User's investigation query
            namespace: Kubernetes namespace
            pod_name: Optional specific pod name
            hours_back: Number of hours to look back
            
        Returns:
            InvestigationResult with analysis findings
        """
        # Create investigation result
        result = InvestigationResult(query=query)
        
        try:
            # Fetch logs
            logs = self.client.fetch_logs(namespace, pod_name, hours_back)
            
            # Create tool result for log fetching
            tool_result = self.client.create_tool_result(
                tool_name="coralogix_fetch_logs",
                success=len(logs) > 0,
                data=f"Retrieved {len(logs)} log entries",
                error=None if len(logs) > 0 else "No logs found"
            )
            result.add_tool_result(tool_result)
            
            # Detect failure patterns
            failure_patterns = self.detect_failures(logs)
            
            # Add patterns to result
            for pattern in failure_patterns:
                result.add_failure_pattern(pattern)
            
            # Generate summary
            summary = self._generate_summary(failure_patterns, logs)
            recommendations = self._generate_recommendations(failure_patterns)
            
            # Complete the investigation
            result.complete(summary, recommendations)
            
        except Exception as e:
            logger.error(f"Error in basic analysis: {str(e)}")
            result.complete(
                f"Error during analysis: {str(e)}",
                ["Check your configuration and try again"]
            )
        
        return result
    
    def detect_failures(self, logs: List[LogEntry]) -> List[FailurePattern]:
        """
        Detect failure patterns in log entries.
        
        Args:
            logs: List of log entries to analyze
            
        Returns:
            List of detected failure patterns
        """
        patterns = []
        
        # Application crash pattern
        crash_pattern = self._detect_crash_pattern(logs)
        if crash_pattern:
            patterns.append(crash_pattern)
        
        # Resource exhaustion pattern
        resource_pattern = self._detect_resource_exhaustion(logs)
        if resource_pattern:
            patterns.append(resource_pattern)
        
        # Configuration error pattern
        config_pattern = self._detect_configuration_errors(logs)
        if config_pattern:
            patterns.append(config_pattern)
        
        # Network issue pattern
        network_pattern = self._detect_network_issues(logs)
        if network_pattern:
            patterns.append(network_pattern)
        
        return patterns
    
    def _detect_crash_pattern(self, logs: List[LogEntry]) -> Optional[FailurePattern]:
        """Detect application crash patterns."""
        crash_keywords = [
            "exception", "error", "crash", "panic", "fatal", "segmentation fault",
            "out of memory", "oom", "killed", "terminated"
        ]
        
        crash_logs = []
        for log in logs:
            if any(keyword in log.message.lower() for keyword in crash_keywords):
                crash_logs.append(log)
        
        if crash_logs:
            return FailurePattern(
                pattern_name="Application Crash",
                severity="ERROR",
                description="Detected application crashes or fatal errors",
                log_entries=crash_logs,
                remediation_suggestions=[
                    "Check application logs for detailed error messages",
                    "Verify resource limits and memory allocation",
                    "Review recent code deployments",
                    "Check for dependency issues"
                ]
            )
        
        return None
    
    def _detect_resource_exhaustion(self, logs: List[LogEntry]) -> Optional[FailurePattern]:
        """Detect resource exhaustion patterns."""
        resource_keywords = [
            "memory", "cpu", "disk", "space", "quota", "limit", "exceeded",
            "out of memory", "no space left", "resource exhausted"
        ]
        
        resource_logs = []
        for log in logs:
            if any(keyword in log.message.lower() for keyword in resource_keywords):
                resource_logs.append(log)
        
        if resource_logs:
            return FailurePattern(
                pattern_name="Resource Exhaustion",
                severity="WARNING",
                description="Detected resource exhaustion issues",
                log_entries=resource_logs,
                remediation_suggestions=[
                    "Increase resource limits for the application",
                    "Monitor resource usage patterns",
                    "Consider horizontal scaling",
                    "Optimize application resource usage"
                ]
            )
        
        return None
    
    def _detect_configuration_errors(self, logs: List[LogEntry]) -> Optional[FailurePattern]:
        """Detect configuration error patterns."""
        config_keywords = [
            "config", "configuration", "yaml", "json", "parse", "invalid",
            "missing", "required", "not found", "syntax error"
        ]
        
        config_logs = []
        for log in logs:
            if any(keyword in log.message.lower() for keyword in config_keywords):
                config_logs.append(log)
        
        if config_logs:
            return FailurePattern(
                pattern_name="Configuration Error",
                severity="ERROR",
                description="Detected configuration or parsing errors",
                log_entries=config_logs,
                remediation_suggestions=[
                    "Validate configuration files",
                    "Check YAML/JSON syntax",
                    "Verify required environment variables",
                    "Review configuration templates"
                ]
            )
        
        return None
    
    def _detect_network_issues(self, logs: List[LogEntry]) -> Optional[FailurePattern]:
        """Detect network issue patterns."""
        network_keywords = [
            "connection", "timeout", "network", "dns", "unreachable",
            "refused", "reset", "broken pipe", "connection lost"
        ]
        
        network_logs = []
        for log in logs:
            if any(keyword in log.message.lower() for keyword in network_keywords):
                network_logs.append(log)
        
        if network_logs:
            return FailurePattern(
                pattern_name="Network Issue",
                severity="WARNING",
                description="Detected network connectivity issues",
                log_entries=network_logs,
                remediation_suggestions=[
                    "Check network connectivity",
                    "Verify DNS resolution",
                    "Review firewall rules",
                    "Check service endpoints"
                ]
            )
        
        return None
    
    def _generate_summary(self, patterns: List[FailurePattern], logs: List[LogEntry]) -> str:
        """Generate a summary of the analysis."""
        if not patterns:
            return f"No failure patterns detected in {len(logs)} log entries."
        
        summary = f"Analysis of {len(logs)} log entries found {len(patterns)} failure patterns:\n"
        
        for pattern in patterns:
            summary += f"- {pattern.pattern_name}: {pattern.get_total_count()} matching entries\n"
        
        return summary
    
    def _generate_recommendations(self, patterns: List[FailurePattern]) -> List[str]:
        """Generate recommendations based on detected patterns."""
        recommendations = []
        
        for pattern in patterns:
            recommendations.extend(pattern.remediation_suggestions)
        
        if not recommendations:
            recommendations.append("Monitor logs for any new issues")
        
        return recommendations


class LLMAnalyzer:
    """
    LLM-driven analyzer for intelligent log analysis.
    
    Provides adaptive, AI-powered investigation capabilities.
    """
    
    def __init__(self, coralogix_client: CoralogixClient, llm_client: LLMClient, settings: Settings):
        """
        Initialize the LLM analyzer.
        
        Args:
            coralogix_client: Coralogix API client
            llm_client: LLM client for AI analysis
            settings: Application settings
        """
        self.client = coralogix_client
        self.llm_client = llm_client
        self.settings = settings
        self.max_iterations = settings.llm.max_iterations
    
    def investigate(self, 
                   query: str, 
                   namespace: str, 
                   pod_name: Optional[str] = None,
                   hours_back: int = 1) -> InvestigationResult:
        """
        Perform LLM-driven investigation.
        
        Args:
            query: User's investigation query
            namespace: Kubernetes namespace
            pod_name: Optional specific pod name
            hours_back: Number of hours to look back
            
        Returns:
            InvestigationResult with AI-driven analysis
        """
        # Create investigation result
        result = InvestigationResult(query=query)
        
        try:
            # Initialize investigation state
            current_iteration = 0
            tool_results = []
            available_tools = self._get_available_tools()
            
            # LLM-driven investigation loop
            while current_iteration < self.max_iterations:
                logger.info(f"LLM investigation iteration {current_iteration + 1}/{self.max_iterations}")
                
                # Get LLM analysis and decisions
                llm_response = self.llm_client.analyze_and_decide(
                    user_input=query,
                    tool_results=tool_results,
                    available_tools=available_tools
                )
                
                if not llm_response.get("success", False):
                    logger.error(f"LLM analysis failed: {llm_response.get('error', 'Unknown error')}")
                    break
                
                # Execute tool calls
                new_tool_results = self._execute_tool_calls(
                    llm_response.get("tool_calls", []),
                    namespace,
                    pod_name,
                    hours_back
                )
                
                tool_results.extend(new_tool_results)
                
                # Check if investigation should continue
                if not new_tool_results or all(not r.get("success", False) for r in new_tool_results):
                    logger.info("No more tools to execute, ending investigation")
                    break
                
                current_iteration += 1
            
            # Add tool results to investigation
            for tool_result in tool_results:
                result.add_tool_result(ToolResult(**tool_result))
            
            # Generate final summary using LLM
            summary = self.llm_client.generate_summary(
                investigation_data={"query": query, "namespace": namespace},
                failure_patterns=[]  # In a real implementation, you'd extract patterns from tool results
            )
            
            # Generate recommendations
            recommendations = [
                "Review the detailed analysis above",
                "Monitor the application for similar issues",
                "Consider implementing the suggested remediations"
            ]
            
            # Complete the investigation
            result.complete(summary, recommendations)
            
        except Exception as e:
            logger.error(f"Error in LLM investigation: {str(e)}")
            result.complete(
                f"Error during LLM investigation: {str(e)}",
                ["Check your LLM configuration and try again"]
            )
        
        return result
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for the LLM."""
        return [
            {
                "name": "coralogix_fetch_logs",
                "description": "Fetch logs from Coralogix for a namespace and optional pod"
            },
            {
                "name": "coralogix_search_errors",
                "description": "Search for specific error patterns in logs"
            },
            {
                "name": "coralogix_get_pod_status",
                "description": "Get pod status information"
            }
        ]
    
    def _execute_tool_calls(self, 
                           tool_calls: List[Dict[str, Any]],
                           namespace: str,
                           pod_name: Optional[str],
                           hours_back: int) -> List[Dict[str, Any]]:
        """Execute tool calls and return results."""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name")
            parameters = tool_call.get("parameters", {})
            
            try:
                if tool_name == "coralogix_fetch_logs":
                    logs = self.client.fetch_logs(
                        namespace=parameters.get("namespace", namespace),
                        pod_name=parameters.get("pod_name", pod_name),
                        hours_back=parameters.get("hours_back", hours_back)
                    )
                    
                    results.append({
                        "tool_name": tool_name,
                        "success": True,
                        "data": f"Retrieved {len(logs)} log entries",
                        "summary": f"Found {len(logs)} log entries"
                    })
                
                elif tool_name == "coralogix_search_errors":
                    search_pattern = parameters.get("pattern", "error")
                    logs = self.client.search_errors(
                        namespace=parameters.get("namespace", namespace),
                        search_pattern=search_pattern,
                        hours_back=parameters.get("hours_back", hours_back)
                    )
                    
                    results.append({
                        "tool_name": tool_name,
                        "success": True,
                        "data": f"Found {len(logs)} logs matching '{search_pattern}'",
                        "summary": f"Found {len(logs)} error logs"
                    })
                
                elif tool_name == "coralogix_get_pod_status":
                    status = self.client.get_pod_status(
                        namespace=parameters.get("namespace", namespace),
                        pod_name=parameters.get("pod_name", pod_name)
                    )
                    
                    results.append({
                        "tool_name": tool_name,
                        "success": True,
                        "data": str(status),
                        "summary": f"Pod status: {status.get('status', 'Unknown')}"
                    })
                
                else:
                    results.append({
                        "tool_name": tool_name,
                        "success": False,
                        "data": "",
                        "error": f"Unknown tool: {tool_name}"
                    })
                    
            except Exception as e:
                results.append({
                    "tool_name": tool_name,
                    "success": False,
                    "data": "",
                    "error": str(e)
                })
        
        return results 