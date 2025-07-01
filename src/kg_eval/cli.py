"""
Command Line Interface for KG-Eval framework.

This module provides a CLI for evaluating knowledge graphs using the KG-Eval framework.
"""

import click
import json
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .data_objects import KnowledgeGraph
from .evaluator import KGEvaluator
from .llm_referee import OpenAIReferee, AnthropicReferee


@click.group()
@click.version_option(version="0.1.0", prog_name="kg-eval")
def cli():
    """
    KG-Eval: A Framework for Evaluating LLM Knowledge Graph Construction Capabilities
    
    Evaluate knowledge graphs across four key dimensions:
    1. Scale & Richness
    2. Structural Integrity  
    3. Semantic Quality
    4. End-to-End Efficiency
    """
    pass


@cli.command()
@click.argument('kg_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), 
              help='Output path for the evaluation report')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'html', 'markdown']), 
              default='json',
              help='Output format for the report')
@click.option('--dimensions', '-d',
              multiple=True,
              type=click.Choice(['scale_richness', 'structural_integrity', 
                               'semantic_quality', 'efficiency']),
              help='Specific dimensions to evaluate (default: all)')
@click.option('--openai-key', envvar='OPENAI_API_KEY',
              help='OpenAI API key for semantic quality evaluation')
@click.option('--openai-base-url', envvar='OPENAI_BASE_URL',
              help='OpenAI base URL (for proxies or custom deployments)')
@click.option('--openai-model', default='gpt-4',
              help='OpenAI model to use (default: gpt-4)')
@click.option('--anthropic-key', envvar='ANTHROPIC_API_KEY', 
              help='Anthropic API key for semantic quality evaluation')
@click.option('--anthropic-base-url', envvar='ANTHROPIC_BASE_URL',
              help='Anthropic base URL (for proxies or custom deployments)')
@click.option('--anthropic-model', default='claude-3-sonnet-20240229',
              help='Anthropic model to use (default: claude-3-sonnet-20240229)')
@click.option('--sample-size', type=int, default=50,
              help='Sample size for LLM-based evaluations')
@click.option('--similarity-threshold', type=float, default=0.7,
              help='Threshold for entity similarity detection')
def evaluate(kg_file: str, 
             output: Optional[str],
             format: str,
             dimensions: tuple,
             openai_key: Optional[str],
             openai_base_url: Optional[str],
             openai_model: str,
             anthropic_key: Optional[str],
             anthropic_base_url: Optional[str],
             anthropic_model: str,
             sample_size: int,
             similarity_threshold: float):
    """
    Evaluate a knowledge graph from a JSON file.
    
    The KG_FILE should be a JSON file containing the knowledge graph data
    in the KG-Eval format (entities, relationships, source_texts).
    """
    click.echo(f"Loading knowledge graph from: {kg_file}")
    
    try:
        # Load knowledge graph
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)
        
        kg = KnowledgeGraph(**kg_data)
        click.echo(f"Loaded: {kg}")
        
    except Exception as e:
        click.echo(f"Error loading knowledge graph: {e}", err=True)
        return
    
    # Set up LLM referee if keys provided
    llm_referee = None
    if openai_key:
        llm_referee = OpenAIReferee(
            api_key=openai_key,
            model=openai_model,
            base_url=openai_base_url
        )
        click.echo(f"Using OpenAI referee (model: {openai_model})")
        if openai_base_url:
            click.echo(f"  Base URL: {openai_base_url}")
    elif anthropic_key:
        llm_referee = AnthropicReferee(
            api_key=anthropic_key,
            model=anthropic_model,
            base_url=anthropic_base_url
        )
        click.echo(f"Using Anthropic referee (model: {anthropic_model})")
        if anthropic_base_url:
            click.echo(f"  Base URL: {anthropic_base_url}")
    else:
        click.echo("No LLM referee configured - semantic quality metrics will be limited")
    
    # Set up evaluator
    evaluator = KGEvaluator(
        llm_referee=llm_referee,
        sample_size=sample_size,
        similarity_threshold=similarity_threshold
    )
    
    # Convert dimensions tuple to list
    include_dimensions = list(dimensions) if dimensions else None
    
    # Perform evaluation
    click.echo("Starting evaluation...")
    try:
        if output:
            # User specified output - use original behavior
            results = evaluator.evaluate_and_report(
                kg=kg,
                output_path=output,
                include_dimensions=include_dimensions,
                report_format=format
            )
        else:
            # No output specified - generate default JSON + HTML reports
            results = evaluator.evaluate(kg, include_dimensions=include_dimensions)
            
            # Generate default reports
            base_name = os.path.splitext(os.path.basename(kg_file))[0]
            json_output = f"{base_name}_evaluation_report.json"
            html_output = f"{base_name}_evaluation_report.html"
            
            click.echo("📄 Generating JSON report...")
            evaluator.report_generator.generate_json_report(results, json_output)
            click.echo(f"JSON report saved to: {json_output}")
            
            click.echo("🌐 Generating HTML report...")
            evaluator.report_generator.generate_html_report(results, html_output)
            click.echo(f"HTML report saved to: {html_output}")
        
        # Print summary to console
        summary = evaluator.get_evaluation_summary(results)
        
        click.echo("\n" + "="*50)
        click.echo("EVALUATION SUMMARY")
        click.echo("="*50)
        
        # Key metrics
        click.echo("\nKey Metrics:")
        for metric, value in summary["key_metrics"].items():
            if value is not None:
                if isinstance(value, float):
                    click.echo(f"  {metric.replace('_', ' ').title()}: {value:.4f}")
                else:
                    click.echo(f"  {metric.replace('_', ' ').title()}: {value}")
        
        # Recommendations
        if summary["recommendations"]:
            click.echo("\nRecommendations:")
            for i, rec in enumerate(summary["recommendations"], 1):
                click.echo(f"  {i}. {rec}")
        
        if output:
            click.echo(f"\nDetailed report saved to: {output}")
        else:
            click.echo(f"\nDetailed reports saved to:")
            click.echo(f"  - {base_name}_evaluation_report.json")
            click.echo(f"  - {base_name}_evaluation_report.html")
        
        click.echo("Evaluation completed successfully!")
        
    except Exception as e:
        click.echo(f"Error during evaluation: {e}", err=True)
        return


@cli.command()
@click.argument('kg_files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--names', '-n', multiple=True,
              help='Names for each knowledge graph (in order)')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output path for the comparison report')
@click.option('--openai-key', envvar='OPENAI_API_KEY',
              help='OpenAI API key for semantic quality evaluation')
@click.option('--openai-base-url', envvar='OPENAI_BASE_URL',
              help='OpenAI base URL (for proxies or custom deployments)')
@click.option('--openai-model', default='gpt-4',
              help='OpenAI model to use (default: gpt-4)')
@click.option('--anthropic-key', envvar='ANTHROPIC_API_KEY',
              help='Anthropic API key for semantic quality evaluation') 
@click.option('--anthropic-base-url', envvar='ANTHROPIC_BASE_URL',
              help='Anthropic base URL (for proxies or custom deployments)')
@click.option('--anthropic-model', default='claude-3-sonnet-20240229',
              help='Anthropic model to use (default: claude-3-sonnet-20240229)')
@click.option('--sample-size', type=int, default=50,
              help='Sample size for LLM-based evaluations')
def compare(kg_files: tuple,
            names: tuple,
            output: str,
            openai_key: Optional[str],
            openai_base_url: Optional[str],
            openai_model: str,
            anthropic_key: Optional[str],
            anthropic_base_url: Optional[str],
            anthropic_model: str,
            sample_size: int):
    """
    Compare multiple knowledge graphs.
    
    Provide multiple KG_FILES (JSON format) to compare their evaluation metrics.
    """
    if len(kg_files) < 2:
        click.echo("At least 2 knowledge graphs are required for comparison", err=True)
        return
    
    if names and len(names) != len(kg_files):
        click.echo("Number of names must match number of files", err=True)
        return
    
    click.echo(f"Comparing {len(kg_files)} knowledge graphs...")
    
    # Load knowledge graphs
    kgs = []
    kg_names = list(names) if names else []
    
    for i, kg_file in enumerate(kg_files):
        try:
            with open(kg_file, 'r', encoding='utf-8') as f:
                kg_data = json.load(f)
            
            kg = KnowledgeGraph(**kg_data)
            kgs.append(kg)
            
            if not kg_names:
                kg_names.append(f"KG_{os.path.basename(kg_file)}")
            
            click.echo(f"Loaded {kg_names[i]}: {kg}")
            
        except Exception as e:
            click.echo(f"Error loading {kg_file}: {e}", err=True)
            return
    
    # Set up LLM referee
    llm_referee = None
    if openai_key:
        llm_referee = OpenAIReferee(
            api_key=openai_key,
            model=openai_model,
            base_url=openai_base_url
        )
        click.echo(f"Using OpenAI referee (model: {openai_model})")
        if openai_base_url:
            click.echo(f"  Base URL: {openai_base_url}")
    elif anthropic_key:
        llm_referee = AnthropicReferee(
            api_key=anthropic_key,
            model=anthropic_model,
            base_url=anthropic_base_url
        )
        click.echo(f"Using Anthropic referee (model: {anthropic_model})")
        if anthropic_base_url:
            click.echo(f"  Base URL: {anthropic_base_url}")
    
    # Set up evaluator
    evaluator = KGEvaluator(llm_referee=llm_referee, sample_size=sample_size)
    
    # Perform comparison
    try:
        comparison_results = evaluator.compare_knowledge_graphs(
            kgs=kgs,
            kg_names=kg_names,
            output_path=output
        )
        
        # Print comparison summary
        summary = comparison_results["comparative_analysis"]["summary"]
        
        click.echo("\n" + "="*50)
        click.echo("COMPARISON SUMMARY") 
        click.echo("="*50)
        
        if "overall_winner" in summary:
            click.echo(f"\nOverall Winner: {summary['overall_winner']}")
            click.echo(f"Metrics Won: {summary['wins_count'].get(summary['overall_winner'], 0)}/{summary['total_metrics_compared']}")
        
        click.echo(f"\nComparison report saved to: {output}")
        click.echo("Comparison completed successfully!")
        
    except Exception as e:
        click.echo(f"Error during comparison: {e}", err=True)
        return





def main():
    """Main entry point for the CLI."""
    cli() 