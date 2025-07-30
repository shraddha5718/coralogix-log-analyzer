"""
Environment configuration loader for the Coralogix Log Analyzer.
"""

import os
from typing import Optional
from .settings import Settings, CoralogixConfig, LLMConfig


def load_environment() -> Settings:
    """
    Load configuration from environment variables.
    
    Returns:
        Settings: Application settings loaded from environment.
        
    Raises:
        ValueError: If required environment variables are missing.
    """
    
    # Load Coralogix configuration
    coralogix_config = CoralogixConfig(
        api_key=os.getenv("CORALOGIX_API_KEY", ""),
        domain=os.getenv("CORALOGIX_DOMAIN", "eu2.coralogix.com"),
        team_hostname=os.getenv("CORALOGIX_TEAM_HOSTNAME", ""),
        verify_ssl=os.getenv("CORALOGIX_VERIFY_SSL", "true").lower() == "true"
    )
    
    # Load LLM configuration
    llm_config = LLMConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("LLM_MODEL", "gpt-4.1"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
        max_iterations=int(os.getenv("LLM_MAX_ITERATIONS", "5"))
    )
    
    # Load application settings
    settings = Settings(
        coralogix=coralogix_config,
        llm=llm_config,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        default_hours_back=int(os.getenv("DEFAULT_HOURS_BACK", "1")),
        max_log_entries=int(os.getenv("MAX_LOG_ENTRIES", "1000"))
    )
    
    return settings


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.
    
    Returns:
        bool: True if all required variables are set, False otherwise.
    """
    required_vars = [
        "CORALOGIX_API_KEY",
        "CORALOGIX_TEAM_HOSTNAME", 
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True 