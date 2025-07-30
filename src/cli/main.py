"""
Main CLI application for the Coralogix Log Analyzer.
"""

import sys
import logging
import re
from typing import Optional
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from ..config.environment import load_environment, validate_environment
from ..core.analyzer import BasicAnalyzer, LLMAnalyzer
from ..core.coralogix_client import CoralogixClient
from ..core.llm_client import LLMClient
from ..models.investigation_result import InvestigationResult


console = Console()


def parse_time_string(time_str: str) -> float:
    """
    Parse a time string like '1h', '30m', '2h30m' and convert to hours.
    
    Args:
        time_str: Time string in format like '1h', '30m', '2h30m'
        
    Returns:
        Time in hours as float
        
    Raises:
        ValueError: If the time string format is invalid
    """
    time_str = time_str.strip().lower()
    
    # Pattern to match hours and minutes
    pattern = r'^(\d*h)?(\d*m)?$'
    match = re.match(pattern, time_str)
    
    if not match:
        raise ValueError(f"Invalid time format: {time_str}. Use format like '1h', '30m', '2h30m'")
    
    hours = 0.0
    minutes = 0.0
    
    if match.group(1):  # hours
        hours = float(match.group(1)[:-1])  # Remove 'h'
    
    if match.group(2):  # minutes
        minutes = float(match.group(2)[:-1])  # Remove 'm'
    
    total_hours = hours + (minutes / 60.0)
    
    if total_hours <= 0:
        raise ValueError("Time must be greater than 0")
    
    return total_hours


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--log-level', default='INFO', help='Logging level')
def cli(debug: bool, log_level: str):
    """
    Coralogix Log Analyzer - Professional tool for analyzing Coralogix logs and detecting failures.
    
    This tool provides both basic pattern-based and LLM-driven analysis capabilities.
    """
    # Configure logging
    level = logging.DEBUG if debug else getattr(logging, log_level.upper())
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@cli.command()
@click.argument('query', required=False)
@click.option('--namespace', '-n', help='Kubernetes namespace to analyze')
@click.option('--pod', '-p', help='Specific pod name to analyze')
@click.option('--time-back', '-t', default='1h', help='Time to look back (e.g., 1h, 30m, 2h30m) (default: 1h)')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text', help='Output format')
def analyze(query: Optional[str], namespace: Optional[str], pod: Optional[str], 
           time_back: str, output: Optional[str], format: str):
    """
    Analyze logs using the basic pattern-based approach.
    
    This is a fast, predictable analysis method suitable for well-known failure patterns.
    """
    try:
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Load configuration
        settings = load_environment()
        
        # Initialize components
        coralogix_client = CoralogixClient(settings.coralogix, verify_ssl=settings.coralogix.verify_ssl)
        analyzer = BasicAnalyzer(coralogix_client, settings)
        
        # Health check
        console.print("🔍 Checking Coralogix connection...")
        is_healthy, message = coralogix_client.health_check()
        
        if not is_healthy:
            console.print(f"[red]❌ Connection failed: {message}[/red]")
            sys.exit(1)
        
        console.print(f"[green]✅ {message}[/green]")
        
        # Get query if not provided
        if not query:
            query = click.prompt("Enter your investigation query")
        
        # Get namespace if not provided
        if not namespace:
            namespace = click.prompt("Enter namespace to analyze")
        
        # Parse time string to hours
        try:
            hours_back = parse_time_string(time_back)
        except ValueError as e:
            console.print(f"[red]❌ Invalid time format: {str(e)}[/red]")
            sys.exit(1)
        
        # Run analysis
        console.print(f"\n🔍 Starting basic analysis for namespace '{namespace}'...")
        result = analyzer.analyze(query, namespace, pod, hours_back)
        
        # Display results
        display_results(result, format, output)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Analysis interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error during analysis: {str(e)}[/red]")
        if settings.debug:
            raise
        sys.exit(1)


@cli.command()
@click.argument('query', required=False)
@click.option('--namespace', '-n', help='Kubernetes namespace to analyze')
@click.option('--pod', '-p', help='Specific pod name to analyze')
@click.option('--time-back', '-t', default='1h', help='Time to look back (e.g., 1h, 30m, 2h30m) (default: 1h)')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--max-iterations', '-i', default=5, help='Maximum LLM iterations (default: 5)')
def investigate(query: Optional[str], namespace: Optional[str], pod: Optional[str],
               time_back: str, output: Optional[str], format: str, max_iterations: int):
    """
    Investigate logs using the LLM-driven approach.
    
    This is an intelligent, adaptive analysis method suitable for complex scenarios.
    """
    try:
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Load configuration
        settings = load_environment()
        settings.llm.max_iterations = max_iterations
        
        # Initialize components
        coralogix_client = CoralogixClient(settings.coralogix, verify_ssl=settings.coralogix.verify_ssl)
        llm_client = LLMClient(settings.llm)
        analyzer = LLMAnalyzer(coralogix_client, llm_client, settings)
        
        # Health check
        console.print("🔍 Checking Coralogix connection...")
        is_healthy, message = coralogix_client.health_check()
        
        if not is_healthy:
            console.print(f"[red]❌ Connection failed: {message}[/red]")
            sys.exit(1)
        
        console.print(f"[green]✅ {message}[/green]")
        
        # Get query if not provided
        if not query:
            query = click.prompt("Enter your investigation query")
        
        # Get namespace if not provided
        if not namespace:
            namespace = click.prompt("Enter namespace to analyze")
        
        # Parse time string to hours
        try:
            hours_back = parse_time_string(time_back)
        except ValueError as e:
            console.print(f"[red]❌ Invalid time format: {str(e)}[/red]")
            sys.exit(1)
        
        # Run investigation
        console.print(f"\n🔍 Starting LLM-driven investigation for namespace '{namespace}'...")
        result = analyzer.investigate(query, namespace, pod, hours_back)
        
        # Display results
        display_results(result, format, output)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Investigation interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error during investigation: {str(e)}[/red]")
        if settings.debug:
            raise
        sys.exit(1)


@cli.command()
def health():
    """Check the health of all configured services."""
    try:
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Load configuration
        settings = load_environment()
        
        # Check Coralogix
        console.print("🔍 Checking Coralogix connection...")
        coralogix_client = CoralogixClient(settings.coralogix, verify_ssl=settings.coralogix.verify_ssl)
        is_healthy, message = coralogix_client.health_check()
        
        if is_healthy:
            console.print(f"[green]✅ Coralogix: {message}[/green]")
        else:
            console.print(f"[red]❌ Coralogix: {message}[/red]")
        
        # Check LLM (if configured)
        console.print("🔍 Checking LLM connection...")
        try:
            llm_client = LLMClient(settings.llm)
            # Simple test call
            test_response = llm_client.test_connection()
            console.print(f"[green]✅ LLM: {test_response}[/green]")
        except Exception as e:
            console.print(f"[red]❌ LLM: {str(e)}[/red]")
        
        console.print("\n[green]✅ Health check completed[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during health check: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from .. import __version__
    console.print(f"Coralogix Log Analyzer v{__version__}")


def display_results(result: InvestigationResult, format: str, output: Optional[str]):
    """Display investigation results in the specified format."""
    
    if format == 'json':
        import json
        output_data = result.to_dict()
        
        if output:
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            console.print(f"[green]✅ Results saved to {output}[/green]")
        else:
            console.print(json.dumps(output_data, indent=2))
    
    else:  # text format
        console.print("\n" + "="*80)
        console.print(Panel.fit("🎯 Investigation Results", style="bold green"))
        console.print("="*80)
        
        # Summary
        stats = result.get_statistics()
        console.print(f"\n📊 Summary:")
        console.print(f"  • Query: {stats['query']}")
        console.print(f"  • Duration: {stats['duration_seconds']:.2f} seconds")
        console.print(f"  • Total patterns detected: {stats['total_patterns']}")
        console.print(f"  • Critical patterns: {stats['critical_patterns']}")
        console.print(f"  • Total errors: {stats['total_errors']}")
        console.print(f"  • Total warnings: {stats['total_warnings']}")
        console.print(f"  • Successful tools: {stats['successful_tools']}")
        console.print(f"  • Failed tools: {stats['failed_tools']}")
        
        # Failure patterns
        if result.failure_patterns:
            console.print(f"\n🚨 Failure Patterns Detected:")
            for i, pattern in enumerate(result.failure_patterns, 1):
                console.print(f"\n  {i}. {pattern.pattern_name}")
                console.print(f"     Severity: {pattern.severity}")
                console.print(f"     Description: {pattern.description}")
                console.print(f"     Log entries: {pattern.get_total_count()}")
                console.print(f"     Errors: {pattern.get_error_count()}")
                console.print(f"     Warnings: {pattern.get_warning_count()}")
                
                # Show sample log entries that match this pattern
                if pattern.log_entries:
                    console.print(f"     📝 Sample matching logs:")
                    # Show first 5 logs as examples
                    for i, log in enumerate(pattern.log_entries[:5], 1):
                        console.print(f"       {i}. [{log.level}] {log.timestamp}")
                        console.print(f"          {log.message[:200]}{'...' if len(log.message) > 200 else ''}")
                        if log.pod_name:
                            console.print(f"          Pod: {log.pod_name}")
                        if log.namespace:
                            console.print(f"          Namespace: {log.namespace}")
                        console.print()  # Empty line for readability
                    
                    if len(pattern.log_entries) > 5:
                        console.print(f"       ... and {len(pattern.log_entries) - 5} more entries")
                    console.print()
                
                if pattern.remediation_suggestions:
                    console.print(f"     💡 Remediation:")
                    for suggestion in pattern.remediation_suggestions:
                        console.print(f"       • {suggestion}")
        else:
            console.print("\n✅ No failure patterns detected.")
        
        # Summary and recommendations
        if result.summary:
            console.print(f"\n📋 Analysis Summary:")
            console.print(result.summary)
        
        if result.recommendations:
            console.print(f"\n💡 Recommendations:")
            for i, rec in enumerate(result.recommendations, 1):
                console.print(f"  {i}. {rec}")
        
        if output:
            # Save text output to file
            with open(output, 'w') as f:
                f.write("Coralogix Log Analyzer - Investigation Results\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Query: {stats['query']}\n")
                f.write(f"Duration: {stats['duration_seconds']:.2f} seconds\n\n")
                
                if result.summary:
                    f.write("Summary:\n")
                    f.write(result.summary + "\n\n")
                
                if result.recommendations:
                    f.write("Recommendations:\n")
                    for i, rec in enumerate(result.recommendations, 1):
                        f.write(f"{i}. {rec}\n")
            
            console.print(f"\n[green]✅ Results saved to {output}[/green]")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main() 