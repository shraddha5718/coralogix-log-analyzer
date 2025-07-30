# MCP Integration for Coralogix Log Analyzer

## 🚀 Model Context Protocol (MCP) Support

The Coralogix Log Analyzer now includes full MCP (Model Context Protocol) support, allowing other tools and AI assistants to interact with our log analysis capabilities through a standardized interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Integration Examples](#integration-examples)
- [Configuration](#configuration)
- [Development](#development)

## 🎯 Overview

MCP (Model Context Protocol) is a standardized protocol that allows AI assistants and other tools to interact with external services. Our MCP server provides access to all Coralogix Log Analyzer capabilities through a clean, well-defined interface.

### Key Benefits

- **🔌 Standardized Interface**: Consistent API for all log analysis operations
- **🤖 AI Assistant Integration**: Works with Claude, GPT-4, and other AI assistants
- **🛠️ Tool Integration**: Can be used by other development tools
- **📊 Rich Data**: Returns structured, formatted results
- **⚡ Async Support**: Non-blocking operations for better performance

## 🛠️ Installation

### 1. Install Dependencies

```bash
cd coralogix-log-analyzer
pip install -r requirements.txt
pip install -e .
```

### 2. Set Environment Variables

```bash
export CORALOGIX_API_KEY="your-coralogix-api-key"
export CORALOGIX_TEAM_HOSTNAME="your-team-name"
export CORALOGIX_DOMAIN="eu2.coralogix.com"
export OPENAI_API_KEY="your-openai-api-key"  # For LLM features
```

### 3. Run MCP Server

```bash
# Direct execution
python mcp_server.py

# Or using the installed command
coralogix-mcp
```

## 📖 Usage

### Basic MCP Server Usage

```bash
# Start the MCP server
python mcp_server.py
```

The server will start and listen for MCP protocol messages on stdin/stdout.

### Integration with AI Assistants

#### Claude Desktop Integration

1. **Install Claude Desktop** (if not already installed)
2. **Add MCP Server Configuration**:

```json
{
  "mcpServers": {
    "coralogix-analyzer": {
      "command": "python",
      "args": ["/path/to/coralogix-log-analyzer/mcp_server.py"],
      "env": {
        "CORALOGIX_API_KEY": "your-api-key",
        "CORALOGIX_TEAM_HOSTNAME": "your-team",
        "OPENAI_API_KEY": "your-openai-key"
      }
    }
  }
}
```

3. **Restart Claude Desktop**
4. **Use the tools**: Claude can now use all Coralogix analysis tools

#### Other AI Assistants

The MCP server works with any MCP-compatible client:

- **GPT-4 with MCP plugins**
- **Custom AI assistants**
- **Development tools with MCP support**

## 🛠️ Available Tools

### 1. `coralogix_analyze_logs`

**Basic pattern-based log analysis**

```json
{
  "name": "coralogix_analyze_logs",
  "arguments": {
    "namespace": "my-app",
    "query": "Check for errors",
    "pod_name": "my-pod",  // optional
    "hours_back": 2  // optional, default: 1
  }
}
```

**Returns**: Structured analysis with failure patterns and recommendations

### 2. `coralogix_investigate_logs`

**LLM-driven intelligent investigation**

```json
{
  "name": "coralogix_investigate_logs",
  "arguments": {
    "namespace": "production",
    "query": "Why is my app failing?",
    "pod_name": "app-pod",  // optional
    "hours_back": 4,  // optional, default: 1
    "max_iterations": 10  // optional, default: 5
  }
}
```

**Returns**: AI-powered analysis with detailed investigation results

### 3. `coralogix_fetch_logs`

**Fetch raw logs from Coralogix**

```json
{
  "name": "coralogix_fetch_logs",
  "arguments": {
    "namespace": "my-app",
    "pod_name": "my-pod",  // optional
    "hours_back": 1,  // optional, default: 1
    "limit": 1000  // optional, default: 1000
  }
}
```

**Returns**: List of log entries with metadata

### 4. `coralogix_search_errors`

**Search for specific error patterns**

```json
{
  "name": "coralogix_search_errors",
  "arguments": {
    "namespace": "my-app",
    "search_pattern": "exception",
    "hours_back": 2  // optional, default: 1
  }
}
```

**Returns**: Log entries matching the search pattern

### 5. `coralogix_get_pod_status`

**Get pod status information**

```json
{
  "name": "coralogix_get_pod_status",
  "arguments": {
    "namespace": "my-app",
    "pod_name": "my-pod"  // optional
  }
}
```

**Returns**: Pod status and health information

### 6. `coralogix_health_check`

**Check Coralogix API connectivity**

```json
{
  "name": "coralogix_health_check",
  "arguments": {}
}
```

**Returns**: API health status and connection details

## 🔧 Integration Examples

### Example 1: AI Assistant Analysis

**User**: "Can you analyze the logs for my production app and tell me what's wrong?"

**AI Assistant Response**:
```json
{
  "tool_calls": [
    {
      "name": "coralogix_investigate_logs",
      "arguments": {
        "namespace": "production",
        "query": "Analyze logs for errors and performance issues",
        "hours_back": 2,
        "max_iterations": 8
      }
    }
  ]
}
```

**Result**: Detailed analysis with failure patterns, root cause analysis, and remediation suggestions

### Example 2: Specific Error Search

**User**: "I'm seeing timeout errors in my app, can you find them?"

**AI Assistant Response**:
```json
{
  "tool_calls": [
    {
      "name": "coralogix_search_errors",
      "arguments": {
        "namespace": "my-app",
        "search_pattern": "timeout",
        "hours_back": 4
      }
    }
  ]
}
```

**Result**: All log entries containing "timeout" with context

### Example 3: Comprehensive Investigation

**User**: "My app is crashing, I need a full investigation"

**AI Assistant Response**:
```json
{
  "tool_calls": [
    {
      "name": "coralogix_health_check",
      "arguments": {}
    },
    {
      "name": "coralogix_investigate_logs",
      "arguments": {
        "namespace": "production",
        "query": "Investigate app crashes and provide detailed analysis",
        "hours_back": 6,
        "max_iterations": 10
      }
    }
  ]
}
```

**Result**: Health check followed by comprehensive LLM-driven investigation

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `CORALOGIX_API_KEY` | Coralogix API key | Yes | - |
| `CORALOGIX_TEAM_HOSTNAME` | Team hostname | Yes | - |
| `CORALOGIX_DOMAIN` | Coralogix domain | No | eu2.coralogix.com |
| `OPENAI_API_KEY` | OpenAI API key | Yes (for LLM) | - |
| `LLM_MODEL` | LLM model to use | No | gpt-4 |
| `LLM_TEMPERATURE` | LLM temperature | No | 0.1 |
| `LLM_MAX_TOKENS` | Max tokens for response | No | 1000 |
| `LLM_MAX_ITERATIONS` | Max investigation iterations | No | 5 |

### MCP Server Configuration

The MCP server can be configured through environment variables or by modifying the server code:

```python
# In src/mcp/server.py
class CoralogixMCPServer:
    def __init__(self):
        self.server = Server("coralogix-log-analyzer")
        # Add custom configuration here
```

## 🔍 Response Format

All MCP tool responses follow a consistent format:

### Success Response

```json
{
  "success": true,
  "data": {
    // Tool-specific data
  },
  "summary": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Detailed error message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Analysis Response Example

```json
{
  "success": true,
  "result": {
    "query": "Check for errors",
    "duration_seconds": 2.45,
    "failure_patterns": [
      {
        "pattern_name": "Application Crash",
        "severity": "ERROR",
        "description": "Detected application crashes",
        "total_entries": 5,
        "error_count": 5,
        "remediation_suggestions": [
          "Check application logs for detailed error messages",
          "Verify resource limits and memory allocation"
        ]
      }
    ],
    "recommendations": [
      "Review recent code deployments",
      "Check for dependency issues"
    ]
  },
  "summary": "Analysis completed: 1 patterns detected"
}
```

## 🛠️ Development

### Adding New Tools

1. **Define the tool schema** in `src/mcp/server.py`:

```python
Tool(
    name="your_tool_name",
    description="Tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
)
```

2. **Add the handler method**:

```python
async def _your_tool_handler(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle your tool call."""
    try:
        # Your tool logic here
        return {
            "success": True,
            "data": result,
            "summary": "Operation completed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

3. **Register the handler** in the `handle_call_tool` method:

```python
elif name == "your_tool_name":
    result = await self._your_tool_handler(arguments)
```

### Testing the MCP Server

```bash
# Test basic functionality
python mcp_server.py

# Test with specific tool calls
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python mcp_server.py
```

### Debugging

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python mcp_server.py
```

## 📊 Performance Considerations

- **Async Operations**: All MCP operations are async for better performance
- **Connection Pooling**: HTTP connections are reused
- **Caching**: Consider implementing result caching for repeated queries
- **Rate Limiting**: Respect Coralogix API rate limits

## 🔒 Security

- **API Key Management**: Store API keys securely
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: Sensitive information is not exposed in error messages
- **Access Control**: Consider implementing access control for production use

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install -e .

ENV CORALOGIX_API_KEY=your-key
ENV CORALOGIX_TEAM_HOSTNAME=your-team
ENV OPENAI_API_KEY=your-openai-key

CMD ["python", "mcp_server.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coralogix-mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: coralogix-mcp-server
  template:
    metadata:
      labels:
        app: coralogix-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/coralogix-mcp-server:latest
        env:
        - name: CORALOGIX_API_KEY
          valueFrom:
            secretKeyRef:
              name: coralogix-secrets
              key: api-key
        - name: CORALOGIX_TEAM_HOSTNAME
          value: "your-team"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secrets
              key: api-key
```

## 🎉 Conclusion

The MCP integration provides a powerful, standardized way to access Coralogix Log Analyzer capabilities from any MCP-compatible client. This enables:

- **🤖 AI Assistant Integration**: Seamless integration with Claude, GPT-4, and other AI assistants
- **🛠️ Tool Integration**: Use in development workflows and automation
- **📊 Rich Analysis**: Access to both basic and LLM-driven analysis
- **🔧 Extensibility**: Easy to add new tools and capabilities
- **⚡ Performance**: Async operations for better responsiveness

The MCP server transforms the Coralogix Log Analyzer into a powerful, accessible tool that can be integrated into any AI assistant or development workflow.

---

**Ready to analyze your Coralogix logs through MCP! 🚀** 