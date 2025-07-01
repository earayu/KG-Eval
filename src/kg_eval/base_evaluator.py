"""
Base evaluator class for KG-Eval framework.

This module defines the abstract base class that all dimension evaluators inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .data_objects import KnowledgeGraph


class BaseEvaluator(ABC):
    """Abstract base class for all evaluators in the KG-Eval framework."""

    @abstractmethod
    def evaluate(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Evaluate the knowledge graph according to this dimension's metrics.
        
        Args:
            kg: The knowledge graph to evaluate
            
        Returns:
            Dictionary containing evaluation metrics specific to this dimension
        """
        pass

    def normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a score to 0-1 range.
        
        Args:
            value: The value to normalize
            min_val: Minimum possible value
            max_val: Maximum possible value
            
        Returns:
            Normalized score between 0 and 1
        """
        if max_val == min_val:
            return 1.0
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    def score_to_10_scale(self, normalized_score: float) -> float:
        """
        Convert a normalized score (0-1) to 10-point scale.
        
        Args:
            normalized_score: Score between 0 and 1
            
        Returns:
            Score between 0 and 10
        """
        return round(normalized_score * 10, 2) 