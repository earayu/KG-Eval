"""
Evaluation dimensions for KG-Eval framework.

This package contains four core evaluation dimensions:
1. Scale and Richness: Measures breadth and depth of extracted information
2. Structural Integrity: Analyzes graph health and topological characteristics
3. Semantic Quality: Evaluates accuracy, consistency, and relevance
4. Efficiency: Measures transformation efficiency from text to structured knowledge
"""

from .scale_richness import ScaleRichnessEvaluator
from .structural_integrity import StructuralIntegrityEvaluator
from .semantic_quality import SemanticQualityEvaluator
from .efficiency import EfficiencyEvaluator

__all__ = [
    "ScaleRichnessEvaluator",
    "StructuralIntegrityEvaluator", 
    "SemanticQualityEvaluator",
    "EfficiencyEvaluator",
] 