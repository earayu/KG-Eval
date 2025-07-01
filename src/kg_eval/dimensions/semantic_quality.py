"""
Dimension Three: Semantic Quality & Faithfulness

This module evaluates the "value" of the knowledge, focusing on its accuracy, 
consistency, and relevance.

Metrics include:
1. Entity Normalization Score: Measures entity fragmentation/aliasing
2. Factual Precision: Faithfulness to source text using referee LLM
3. Contextual Relevance: Importance of extracted knowledge using referee LLM
"""

import random
from typing import Dict, Any, List, Tuple, Optional, Set
from Levenshtein import distance as levenshtein_distance
import numpy as np
from tqdm import tqdm

from ..data_objects import KnowledgeGraph, Relationship, SourceText
from ..base_evaluator import BaseEvaluator
from ..llm_referee import LLMReferee


class SemanticQualityEvaluator(BaseEvaluator):
    """Evaluator for Semantic Quality and Faithfulness dimension."""

    def __init__(self, llm_referee: Optional[LLMReferee] = None, 
                 sample_size: int = 50, similarity_threshold: float = 0.7):
        """
        Initialize the evaluator.
        
        Args:
            llm_referee: LLM referee for factual precision and relevance evaluation
            sample_size: Number of samples to evaluate for LLM-based metrics
            similarity_threshold: Threshold for entity similarity detection
        """
        self.llm_referee = llm_referee
        self.sample_size = sample_size
        self.similarity_threshold = similarity_threshold

    def evaluate(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Evaluate the semantic quality of the knowledge graph.
        
        Args:
            kg: The knowledge graph to evaluate
            
        Returns:
            Dictionary containing evaluation metrics
        """
        metrics = {}
        
        # 1. Entity Normalization Score
        metrics.update(self._calculate_entity_normalization_score(kg))
        
        # 2. Factual Precision (requires LLM referee)
        if self.llm_referee:
            metrics.update(self._calculate_factual_precision(kg))
        else:
            metrics["factual_precision"] = None
            metrics["factual_precision_details"] = "LLM referee not provided"
        
        # 3. Contextual Relevance (requires LLM referee)
        if self.llm_referee:
            metrics.update(self._calculate_contextual_relevance(kg))
        else:
            metrics["contextual_relevance"] = None
            metrics["contextual_relevance_details"] = "LLM referee not provided"
        
        return metrics

    def _calculate_entity_normalization_score(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Calculate entity normalization score by detecting potential aliases.
        
        A higher score indicates better entity normalization (less fragmentation).
        """
        if len(kg.entities) <= 1:
            return {
                "entity_normalization_score": 1.0,
                "potential_alias_pairs": [],
                "alias_pairs_count": 0
            }

        entity_names = [entity.entity_name for entity in kg.entities]
        alias_pairs = self._find_potential_aliases(entity_names)
        
        # Score = 1 - (Number of Alias Pairs / Total Entities)
        score = 1.0 - (len(alias_pairs) / len(kg.entities))
        score = max(0.0, score)  # Ensure non-negative
        
        return {
            "entity_normalization_score": round(score, 4),
            "potential_alias_pairs": alias_pairs[:10],  # Show top 10 pairs
            "alias_pairs_count": len(alias_pairs)
        }

    def _find_potential_aliases(self, entity_names: List[str]) -> List[Tuple[str, str, float]]:
        """
        Find potential alias pairs using string similarity.
        
        Returns:
            List of tuples (entity1, entity2, similarity_score)
        """
        alias_pairs = []
        
        for i, name1 in enumerate(entity_names):
            for j, name2 in enumerate(entity_names[i+1:], i+1):
                similarity = self._calculate_string_similarity(name1, name2)
                if similarity >= self.similarity_threshold:
                    alias_pairs.append((name1, name2, similarity))
        
        # Sort by similarity score (descending)
        alias_pairs.sort(key=lambda x: x[2], reverse=True)
        return alias_pairs

    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate normalized string similarity using Levenshtein distance.
        
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        str1_norm = str1.lower().strip()
        str2_norm = str2.lower().strip()
        
        if str1_norm == str2_norm:
            return 1.0
        
        # Calculate Levenshtein distance
        max_len = max(len(str1_norm), len(str2_norm))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(str1_norm, str2_norm)
        similarity = 1.0 - (distance / max_len)
        
        return max(0.0, similarity)

    def _calculate_factual_precision(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Calculate factual precision using LLM referee.
        
        Measures graph's fidelity to original text and resistance to hallucination.
        """
        if not kg.relationships or not kg.source_texts:
            return {
                "factual_precision": 0.0,
                "factual_precision_details": {
                    "total_evaluated": 0,
                    "correct": 0,
                    "partially_correct": 0,
                    "incorrect": 0
                }
            }

        # Create mapping from relationships to source texts
        rel_to_source = self._map_relationships_to_sources(kg)
        
        # Sample relationships for evaluation
        evaluable_relationships = [
            rel for rel in kg.relationships 
            if rel in rel_to_source
        ]
        
        if not evaluable_relationships:
            return {
                "factual_precision": 0.0,
                "factual_precision_details": {
                    "total_evaluated": 0,
                    "correct": 0,
                    "partially_correct": 0,
                    "incorrect": 0,
                    "error": "No relationships could be mapped to source texts"
                }
            }

        sample_size = min(self.sample_size, len(evaluable_relationships))
        sampled_relationships = random.sample(evaluable_relationships, sample_size)
        
        # Evaluate each relationship
        correct = 0
        partially_correct = 0
        incorrect = 0
        
        for relationship in tqdm(sampled_relationships, desc="Evaluating factual precision"):
            source_text = rel_to_source[relationship]
            verdict = self.llm_referee.evaluate_factual_precision(
                relationship, source_text
            )
            
            if verdict == "correct":
                correct += 1
            elif verdict == "partially_correct":
                partially_correct += 1
            else:  # incorrect
                incorrect += 1
        
        # Calculate precision: (Correct + 0.5 * Partially Correct) / Total
        precision = (correct + 0.5 * partially_correct) / sample_size if sample_size > 0 else 0.0
        
        return {
            "factual_precision": round(precision, 4),
            "factual_precision_details": {
                "total_evaluated": sample_size,
                "correct": correct,
                "partially_correct": partially_correct,
                "incorrect": incorrect
            }
        }

    def _calculate_contextual_relevance(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Calculate contextual relevance using LLM referee.
        
        Assesses whether extracted knowledge represents core facts vs. trivial information.
        """
        if not kg.source_texts:
            return {
                "contextual_relevance": 0.0,
                "contextual_relevance_details": {
                    "total_evaluated": 0,
                    "core_facts": 0,
                    "marginal_facts": 0
                }
            }

        # Sample entities and relationships for evaluation
        all_knowledge_items = []
        
        # Add entities
        for entity in kg.entities:
            source_texts = self._find_source_texts_for_entity(entity.entity_name, kg)
            if source_texts:
                all_knowledge_items.extend([
                    ("entity", entity, source_text) for source_text in source_texts
                ])
        
        # Add relationships
        rel_to_source = self._map_relationships_to_sources(kg)
        for relationship, source_text in rel_to_source.items():
            all_knowledge_items.append(("relationship", relationship, source_text))
        
        if not all_knowledge_items:
            return {
                "contextual_relevance": 0.0,
                "contextual_relevance_details": {
                    "total_evaluated": 0,
                    "core_facts": 0,
                    "marginal_facts": 0,
                    "error": "No knowledge items could be mapped to source texts"
                }
            }

        # Sample for evaluation
        sample_size = min(self.sample_size, len(all_knowledge_items))
        sampled_items = random.sample(all_knowledge_items, sample_size)
        
        # Evaluate each item
        core_facts = 0
        marginal_facts = 0
        
        for item_type, knowledge_item, source_text in tqdm(sampled_items, desc="Evaluating contextual relevance"):
            is_core = self.llm_referee.evaluate_contextual_relevance(
                knowledge_item, source_text, item_type
            )
            
            if is_core:
                core_facts += 1
            else:
                marginal_facts += 1
        
        # Calculate relevance score
        relevance = core_facts / sample_size if sample_size > 0 else 0.0
        
        return {
            "contextual_relevance": round(relevance, 4),
            "contextual_relevance_details": {
                "total_evaluated": sample_size,
                "core_facts": core_facts,
                "marginal_facts": marginal_facts
            }
        }

    def _map_relationships_to_sources(self, kg: KnowledgeGraph) -> Dict[Relationship, SourceText]:
        """Map relationships to their source texts."""
        rel_to_source = {}
        
        for source_text in kg.source_texts:
            for edge in source_text.linked_edges:
                source_entity, target_entity = edge
                
                # Find matching relationship
                for relationship in kg.relationships:
                    if (relationship.source_entity_name == source_entity and 
                        relationship.target_entity_name == target_entity):
                        rel_to_source[relationship] = source_text
                        break
        
        return rel_to_source

    def _find_source_texts_for_entity(self, entity_name: str, kg: KnowledgeGraph) -> List[SourceText]:
        """Find source texts that mention a specific entity."""
        source_texts = []
        
        for source_text in kg.source_texts:
            if entity_name in source_text.linked_entity_names:
                source_texts.append(source_text)
        
        return source_texts 