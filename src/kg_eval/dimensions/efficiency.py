"""
Dimension Four: End-to-End Efficiency

This module measures the model's efficiency in transforming unstructured text 
into structured knowledge.

Metrics include:
1. Knowledge Density per Chunk: (Total Entities + Total Relationships) / Total Source Texts
"""

from typing import Dict, Any
from ..data_objects import KnowledgeGraph
from ..base_evaluator import BaseEvaluator


class EfficiencyEvaluator(BaseEvaluator):
    """Evaluator for End-to-End Efficiency dimension."""

    def evaluate(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Evaluate the efficiency of the knowledge graph construction.
        
        Args:
            kg: The knowledge graph to evaluate
            
        Returns:
            Dictionary containing evaluation metrics
        """
        metrics = {}
        
        # 1. Knowledge Density per Chunk
        metrics.update(self._calculate_knowledge_density(kg))
        
        # 2. Additional efficiency metrics
        metrics.update(self._calculate_additional_efficiency_metrics(kg))
        
        return metrics

    def _calculate_knowledge_density(self, kg: KnowledgeGraph) -> Dict[str, float]:
        """
        Calculate knowledge density per source text chunk.
        
        This measures how much structured knowledge is produced from each unit 
        of source text on average.
        """
        if not kg.source_texts:
            return {
                "knowledge_density_per_chunk": 0.0,
                "total_knowledge_items": 0,
                "total_source_chunks": 0
            }

        total_knowledge_items = len(kg.entities) + len(kg.relationships)
        total_source_chunks = len(kg.source_texts)
        
        knowledge_density = total_knowledge_items / total_source_chunks
        
        return {
            "knowledge_density_per_chunk": round(knowledge_density, 4),
            "total_knowledge_items": total_knowledge_items,
            "total_source_chunks": total_source_chunks
        }

    def _calculate_additional_efficiency_metrics(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Calculate additional efficiency-related metrics.
        """
        metrics = {}
        
        # Entity extraction efficiency
        if kg.source_texts:
            total_text_length = sum(len(source.content) for source in kg.source_texts)
            
            # Entities per character
            entities_per_char = len(kg.entities) / total_text_length if total_text_length > 0 else 0.0
            
            # Relationships per character  
            relationships_per_char = len(kg.relationships) / total_text_length if total_text_length > 0 else 0.0
            
            # Average entities per source text
            avg_entities_per_source = len(kg.entities) / len(kg.source_texts)
            
            # Average relationships per source text
            avg_relationships_per_source = len(kg.relationships) / len(kg.source_texts)
            
            # Average source text length
            avg_source_length = total_text_length / len(kg.source_texts)
            
            metrics.update({
                "entities_per_character": round(entities_per_char * 1000, 6),  # per 1000 chars
                "relationships_per_character": round(relationships_per_char * 1000, 6),  # per 1000 chars
                "average_entities_per_source": round(avg_entities_per_source, 4),
                "average_relationships_per_source": round(avg_relationships_per_source, 4),
                "average_source_text_length": round(avg_source_length, 2),
                "total_text_length": total_text_length
            })
        else:
            metrics.update({
                "entities_per_character": 0.0,
                "relationships_per_character": 0.0,
                "average_entities_per_source": 0.0,
                "average_relationships_per_source": 0.0,
                "average_source_text_length": 0.0,
                "total_text_length": 0
            })

        # Knowledge extraction coverage
        if kg.source_texts:
            # Calculate how many source texts actually contributed entities/relationships
            productive_sources = 0
            for source in kg.source_texts:
                if source.linked_entity_names or source.linked_edges:
                    productive_sources += 1
            
            coverage_ratio = productive_sources / len(kg.source_texts)
            
            metrics.update({
                "productive_source_ratio": round(coverage_ratio, 4),
                "productive_sources": productive_sources,
                "unproductive_sources": len(kg.source_texts) - productive_sources
            })
        else:
            metrics.update({
                "productive_source_ratio": 0.0,
                "productive_sources": 0,
                "unproductive_sources": 0
            })

        return metrics 