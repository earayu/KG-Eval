"""
KG-Eval: A Framework for Evaluating Large Language Models' Knowledge Graph Construction Capabilities

This package provides a comprehensive framework for evaluating the quality of knowledge graphs
constructed by LLMs across four key dimensions:

1. Scale & Richness: Breadth and depth of extracted information
2. Structural Integrity: Graph health and topological characteristics  
3. Semantic Quality: Accuracy, consistency, and relevance
4. End-to-End Efficiency: Transformation efficiency from text to structured knowledge
"""

from .data_objects import Entity, Relationship, SourceText, KnowledgeGraph
from .evaluator import KGEvaluator
from .llm_referee import LLMReferee, OpenAIReferee, AnthropicReferee
from .report_generator import ReportGenerator
from .dimensions import (
    ScaleRichnessEvaluator,
    StructuralIntegrityEvaluator,
    SemanticQualityEvaluator,
    EfficiencyEvaluator
)

__version__ = "0.1.0"
__author__ = "earayu"
__email__ = "earayu@163.com"

__all__ = [
    # Core data objects
    "Entity",
    "Relationship", 
    "SourceText",
    "KnowledgeGraph",
    
    # Main evaluator
    "KGEvaluator",
    
    # LLM referees
    "LLMReferee",
    "OpenAIReferee",
    "AnthropicReferee",
    
    # Report generator
    "ReportGenerator",
    
    # Individual dimension evaluators
    "ScaleRichnessEvaluator",
    "StructuralIntegrityEvaluator", 
    "SemanticQualityEvaluator",
    "EfficiencyEvaluator",
]


def main():
    """Entry point for the kg-eval command line interface."""
    from .cli import main as cli_main
    cli_main()
