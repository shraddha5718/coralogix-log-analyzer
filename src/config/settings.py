"""
Configuration settings for the Coralogix Log Analyzer.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator


class CoralogixConfig(BaseModel):
    """Configuration for Coralogix API connection."""
    
    api_key: str = Field(..., description="Coralogix API key")
    domain: str = Field(default="eu2.coralogix.com", description="Coralogix domain")
    team_hostname: str = Field(..., description="Team hostname")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Coralogix API key cannot be empty")
        return v.strip()
    
    @validator('team_hostname')
    def validate_team_hostname(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Team hostname cannot be empty")
        return v.strip()


class LLMConfig(BaseModel):
    """Configuration for LLM integration."""
    
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4.1", description="LLM model to use")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens for response")
    max_iterations: int = Field(default=5, ge=1, le=20, description="Maximum investigation iterations")
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("OpenAI API key cannot be empty")
        return v.strip()


class Settings(BaseModel):
    """Main application settings."""
    
    coralogix: CoralogixConfig
    llm: LLMConfig
    
    # Application settings
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Analysis settings
    default_hours_back: int = Field(default=1, ge=1, le=168, description="Default hours to look back")
    max_log_entries: int = Field(default=1000, ge=1, le=10000, description="Maximum log entries to fetch")
    
    class Config:
        env_prefix = "CORALOGIX_ANALYZER_" 