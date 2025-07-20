"""
Command-line interface for the Autonomous Agent-Based Testing Framework
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from .framework import TestingFramework
from .llm_config import Provider, llm_config
from litellm import completion


console = Console()


@click.group()
@click.version_option()
def cli():
    """Autonomous Agent-Based Testing Framework
    
    A comprehensive framework that uses AI agents to analyze, assess, and improve
    test quality through dependency mapping, mutation testing, and autonomous
    test generation.
    """
    pass


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--provider', type=click.Choice(['openai', 'azure_openai', 'anthropic', 'google', 'cohere']), 
              help='LLM provider to use (auto-detected if not specified)')
@click.option('--model', help='LLM model to use (auto-detected if not specified)')
@click.option('--no-generate', is_flag=True, help='Skip test generation')
@click.option('--no-mutation', is_flag=True, help='Skip mutation testing')
@click.option('--iterations', default=3, help='Maximum iterations for improvement')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def audit(project_path, provider, model, no_generate, no_mutation, iterations, verbose):
    """Run a full audit of the project's testing quality"""
    
    project_path = Path(project_path)
    
    if verbose:
        console.print(Panel(f"[bold blue]Starting Audit for: {project_path}", title="Autonomous Testing Framework"))
    
    try:
        # Convert provider string to enum if specified
        provider_enum = None
        if provider:
            provider_enum = Provider(provider)
        
        # Show provider info
        provider_info = llm_config.get_provider_info()
        if verbose:
            console.print(f"[blue]Using provider: {provider_info['default_provider']}")
            console.print(f"[blue]Available providers: {', '.join(provider_info['available_providers'])}")
        
        # Initialize framework
        framework = TestingFramework(
            project_path=project_path,
            provider=provider_enum,
            model=model
        )
        
        # Run audit
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose
        ) as progress:
            task = progress.add_task("Running audit...", total=None)
            
            audit_report = framework.run_full_audit(
                generate_tests=not no_generate,
                run_mutation_testing=not no_mutation,
                max_iterations=iterations
            )
            
            progress.update(task, completed=True)
        
        # Display results
        display_results(audit_report, framework)
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}")
        raise click.Abort()


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def analyze(project_path):
    """Analyze the current state of the project without making changes"""
    
    project_path = Path(project_path)
    
    try:
        # Initialize framework
        framework = TestingFramework(project_path=project_path)
        
        # Map codebase
        console.print("[bold blue]📊 Mapping Codebase Structure...")
        code_units = framework.code_mapper.map_codebase(framework.source_path)
        
        # Discover tests
        console.print("[bold blue]🔍 Discovering Existing Tests...")
        test_cases = framework.test_discovery.discover_tests(framework.test_path)
        
        # Assess quality
        console.print("[bold blue]📈 Assessing Test Quality...")
        metrics = framework.test_assessor.assess_quality(code_units, test_cases)
        
        # Display analysis
        display_analysis(code_units, test_cases, metrics)
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}")
        raise click.Abort()


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def generate(project_path):
    """Generate tests for uncovered code units"""
    
    project_path = Path(project_path)
    
    try:
        # Initialize framework
        framework = TestingFramework(project_path=project_path)
        
        # Map codebase
        console.print("[bold blue]📊 Mapping Codebase Structure...")
        code_units = framework.code_mapper.map_codebase(framework.source_path)
        
        # Discover existing tests
        console.print("[bold blue]🔍 Discovering Existing Tests...")
        test_cases = framework.test_discovery.discover_tests(framework.test_path)
        
        # Identify uncovered units
        uncovered_units = framework._identify_uncovered_units()
        
        console.print(f"[bold yellow]🎯 Found {len(uncovered_units)} uncovered units")
        
        # Generate tests for uncovered units
        generated_count = 0
        for unit_name in list(uncovered_units)[:10]:  # Limit to 10 units
            unit = framework._find_code_unit(unit_name)
            if unit:
                console.print(f"[blue]Generating tests for: {unit_name}")
                new_tests = framework.test_generator.generate_tests(unit, test_cases)
                
                if new_tests:
                    for test in new_tests:
                        judgment = framework.test_judge.judge_test(test, unit)
                        if judgment.get("overall_score", 0) >= 7.0:
                            framework._save_test_case(test)
                            generated_count += 1
                            console.print(f"[green]✅ Generated test for {unit_name}")
                        else:
                            console.print(f"[red]❌ Rejected test for {unit_name}")
        
        console.print(f"[bold green]🎉 Generated {generated_count} new test cases!")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}")
        raise click.Abort()


def display_results(audit_report, framework):
    """Display audit results in a formatted table"""
    
    console.print("\n[bold green]📊 Audit Results Summary")
    console.print("=" * 50)
    
    # Metrics comparison table
    table = Table(title="Metrics Comparison")
    table.add_column("Metric", style="cyan")
    table.add_column("Before", style="red")
    table.add_column("After", style="green")
    table.add_column("Delta", style="yellow")
    
    if audit_report.before_metrics and audit_report.after_metrics:
        before = audit_report.before_metrics
        after = audit_report.after_metrics
        
        table.add_row(
            "Coverage %",
            f"{before.coverage_percentage:.1f}%",
            f"{after.coverage_percentage:.1f}%",
            f"{after.coverage_percentage - before.coverage_percentage:+.1f}%"
        )
        
        table.add_row(
            "Total Tests",
            str(before.total_tests),
            str(after.total_tests),
            f"{after.total_tests - before.total_tests:+d}"
        )
        
        table.add_row(
            "Total Assertions",
            str(before.total_assertions),
            str(after.total_assertions),
            f"{after.total_assertions - before.total_assertions:+d}"
        )
        
        table.add_row(
            "Assertion Density",
            f"{before.assertion_density:.2f}",
            f"{after.assertion_density:.2f}",
            f"{after.assertion_density - before.assertion_density:+.2f}"
        )
    
    console.print(table)
    
    # Improvements
    if audit_report.improvements:
        console.print("\n[bold green]🎉 Improvements Made:")
        for improvement in audit_report.improvements:
            console.print(f"  ✅ {improvement}")
    
    # Recommendations
    if audit_report.recommendations:
        console.print("\n[bold yellow]💡 Recommendations:")
        for rec in audit_report.recommendations:
            console.print(f"  📝 {rec}")
    
    # Generated tests
    if audit_report.generated_tests:
        console.print(f"\n[bold blue]🤖 Generated {len(audit_report.generated_tests)} new test cases")


def display_analysis(code_units, test_cases, metrics):
    """Display analysis results"""
    
    console.print("\n[bold blue]📊 Codebase Analysis")
    console.print("=" * 40)
    
    # Code units summary
    code_table = Table(title="Code Units")
    code_table.add_column("Type", style="cyan")
    code_table.add_column("Count", style="green")
    
    types = {}
    for unit in code_units:
        types[unit.type.value] = types.get(unit.type.value, 0) + 1
    
    for unit_type, count in types.items():
        code_table.add_row(unit_type.title(), str(count))
    
    console.print(code_table)
    
    # Test summary
    test_table = Table(title="Test Cases")
    test_table.add_column("Type", style="cyan")
    test_table.add_column("Count", style="green")
    
    test_types = {}
    for test in test_cases:
        test_types[test.type.value] = test_types.get(test.type.value, 0) + 1
    
    for test_type, count in test_types.items():
        test_table.add_row(test_type.title(), str(count))
    
    console.print(test_table)
    
    # Quality metrics
    console.print(f"\n[bold yellow]📈 Quality Metrics:")
    console.print(f"  Coverage: {metrics.coverage_percentage:.1f}%")
    console.print(f"  Total Tests: {metrics.total_tests}")
    console.print(f"  Total Assertions: {metrics.total_assertions}")
    console.print(f"  Assertion Density: {metrics.assertion_density:.2f}")
    console.print(f"  Test Clarity Score: {metrics.test_clarity_score:.1f}/10")
    console.print(f"  Uncovered Units: {len(metrics.uncovered_units)}")
    
    if metrics.uncovered_units:
        console.print(f"\n[bold red]⚠️  Uncovered Units:")
        for unit in list(metrics.uncovered_units)[:10]:  # Show first 10
            console.print(f"  - {unit}")


if __name__ == '__main__':
    cli() 