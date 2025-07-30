"""
LLM client for OpenAI integration.
"""

import logging
import openai
from typing import List, Dict, Any, Optional
from ..config.settings import LLMConfig


logger = logging.getLogger(__name__)


class LLMClient:
    """
    Professional client for interacting with OpenAI LLM.
    
    Provides methods for intelligent analysis and decision-making.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM client.
        
        Args:
            config: LLM configuration settings
        """
        self.config = config
        self.client = openai.OpenAI(api_key=config.api_key)
    
    def test_connection(self) -> str:
        """
        Test the LLM connection with a simple call.
        
        Returns:
            str: Test response message
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10,
                temperature=0.1
            )
            return "Connection successful"
        except Exception as e:
            return f"Connection failed: {str(e)}"
    
    def analyze_and_decide(self, 
                          user_input: str, 
                          tool_results: List[Dict[str, Any]] = None,
                          available_tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze the current situation and decide on next actions.
        
        Args:
            user_input: The user's query or investigation request
            tool_results: Results from previous tool executions
            available_tools: List of available tools for the LLM to use
            
        Returns:
            Dict containing the LLM's analysis and decisions
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(available_tools)
            
            # Build user message
            user_message = self._build_user_message(user_input, tool_results)
            
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # Parse response
            llm_response = response.choices[0].message.content
            
            # Extract tool calls (simplified implementation)
            tool_calls = self._extract_tool_calls(llm_response)
            
            return {
                "response": llm_response,
                "tool_calls": tool_calls,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return {
                "response": f"Error during analysis: {str(e)}",
                "tool_calls": [],
                "success": False,
                "error": str(e)
            }
    
    def generate_summary(self, 
                        investigation_data: Dict[str, Any],
                        failure_patterns: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the investigation results.
        
        Args:
            investigation_data: Data from the investigation
            failure_patterns: Detected failure patterns
            
        Returns:
            str: Generated summary
        """
        try:
            prompt = f"""
            Based on the following investigation data, provide a comprehensive summary:
            
            Investigation Data: {investigation_data}
            Failure Patterns: {failure_patterns}
            
            Please provide:
            1. A clear summary of what was found
            2. The root cause analysis
            3. Recommended actions
            """
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def _build_system_prompt(self, available_tools: List[Dict[str, Any]] = None) -> str:
        """Build the system prompt for the LLM."""
        base_prompt = """
        You are an intelligent log analysis assistant. Your role is to:
        1. Analyze log data and identify failure patterns
        2. Decide which tools to use for further investigation
        3. Provide clear, actionable recommendations
        
        You have access to the following tools:
        """
        
        if available_tools:
            for tool in available_tools:
                base_prompt += f"- {tool['name']}: {tool['description']}\n"
        
        base_prompt += """
        When you need to use a tool, respond with:
        TOOL_CALL: tool_name
        PARAMETERS: {"param1": "value1", "param2": "value2"}
        
        Always provide clear reasoning for your decisions.
        """
        
        return base_prompt
    
    def _build_user_message(self, user_input: str, tool_results: List[Dict[str, Any]] = None) -> str:
        """Build the user message for the LLM."""
        message = f"User Query: {user_input}\n\n"
        
        if tool_results:
            message += "Previous tool results:\n"
            for result in tool_results:
                message += f"- {result.get('tool_name', 'Unknown')}: {result.get('summary', 'No data')}\n"
        
        return message
    
    def _extract_tool_calls(self, llm_response: str) -> List[Dict[str, Any]]:
        """Extract tool calls from LLM response (simplified implementation)."""
        tool_calls = []
        
        # Simple regex-based extraction (in a real implementation, you'd use function calling)
        lines = llm_response.split('\n')
        current_tool = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('TOOL_CALL:'):
                current_tool = line.replace('TOOL_CALL:', '').strip()
            elif line.startswith('PARAMETERS:') and current_tool:
                try:
                    import json
                    params_str = line.replace('PARAMETERS:', '').strip()
                    params = json.loads(params_str)
                    tool_calls.append({
                        "tool_name": current_tool,
                        "parameters": params
                    })
                    current_tool = None
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse parameters for tool {current_tool}")
                    current_tool = None
        
        return tool_calls 