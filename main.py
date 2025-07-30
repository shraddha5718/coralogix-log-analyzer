#!/usr/bin/env python3
"""
Coralogix Log Analyzer - Professional Edition

A sophisticated tool for analyzing Coralogix logs and detecting failures with remediation.
This tool provides both basic pattern-based and LLM-driven analysis capabilities.

Usage:
    python main.py analyze [OPTIONS] [QUERY]
    python main.py investigate [OPTIONS] [QUERY]
    python main.py health
    python main.py version
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.cli.main import main

if __name__ == "__main__":
    main() 