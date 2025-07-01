"""
Dimension One: Generative Scale & Richness

This module evaluates the breadth and depth of information extracted by the model.
Metrics include:
1. Entity/Relationship Count: Overall size of the knowledge graph
2. Property Fill Rate: Proportion of optional attributes that are populated
3. Relational Diversity: Total number of distinct relationship types
"""

from typing import Dict, Any, Set
from collections import Counter
from ..data_objects import KnowledgeGraph
from ..base_evaluator import BaseEvaluator


class ScaleRichnessEvaluator(BaseEvaluator):
    """Evaluator for Scale and Richness dimension."""

    def evaluate(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Evaluate the scale and richness of the knowledge graph.
        
        Args:
            kg: The knowledge graph to evaluate
            
        Returns:
            Dictionary containing evaluation metrics
        """
        metrics = {}
        
        # 1. Entity/Relationship Count
        metrics.update(self._calculate_counts(kg))
        
        # 2. Property Fill Rate
        metrics.update(self._calculate_property_fill_rate(kg))
        
        # 3. Relational Diversity
        metrics.update(self._calculate_relational_diversity(kg))
        
        return metrics

    def _calculate_counts(self, kg: KnowledgeGraph) -> Dict[str, int]:
        """Calculate basic counts of entities and relationships."""
        return {
            "entity_count": len(kg.entities),
            "relationship_count": len(kg.relationships),
            "source_text_count": len(kg.source_texts),
        }

    def _calculate_property_fill_rate(self, kg: KnowledgeGraph) -> Dict[str, float]:
        """
        Calculate the proportion of optional attributes that are populated.
        
        A higher fill rate indicates richer metadata in the graph.
        """
        if not kg.entities and not kg.relationships:
            return {
                "entity_property_fill_rate": 0.0,
                "relationship_property_fill_rate": 0.0,
                "overall_property_fill_rate": 0.0,
            }

        # Entity property fill rate
        entity_fill_rates = []
        for entity in kg.entities:
            filled_count = 0
            total_optional = 2  # entity_type and description
            
            if entity.entity_type is not None:
                filled_count += 1
            if entity.description is not None:
                filled_count += 1
                
            entity_fill_rates.append(filled_count / total_optional)

        # Relationship property fill rate
        relationship_fill_rates = []
        for relationship in kg.relationships:
            filled_count = 0
            total_optional = 2  # keywords and weight
            
            if relationship.keywords is not None and len(relationship.keywords) > 0:
                filled_count += 1
            if relationship.weight is not None:
                filled_count += 1
                
            relationship_fill_rates.append(filled_count / total_optional)

        entity_avg_fill_rate = sum(entity_fill_rates) / len(entity_fill_rates) if entity_fill_rates else 0.0
        relationship_avg_fill_rate = sum(relationship_fill_rates) / len(relationship_fill_rates) if relationship_fill_rates else 0.0
        
        # Overall fill rate (weighted average)
        total_objects = len(kg.entities) + len(kg.relationships)
        overall_fill_rate = (
            (entity_avg_fill_rate * len(kg.entities) + 
             relationship_avg_fill_rate * len(kg.relationships)) / total_objects
        ) if total_objects > 0 else 0.0

        return {
            "entity_property_fill_rate": round(entity_avg_fill_rate, 4),
            "relationship_property_fill_rate": round(relationship_avg_fill_rate, 4),
            "overall_property_fill_rate": round(overall_fill_rate, 4),
        }

    def _calculate_relational_diversity(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Calculate the diversity of relationship types.
        
        More diversity indicates stronger ability to identify complex relationships.
        """
        if not kg.relationships:
            return {
                "unique_relationship_types": 0,
                "relationship_type_distribution": {},
                "relationship_diversity_score": 0.0,
            }

        # Extract relationship types from keywords
        relationship_types: Set[str] = set()
        type_counter = Counter()

        for relationship in kg.relationships:
            if relationship.keywords:
                for keyword in relationship.keywords:
                    relationship_types.add(keyword.lower().strip())
                    type_counter[keyword.lower().strip()] += 1
            else:
                # If no keywords, use the first few words of description as type
                desc_words = relationship.description.lower().split()[:2]
                type_desc = " ".join(desc_words)
                relationship_types.add(type_desc)
                type_counter[type_desc] += 1

        # Calculate diversity score using Shannon entropy
        total_relationships = sum(type_counter.values())
        diversity_score = 0.0
        
        if total_relationships > 0:
            for count in type_counter.values():
                prob = count / total_relationships
                if prob > 0:
                    diversity_score -= prob * (prob ** 0.5)  # Modified entropy for better scaling

        return {
            "unique_relationship_types": len(relationship_types),
            "relationship_type_distribution": dict(type_counter.most_common(10)),  # Top 10 types
            "relationship_diversity_score": round(diversity_score, 4),
        } 