"""
Dimension Two: Structural & Topological Integrity

This module analyzes the health, connectivity, and structural characteristics 
of the graph using graph theory principles.

Metrics include:
1. Graph Density: Measures overall interconnectedness
2. Connectedness Analysis: LCC ratio and singleton ratio
3. Centrality Distribution: PageRank or Degree Centrality analysis
"""

from typing import Dict, Any, List
import networkx as nx
import numpy as np
from collections import Counter
from ..data_objects import KnowledgeGraph
from ..base_evaluator import BaseEvaluator


class StructuralIntegrityEvaluator(BaseEvaluator):
    """Evaluator for Structural and Topological Integrity dimension."""

    def evaluate(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Evaluate the structural integrity of the knowledge graph.
        
        Args:
            kg: The knowledge graph to evaluate
            
        Returns:
            Dictionary containing evaluation metrics
        """
        if not kg.entities or not kg.relationships:
            return self._empty_graph_metrics()

        # Build NetworkX graph
        graph = self._build_networkx_graph(kg)
        
        metrics = {}
        
        # 1. Graph Density
        metrics.update(self._calculate_graph_density(graph, kg))
        
        # 2. Connectedness Analysis
        metrics.update(self._calculate_connectedness(graph))
        
        # 3. Centrality Distribution
        metrics.update(self._calculate_centrality_distribution(graph))
        
        return metrics

    def _empty_graph_metrics(self) -> Dict[str, Any]:
        """Return metrics for empty graph."""
        return {
            "graph_density": 0.0,
            "largest_connected_component_ratio": 0.0,
            "singleton_ratio": 1.0,
            "connected_components_count": 0,
            "average_degree_centrality": 0.0,
            "pagerank_entropy": 0.0,
            "centrality_distribution_stats": {
                "mean": 0.0,
                "std": 0.0,
                "max": 0.0,
                "min": 0.0
            }
        }

    def _build_networkx_graph(self, kg: KnowledgeGraph) -> nx.DiGraph:
        """Build a NetworkX directed graph from the knowledge graph."""
        graph = nx.DiGraph()
        
        # Add nodes (entities)
        for entity in kg.entities:
            graph.add_node(entity.entity_name, 
                          entity_type=entity.entity_type,
                          description=entity.description)
        
        # Add edges (relationships)
        for relationship in kg.relationships:
            graph.add_edge(
                relationship.source_entity_name,
                relationship.target_entity_name,
                description=relationship.description,
                keywords=relationship.keywords,
                weight=relationship.weight or 1.0
            )
        
        return graph

    def _calculate_graph_density(self, graph: nx.DiGraph, kg: KnowledgeGraph) -> Dict[str, float]:
        """
        Calculate graph density as Total Relationships / Total Entities.
        
        Note: This is different from NetworkX density which is edges/(nodes*(nodes-1))
        """
        total_entities = len(kg.entities)
        total_relationships = len(kg.relationships)
        
        if total_entities == 0:
            density = 0.0
        else:
            density = total_relationships / total_entities
            
        return {
            "graph_density": round(density, 4),
            "networkx_density": round(nx.density(graph), 4)
        }

    def _calculate_connectedness(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Calculate connectedness metrics including LCC ratio and singleton ratio.
        """
        if graph.number_of_nodes() == 0:
            return {
                "largest_connected_component_ratio": 0.0,
                "singleton_ratio": 1.0,
                "connected_components_count": 0,
                "average_component_size": 0.0
            }

        # Convert to undirected for connectivity analysis
        undirected_graph = graph.to_undirected()
        
        # Find connected components
        connected_components = list(nx.connected_components(undirected_graph))
        component_sizes = [len(component) for component in connected_components]
        
        # Largest Connected Component (LCC) ratio
        largest_component_size = max(component_sizes) if component_sizes else 0
        lcc_ratio = largest_component_size / graph.number_of_nodes()
        
        # Singleton ratio (nodes with no connections)
        singletons = sum(1 for size in component_sizes if size == 1)
        singleton_ratio = singletons / graph.number_of_nodes()
        
        # Average component size
        avg_component_size = np.mean(component_sizes) if component_sizes else 0.0
        
        return {
            "largest_connected_component_ratio": round(lcc_ratio, 4),
            "singleton_ratio": round(singleton_ratio, 4),
            "connected_components_count": len(connected_components),
            "average_component_size": round(avg_component_size, 4),
            "component_size_distribution": dict(Counter(component_sizes))
        }

    def _calculate_centrality_distribution(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Calculate centrality distribution using PageRank and Degree Centrality.
        """
        if graph.number_of_nodes() == 0:
            return {
                "average_degree_centrality": 0.0,
                "pagerank_entropy": 0.0,
                "centrality_distribution_stats": {
                    "mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0
                },
                "top_central_entities": []
            }

        # Calculate PageRank
        try:
            pagerank_scores = nx.pagerank(graph, weight='weight')
        except:
            # Fallback to unweighted PageRank
            pagerank_scores = nx.pagerank(graph)
            
        # Calculate Degree Centrality
        degree_centrality = nx.degree_centrality(graph)
        
        # PageRank entropy (measure of importance distribution)
        pagerank_values = list(pagerank_scores.values())
        pagerank_entropy = self._calculate_entropy(pagerank_values)
        
        # Centrality distribution statistics
        centrality_stats = {
            "mean": round(np.mean(pagerank_values), 6),
            "std": round(np.std(pagerank_values), 6),
            "max": round(np.max(pagerank_values), 6),
            "min": round(np.min(pagerank_values), 6)
        }
        
        # Top central entities
        top_entities = sorted(pagerank_scores.items(), 
                            key=lambda x: x[1], reverse=True)[:5]
        
        # Average degree centrality
        avg_degree_centrality = np.mean(list(degree_centrality.values()))
        
        return {
            "average_degree_centrality": round(avg_degree_centrality, 4),
            "pagerank_entropy": round(pagerank_entropy, 4),
            "centrality_distribution_stats": centrality_stats,
            "top_central_entities": [(entity, round(score, 6)) for entity, score in top_entities]
        }

    def _calculate_entropy(self, values: List[float]) -> float:
        """Calculate Shannon entropy of a distribution."""
        if not values or all(v == 0 for v in values):
            return 0.0
            
        # Normalize to probabilities
        total = sum(values)
        if total == 0:
            return 0.0
            
        probs = [v / total for v in values if v > 0]
        
        # Calculate entropy
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        return entropy 