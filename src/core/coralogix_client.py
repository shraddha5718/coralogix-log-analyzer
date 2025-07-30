"""
Coralogix API client for log retrieval and analysis.
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urljoin

from ..config.settings import CoralogixConfig
from ..models.log_entry import LogEntry
from ..models.tool_result import ToolResult


logger = logging.getLogger(__name__)


class CoralogixClient:
    """
    Professional client for interacting with Coralogix API.
    
    Provides methods for fetching logs, searching patterns, and retrieving
    pod status information from Coralogix.
    """
    
    def __init__(self, config: CoralogixConfig, verify_ssl: bool = True):
        """
        Initialize the Coralogix client.
        
        Args:
            config: Coralogix configuration settings
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        # Fix the base URL structure - Coralogix uses different endpoint patterns
        if config.domain == "eu2.coralogix.com":
            self.base_url = "https://api.coralogix.com"
        elif "app.coralogix.us" in config.domain:
            # For custom app domains, use the standard API endpoint
            self.base_url = "https://api.coralogix.com"
        else:
            # For custom domains, try the standard pattern
            self.base_url = f"https://api.{config.domain}"
        
        # Use the specific logquery endpoint
        self.logquery_url = "https://api.us1.coralogix.com/api/v1/dataprime/query"
        
        self.session = requests.Session()
        
        # Update authentication - Coralogix uses different auth methods
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Use Bearer token authentication
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}"
        })
        
        # Configure SSL verification
        self.verify_ssl = verify_ssl
        if not verify_ssl:
            logger.warning("SSL verification is disabled. This is not recommended for production use.")
            # Suppress SSL warnings when verification is disabled
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def health_check(self) -> Tuple[bool, str]:
        """
        Check if Coralogix API is accessible.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Simple connectivity test - just check if the base URL is accessible
            try:
                response = self.session.get(
                    self.base_url,
                    timeout=10,
                    verify=self.verify_ssl
                )
                
                if response.status_code == 200:
                    return True, f"Connection successful - API base URL is accessible (status: {response.status_code})"
                elif response.status_code == 401:
                    return False, f"Authentication failed (401) - check your API key"
                elif response.status_code == 403:
                    return False, f"Access denied (403) - check your API key permissions. Response: {response.text[:200]}"
                else:
                    return False, f"Base URL returned status: {response.status_code}. {response.text[:200]}"
                    
            except requests.exceptions.RequestException as e:
                return False, f"Connection failed: {str(e)}"
                
        except requests.exceptions.SSLError as e:
            error_msg = f"SSL certificate verification failed: {str(e)}"
            if self.verify_ssl:
                error_msg += "\nTry setting verify_ssl=False for development, or check your domain configuration."
            return False, error_msg
        except requests.exceptions.RequestException as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def fetch_logs(self, 
                   namespace: str, 
                   pod_name: Optional[str] = None,
                   hours_back: int = 1,
                   limit: int = 1000) -> List[LogEntry]:
        """
        Fetch logs from Coralogix for specified namespace and pod.
        
        Args:
            namespace: Kubernetes namespace
            pod_name: Optional specific pod name
            hours_back: Number of hours to look back
            limit: Maximum number of log entries to fetch
            
        Returns:
            List of LogEntry objects
        """
        try:
            # Build query
            query_filters = [f'kubernetes.namespace_name:"{namespace}"']
            if pod_name:
                query_filters.append(f'kubernetes.pod_name:"{pod_name}"')
            
            query_string = " AND ".join(query_filters)
            
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            # DataPrime query payload formats using "logs" source with customer filter
            query_payloads = [
                # Format 1: Basic logs source query with customer filter
                {
                    "query": "source logs | filter customer_name == 'testhack'",
                    "startDate": start_time.isoformat() + "Z",
                    "endDate": end_time.isoformat() + "Z",
                    "limit": limit
                },
                # Format 2: Logs with customer and namespace filter
                {
                    "query": f"source logs | filter customer_name == 'testhack' | filter kubernetes.namespace_name == '{namespace}'",
                    "startDate": start_time.isoformat() + "Z",
                    "endDate": end_time.isoformat() + "Z",
                    "limit": limit
                },
                # Format 3: Logs with customer, namespace and error filter
                {
                    "query": f"source logs | filter customer_name == 'testhack' | filter kubernetes.namespace_name == '{namespace}' | filter severity == 'ERROR'",
                    "startDate": start_time.isoformat() + "Z",
                    "endDate": end_time.isoformat() + "Z",
                    "limit": limit
                }
            ]
            
            logger.info(f"Fetching logs for namespace '{namespace}' from {start_time} to {end_time}")
            
            for i, query_payload in enumerate(query_payloads):
                try:
                    logger.info(f"Trying query format {i+1}")
                    logger.info(f"Query payload: {json.dumps(query_payload, indent=2)}")
                    logger.info(f"Logquery URL: {self.logquery_url}")
                    
                    response = self.session.post(
                        self.logquery_url,
                        json=query_payload,
                        timeout=30,
                        verify=self.verify_ssl
                    )
                    
                    logger.info(f"Logquery endpoint response status: {response.status_code}")
                    logger.info(f"Response text length: {len(response.text)} characters")
                    if response.text:
                        logger.info(f"Response preview: {response.text[:100]}...")
                    else:
                        logger.info("Response is empty")
                    
                    if response.status_code == 200:
                        logger.info("Logquery successful")
                        break
                    elif response.status_code == 403:
                        logger.error(f"Logquery access forbidden. Response: {response.text[:200]}")
                        continue
                    elif response.status_code == 401:
                        logger.error(f"Logquery authentication failed. Response: {response.text[:200]}")
                        return []
                    else:
                        logger.error(f"Logquery failed with status {response.status_code}. Response: {response.text[:200]}")
                        continue
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request failed: {str(e)}")
                    continue
            else:
                logger.error("All query formats failed")
                return []
            
            # Parse response - handle different response formats
            response_text = response.text.strip()
            logs = []
            
            logger.info(f"Processing response of {len(response_text)} characters")
            
            # Try different parsing strategies
            parsing_strategies = [
                # Strategy 1: Try parsing as a single JSON object
                lambda: self._parse_single_json(response_text),
                # Strategy 2: Try parsing as streaming JSON (one object per line)
                lambda: self._parse_streaming_json(response_text),
                # Strategy 3: Try parsing as JSON array
                lambda: self._parse_json_array(response_text),
                # Strategy 4: Try parsing as CSV-like format
                lambda: self._parse_csv_like(response_text)
            ]
            
            for i, strategy in enumerate(parsing_strategies):
                try:
                    logger.info(f"Trying parsing strategy {i+1}")
                    strategy_logs = strategy()
                    if strategy_logs:
                        logs = strategy_logs
                        logger.info(f"Strategy {i+1} successful, found {len(logs)} logs")
                        break
                except Exception as e:
                    logger.warning(f"Strategy {i+1} failed: {str(e)}")
                    continue
            else:
                logger.error("All parsing strategies failed")
                logger.info(f"Raw response text (first 1000 chars): {response_text[:1000]}")
                return []
            
            logger.info(f"Retrieved {len(logs)} log entries from Coralogix")
            return logs
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL certificate verification failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching logs: {str(e)}")
            return []
    
    def _parse_single_json(self, response_text: str) -> List[LogEntry]:
        """Parse response as a single JSON object."""
        try:
            data = json.loads(response_text)
            logs = []
            
            # Handle different possible structures
            if isinstance(data, dict):
                if "data" in data:
                    # Data might be in a "data" field
                    entries = data["data"]
                elif "results" in data:
                    # Data might be in a "results" field
                    entries = data["results"]
                else:
                    # Try to treat the whole object as a single log entry
                    entries = [data]
            else:
                entries = [data]
            
            for entry in entries:
                log_entry = self._parse_log_entry(entry)
                if log_entry:
                    logs.append(log_entry)
            
            return logs
        except Exception as e:
            logger.debug(f"Single JSON parsing failed: {str(e)}")
            return []
    
    def _parse_streaming_json(self, response_text: str) -> List[LogEntry]:
        """Parse response as streaming JSON (one object per line)."""
        logs = []
        for line in response_text.split('\n'):
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    
                    # Handle Coralogix specific response structure
                    if "queryId" in entry:
                        # Skip queryId lines - they're metadata
                        continue
                    elif "result" in entry:
                        # Handle result structure
                        result_data = entry["result"]
                        if "results" in result_data:
                            for result_item in result_data["results"]:
                                # Parse the userData field which contains the actual log
                                user_data = result_item.get("userData", "")
                                if user_data:
                                    try:
                                        # userData is a JSON string, parse it
                                        log_data = json.loads(user_data)
                                        log_entry = self._parse_log_entry(log_data)
                                        if log_entry:
                                            logs.append(log_entry)
                                    except json.JSONDecodeError:
                                        # If userData is not valid JSON, try parsing the whole result_item
                                        log_entry = self._parse_log_entry(result_item)
                                        if log_entry:
                                            logs.append(log_entry)
                                else:
                                    # No userData, try parsing the whole result_item
                                    log_entry = self._parse_log_entry(result_item)
                                    if log_entry:
                                        logs.append(log_entry)
                        else:
                            # Single result item
                            log_entry = self._parse_log_entry(result_data)
                            if log_entry:
                                logs.append(log_entry)
                    else:
                        # Direct log entry
                        log_entry = self._parse_log_entry(entry)
                        if log_entry:
                            logs.append(log_entry)
                            
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue
        return logs
    
    def _parse_json_array(self, response_text: str) -> List[LogEntry]:
        """Parse response as a JSON array."""
        try:
            data = json.loads(response_text)
            if isinstance(data, list):
                logs = []
                for entry in data:
                    log_entry = self._parse_log_entry(entry)
                    if log_entry:
                        logs.append(log_entry)
                return logs
            return []
        except Exception as e:
            logger.debug(f"JSON array parsing failed: {str(e)}")
            return []
    
    def _parse_csv_like(self, response_text: str) -> List[LogEntry]:
        """Parse response as CSV-like format."""
        try:
            logs = []
            lines = response_text.split('\n')
            if len(lines) < 2:  # Need at least header and one data row
                return []
            
            # Assume first line is header
            headers = lines[0].split(',')
            
            for line in lines[1:]:
                if line.strip():
                    values = line.split(',')
                    if len(values) >= len(headers):
                        # Create a dict-like structure
                        entry = dict(zip(headers, values))
                        log_entry = self._parse_log_entry(entry)
                        if log_entry:
                            logs.append(log_entry)
            
            return logs
        except Exception as e:
            logger.debug(f"CSV-like parsing failed: {str(e)}")
            return []
    
    def search_errors(self, 
                     namespace: str, 
                     search_pattern: str,
                     hours_back: int = 1) -> List[LogEntry]:
        """
        Search for specific error patterns in logs.
        
        Args:
            namespace: Kubernetes namespace
            search_pattern: Pattern to search for
            hours_back: Number of hours to look back
            
        Returns:
            List of LogEntry objects matching the pattern
        """
        logs = self.fetch_logs(namespace, None, hours_back)
        error_logs = [
            log for log in logs 
            if search_pattern.lower() in log.message.lower()
        ]
        
        logger.info(f"Found {len(error_logs)} logs matching pattern '{search_pattern}'")
        return error_logs
    
    def get_pod_status(self, namespace: str, pod_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get pod status information (simulated for this implementation).
        
        Args:
            namespace: Kubernetes namespace
            pod_name: Optional specific pod name
            
        Returns:
            Dictionary with pod status information
        """
        # This is a simulated response - in a real implementation,
        # you would call Kubernetes API or Coralogix for pod status
        if pod_name:
            status_info = {
                "pod_name": pod_name,
                "namespace": namespace,
                "status": "Running",
                "containers_ready": "2/2",
                "restarts": 0
            }
        else:
            status_info = {
                "namespace": namespace,
                "total_pods": 5,
                "running_pods": 4,
                "pending_pods": 1,
                "failed_pods": 0
            }
        
        logger.info(f"Retrieved pod status for namespace '{namespace}'")
        return status_info
    
    def _parse_log_entry(self, result: Dict[str, Any]) -> Optional[LogEntry]:
        """
        Parse a log entry from Coralogix response.
        
        Args:
            result: Raw log entry from Coralogix API
            
        Returns:
            LogEntry object or None if parsing fails
        """
        try:
            # Extract timestamp and message - try different field names
            timestamp = result.get("timestamp", "")
            message = result.get("log", result.get("text", result.get("message", "")))
            
            # Handle empty timestamp - use current time if not provided
            if not timestamp or timestamp.strip() == "":
                timestamp = datetime.utcnow().isoformat() + "Z"
                logger.debug(f"Using current timestamp for log entry: {timestamp}")
            
            # Extract metadata - handle different metadata structures
            metadata = result.get("metadata", {})
            if isinstance(metadata, list):
                # Metadata might be a list of key-value pairs
                metadata_dict = {}
                for item in metadata:
                    if isinstance(item, dict) and "key" in item and "value" in item:
                        metadata_dict[item["key"]] = item["value"]
                metadata = metadata_dict
            
            # Extract Kubernetes fields from metadata
            pod_name = metadata.get("kubernetes.pod_name", metadata.get("pod_name"))
            namespace = metadata.get("kubernetes.namespace_name", metadata.get("namespace"))
            container = metadata.get("kubernetes.container_name", metadata.get("container"))
            
            # Also check direct fields in result
            if not pod_name:
                pod_name = result.get("kubernetes.pod_name", result.get("pod_name"))
            if not namespace:
                namespace = result.get("kubernetes.namespace_name", result.get("namespace"))
            if not container:
                container = result.get("kubernetes.container_name", result.get("container"))
            
            # Handle container field - it might be a dict with image info
            if isinstance(container, dict):
                if "image" in container and isinstance(container["image"], dict):
                    container = container["image"].get("name", str(container))
                else:
                    container = str(container)
            
            # Determine log level
            level = "INFO"
            if any(keyword in message.lower() for keyword in ["error", "exception", "failed"]):
                level = "ERROR"
            elif any(keyword in message.lower() for keyword in ["warn", "warning"]):
                level = "WARNING"
            
            # Validate required fields
            if not message or message.strip() == "":
                logger.debug("Skipping log entry with empty message")
                return None
            
            return LogEntry(
                timestamp=timestamp,
                message=message,
                level=level,
                pod_name=pod_name,
                namespace=namespace,
                container=container,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error parsing log entry: {str(e)}")
            logger.debug(f"Raw log entry data: {result}")
            return None
    
    def create_tool_result(self, 
                          tool_name: str, 
                          success: bool, 
                          data: str, 
                          error: Optional[str] = None,
                          execution_time: float = 0.0) -> ToolResult:
        """
        Create a ToolResult from an operation.
        
        Args:
            tool_name: Name of the tool
            success: Whether the operation was successful
            data: Result data
            error: Error message if failed
            execution_time: Time taken to execute
            
        Returns:
            ToolResult object
        """
        return ToolResult(
            tool_name=tool_name,
            success=success,
            data=data,
            error=error,
            execution_time=execution_time
        ) 