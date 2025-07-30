# Coralogix Log Analyzer - Professional Edition

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A sophisticated, professional tool for analyzing Coralogix logs and detecting failures with intelligent remediation suggestions. This tool provides both basic pattern-based and LLM-driven analysis capabilities.

## 🚀 Features

- **🔍 Dual Analysis Modes**: Both pattern-based and AI-driven analysis
- **🤖 LLM Integration**: GPT-4 powered intelligent investigation
- **📊 Rich Reporting**: Beautiful console output with detailed analysis
- **🔧 Professional CLI**: Command-line interface with comprehensive options
- **🔌 MCP Support**: Model Context Protocol integration for AI assistants
- **⚡ Fast & Efficient**: Optimized for production use
- **🛡️ Error Handling**: Robust error handling and validation
- **📈 Extensible**: Modular architecture for easy extension

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Coralogix API key with `DataQuerying` permission
- OpenAI API key (for LLM-driven analysis)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/coralogix-log-analyzer.git
cd coralogix-log-analyzer

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install with pip

```bash
pip install coralogix-log-analyzer
```

## 🚀 Quick Start

### 1. Set Environment Variables

```bash
export CORALOGIX_API_KEY="test"
export CORALOGIX_TEAM_HOSTNAME="test"
export CORALOGIX_DOMAIN="test"  # or your domain
export CORALOGIX_VERIFY_SSL="false"  # set to "false" for development if SSL issues occur
export OPENAI_API_KEY="test"  # for LLM analysis
```

### 2. Basic Analysis

```bash
# Analyze logs using pattern-based detection
python main.py analyze "Why is my app failing?" --namespace my-app

# Or use the installed command
coralogix-analyzer analyze "Why is my app failing?" --namespace my-app
```

### 3. LLM-Driven Investigation

```bash
# Use AI-powered investigation
python main.py investigate "What's causing the performance issues?" --namespace production

# Or use the installed command
coralogix-analyzer investigate "What's causing the performance issues?" --namespace production
```

### 4. Health Check

```bash
# Check service connectivity
python main.py health
```

### 5. MCP Server

```bash
# Start MCP server for AI assistant integration
python mcp_server.py

# Or use the installed command
coralogix-mcp
```

## 📖 Usage

### Command Line Interface

The tool provides a comprehensive CLI with multiple commands:

```bash
# Basic pattern-based analysis
coralogix-analyzer analyze [QUERY] [OPTIONS]

# LLM-driven investigation
coralogix-analyzer investigate [QUERY] [OPTIONS]

# Health check
coralogix-analyzer health

# MCP server
coralogix-mcp

# Version information
coralogix-analyzer version

### Analysis Options

```bash
# Basic analysis with options
coralogix-analyzer analyze "Check for errors" \
  --namespace my-app \
  --pod my-pod \
  --hours-back 2 \
  --output results.txt \
  --format json

# LLM investigation with options
coralogix-analyzer investigate "Why is the app slow?" \
  --namespace production \
  --hours-back 4 \
  --max-iterations 10 \
  --output investigation.json \
  --format json
```

### Output Formats

The tool supports multiple output formats:

- **Text**: Human-readable console output (default)
- **JSON**: Structured data for programmatic consumption

```bash
# Save results to file
coralogix-analyzer analyze "Check errors" --output results.txt

# Get JSON output
coralogix-analyzer investigate "Analyze failures" --format json --output results.json
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `CORALOGIX_API_KEY` | Coralogix API key | Yes | - |
| `CORALOGIX_TEAM_HOSTNAME` | Team hostname | Yes | - |
| `CORALOGIX_DOMAIN` | Coralogix domain | No | eu2.coralogix.com |
| `CORALOGIX_VERIFY_SSL` | SSL certificate verification | No | true |
| `OPENAI_API_KEY` | OpenAI API key | Yes (for LLM) | - |
| `LLM_MODEL` | LLM model to use | No | gpt-4.1 |
| `LLM_TEMPERATURE` | LLM temperature | No | 0.1 |
| `LLM_MAX_TOKENS` | Max tokens for response | No | 1000 |
| `LLM_MAX_ITERATIONS` | Max investigation iterations | No | 5 |
| `LOG_LEVEL` | Logging level | No | INFO |
| `DEBUG` | Enable debug mode | No | false |

### Configuration File

You can also use a `.env` file:

```bash
# .env
CORALOGIX_API_KEY=your-api-key
CORALOGIX_TEAM_HOSTNAME=your-team
OPENAI_API_KEY=your-openai-key
LLM_MODEL=gpt-4
DEBUG=true
```

## 🏗️ Architecture

### Project Structure

```
coralogix-log-analyzer/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── environment.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── log_entry.py
│   │   ├── failure_pattern.py
│   │   ├── tool_result.py
│   │   └── investigation_result.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── coralogix_client.py
│   │   ├── llm_client.py
│   │   └── analyzer.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   └── mcp/
│       ├── __init__.py
│       ├── server.py
│       └── tools.py
├── tests/
├── docs/
├── main.py
├── mcp_server.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── MCP_INTEGRATION.md
```

### Core Components

#### 1. Configuration Management (`src/config/`)
- **Settings**: Centralized configuration with validation
- **Environment**: Environment variable loading and validation

#### 2. Data Models (`src/models/`)
- **LogEntry**: Represents individual log entries
- **FailurePattern**: Detected failure patterns with metadata
- **ToolResult**: Results from tool executions
- **InvestigationResult**: Complete investigation outcomes

#### 3. Core Logic (`src/core/`)
- **CoralogixClient**: Professional API client for Coralogix
- **LLMClient**: OpenAI integration for AI-driven analysis
- **BasicAnalyzer**: Pattern-based analysis engine
- **LLMAnalyzer**: LLM-driven investigation engine

#### 4. CLI Interface (`src/cli/`)
- **Main CLI**: Professional command-line interface
- **Commands**: Analyze, investigate, health check, version

#### 5. MCP Integration (`src/mcp/`)
- **MCP Server**: Model Context Protocol server for AI assistant integration
- **Tools**: Standardized tools for log analysis and investigation

## 🔍 Analysis Modes

### 1. Basic Pattern-Based Analysis

Fast, predictable analysis using predefined patterns:

```python
from src.core.analyzer import BasicAnalyzer
from src.core.coralogix_client import CoralogixClient

# Initialize
client = CoralogixClient(config)
analyzer = BasicAnalyzer(client, settings)

# Analyze
result = analyzer.analyze("Check for errors", "my-namespace")
```

**Features:**
- ⚡ Fast execution (milliseconds)
- 🎯 Predictable results
- 💰 Low cost (no LLM calls)
- 🔧 Simple to understand and modify

### 2. LLM-Driven Investigation

Intelligent, adaptive analysis using AI:

```python
from src.core.analyzer import LLMAnalyzer
from src.core.llm_client import LLMClient

# Initialize
llm_client = LLMClient(config)
analyzer = LLMAnalyzer(client, llm_client, settings)

# Investigate
result = analyzer.investigate("Why is my app failing?", "my-namespace")
```

**Features:**
- 🤖 AI-driven analysis
- 🔄 Adaptive investigation
- 📊 Context-aware results
- 💡 Intelligent remediation

## 📊 API Reference

### CoralogixClient

```python
class CoralogixClient:
    def health_check(self) -> Tuple[bool, str]
    def fetch_logs(self, namespace: str, pod_name: Optional[str] = None, 
                   hours_back: int = 1, limit: int = 1000) -> List[LogEntry]
    def search_errors(self, namespace: str, search_pattern: str, 
                     hours_back: int = 1) -> List[LogEntry]
    def get_pod_status(self, namespace: str, pod_name: Optional[str] = None) -> Dict[str, Any]
```

### BasicAnalyzer

```python
class BasicAnalyzer:
    def analyze(self, query: str, namespace: str, pod_name: Optional[str] = None,
                hours_back: int = 1) -> InvestigationResult
    def detect_failures(self, logs: List[LogEntry]) -> List[FailurePattern]
```

### LLMAnalyzer

```python
class LLMAnalyzer:
    def investigate(self, query: str, namespace: str, pod_name: Optional[str] = None,
                   hours_back: int = 1) -> InvestigationResult
    def llm_analyze_and_decide(self, user_input: str, 
                               tool_results: List[ToolResult] = None) -> Tuple[str, List[Dict[str, Any]]]
```

## 🔧 Troubleshooting

### SSL Certificate Issues

If you encounter SSL certificate verification errors like:
```
❌ Connection failed: Connection failed: HTTPSConnectionPool(host='ng-api-http.jfrog-dev.app.coralogix.us', port=443): Max retries exceeded with url: /api/v1/health (Caused by SSLError(SSLCertVerificationError(1, "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch, certificate is not valid for 'ng-api-http.jfrog-dev.app.coralogix.us'. (_ssl.c:1028)")))
```

**Solutions:**

1. **For Development/Testing**: Disable SSL verification temporarily:
   ```bash
   export CORALOGIX_VERIFY_SSL="false"
   ```

2. **For Production**: Verify your domain configuration:
   ```bash
   # Check if the domain is correct
   export CORALOGIX_DOMAIN="eu2.coralogix.com"  # Use the default domain
   # or
   export CORALOGIX_DOMAIN="your-correct-domain.coralogix.com"
   ```

3. **Check your team hostname**:
   ```bash
   export CORALOGIX_TEAM_HOSTNAME="your-correct-team-hostname"
   ```

### Common Issues

- **"Missing required environment variables"**: Ensure all required environment variables are set
- **"Connection failed"**: Check your API key and domain configuration
- **"No logs found"**: Verify the namespace and time range settings

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_analyzer.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/coralogix-log-analyzer.git
cd coralogix-log-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pre-commit** for automated checks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔌 MCP Integration

For detailed information about the Model Context Protocol (MCP) integration, see [MCP_INTEGRATION.md](MCP_INTEGRATION.md).

## 🙏 Acknowledgments

- Built with inspiration from the HolmesGPT project
- Uses OpenAI's GPT models for intelligent analysis
- Integrates with Coralogix for log aggregation
- MCP integration for AI assistant compatibility

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/your-org/coralogix-log-analyzer/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/coralogix-log-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/coralogix-log-analyzer/discussions)

---

**Made with ❤️ for the DevOps community** 