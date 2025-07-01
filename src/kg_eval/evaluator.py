"""
Main KG-Eval evaluator that coordinates all dimension evaluators.

This module provides the primary interface for evaluating knowledge graphs
across all four dimensions of the KG-Eval framework.
"""

from typing import Dict, Any, Optional, List
from .data_objects import KnowledgeGraph
from .dimensions import (
    ScaleRichnessEvaluator,
    StructuralIntegrityEvaluator,
    SemanticQualityEvaluator,
    EfficiencyEvaluator
)
from .llm_referee import LLMReferee
from .report_generator import ReportGenerator


class KGEvaluator:
    """
    Main evaluator for the KG-Eval framework.
    
    This class coordinates evaluation across all four dimensions:
    1. Scale and Richness
    2. Structural Integrity  
    3. Semantic Quality
    4. End-to-End Efficiency
    """

    def __init__(self, 
                 llm_referee: Optional[LLMReferee] = None,
                 sample_size: int = 50,
                 similarity_threshold: float = 0.7):
        """
        Initialize the KG evaluator.
        
        Args:
            llm_referee: LLM referee for semantic quality evaluation
            sample_size: Sample size for LLM-based evaluations
            similarity_threshold: Threshold for entity similarity detection
        """
        self.llm_referee = llm_referee
        self.sample_size = sample_size
        self.similarity_threshold = similarity_threshold
        
        # Initialize dimension evaluators
        self.scale_richness_evaluator = ScaleRichnessEvaluator()
        self.structural_integrity_evaluator = StructuralIntegrityEvaluator()
        self.semantic_quality_evaluator = SemanticQualityEvaluator(
            llm_referee=llm_referee,
            sample_size=sample_size,
            similarity_threshold=similarity_threshold
        )
        self.efficiency_evaluator = EfficiencyEvaluator()
        
        # Initialize report generator
        self.report_generator = ReportGenerator()

    def evaluate(self, kg: KnowledgeGraph, 
                 include_dimensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluate the knowledge graph across all or specified dimensions.
        
        Args:
            kg: The knowledge graph to evaluate
            include_dimensions: List of dimensions to include 
                              ['scale_richness', 'structural_integrity', 
                               'semantic_quality', 'efficiency']
                              If None, includes all dimensions.
                              
        Returns:
            Dictionary containing evaluation results for all dimensions
        """
        if include_dimensions is None:
            include_dimensions = [
                'scale_richness', 
                'structural_integrity', 
                'semantic_quality', 
                'efficiency'
            ]

        results = {
            "evaluation_metadata": {
                "kg_summary": str(kg),
                "llm_referee_available": self.llm_referee is not None,
                "sample_size": self.sample_size,
                "similarity_threshold": self.similarity_threshold,
                "included_dimensions": include_dimensions
            }
        }

        # Evaluate each dimension
        if 'scale_richness' in include_dimensions:
            print("Evaluating Scale & Richness...")
            results['scale_richness'] = self.scale_richness_evaluator.evaluate(kg)

        if 'structural_integrity' in include_dimensions:
            print("Evaluating Structural Integrity...")
            results['structural_integrity'] = self.structural_integrity_evaluator.evaluate(kg)

        if 'semantic_quality' in include_dimensions:
            print("Evaluating Semantic Quality...")
            results['semantic_quality'] = self.semantic_quality_evaluator.evaluate(kg)

        if 'efficiency' in include_dimensions:
            print("Evaluating Efficiency...")
            results['efficiency'] = self.efficiency_evaluator.evaluate(kg)

        print("Evaluation complete!")
        return results

    def evaluate_and_report(self, kg: KnowledgeGraph,
                          output_path: Optional[str] = None,
                          include_dimensions: Optional[List[str]] = None,
                          report_format: str = 'json') -> Dict[str, Any]:
        """
        Evaluate the knowledge graph and generate a comprehensive report.
        
        Args:
            kg: The knowledge graph to evaluate
            output_path: Path to save the report (optional)
            include_dimensions: Dimensions to include in evaluation
            report_format: Format for the report ('json', 'html', 'markdown')
            
        Returns:
            Dictionary containing evaluation results
        """
        # Perform evaluation
        results = self.evaluate(kg, include_dimensions)
        
        # Generate report
        if output_path:
            if report_format == 'html':
                self.report_generator.generate_html_report(results, output_path)
            elif report_format == 'markdown':
                self.report_generator.generate_markdown_report(results, output_path)
            else:  # json
                self.report_generator.generate_json_report(results, output_path)
        
        return results

    def compare_knowledge_graphs(self, 
                                kgs: List[KnowledgeGraph],
                                kg_names: Optional[List[str]] = None,
                                output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare multiple knowledge graphs.
        
        Args:
            kgs: List of knowledge graphs to compare
            kg_names: Names for each knowledge graph (optional)
            output_path: Path to save comparison report (optional)
            
        Returns:
            Dictionary containing comparison results
        """
        if kg_names is None:
            kg_names = [f"KG_{i+1}" for i in range(len(kgs))]
        
        if len(kgs) != len(kg_names):
            raise ValueError("Number of knowledge graphs must match number of names")

        comparison_results = {
            "comparison_metadata": {
                "num_graphs": len(kgs),
                "graph_names": kg_names,
                "llm_referee_available": self.llm_referee is not None
            },
            "individual_results": {},
            "comparative_analysis": {}
        }

        # Evaluate each knowledge graph
        print(f"Comparing {len(kgs)} knowledge graphs...")
        for i, (kg, name) in enumerate(zip(kgs, kg_names)):
            print(f"Evaluating {name} ({i+1}/{len(kgs)})...")
            comparison_results["individual_results"][name] = self.evaluate(kg)

        # Generate comparative analysis
        comparison_results["comparative_analysis"] = self.report_generator.generate_comparative_analysis(
            comparison_results["individual_results"]
        )

        # Save comparison report if path provided
        if output_path:
            self.report_generator.generate_comparison_report(comparison_results, output_path)

        return comparison_results

    def get_evaluation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of evaluation results with key metrics.
        
        Args:
            results: Evaluation results from evaluate() method
            
        Returns:
            Summary dictionary with key metrics
        """
        summary = {
            "overall_scores": {},
            "key_metrics": {},
            "recommendations": []
        }

        # Extract key metrics from each dimension
        if 'scale_richness' in results:
            sr = results['scale_richness']
            summary["key_metrics"]["total_entities"] = sr.get("entity_count", 0)
            summary["key_metrics"]["total_relationships"] = sr.get("relationship_count", 0)
            summary["key_metrics"]["property_fill_rate"] = sr.get("overall_property_fill_rate", 0.0)

        if 'structural_integrity' in results:
            si = results['structural_integrity']
            summary["key_metrics"]["graph_density"] = si.get("graph_density", 0.0)
            summary["key_metrics"]["lcc_ratio"] = si.get("largest_connected_component_ratio", 0.0)
            summary["key_metrics"]["singleton_ratio"] = si.get("singleton_ratio", 0.0)

        if 'semantic_quality' in results:
            sq = results['semantic_quality']
            summary["key_metrics"]["entity_normalization_score"] = sq.get("entity_normalization_score", 0.0)
            summary["key_metrics"]["factual_precision"] = sq.get("factual_precision", None)

        if 'efficiency' in results:
            eff = results['efficiency']
            summary["key_metrics"]["knowledge_density"] = eff.get("knowledge_density_per_chunk", 0.0)

        # Generate recommendations based on results
        summary["recommendations"] = self._generate_recommendations(results)

        return summary

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on evaluation results."""
        recommendations = []

        # Scale and Richness recommendations
        if 'scale_richness' in results:
            sr = results['scale_richness']
            if sr.get("overall_property_fill_rate", 0) < 0.5:
                recommendations.append("Consider improving metadata extraction to increase property fill rate")
            if sr.get("relationship_diversity_score", 0) < 1.0:
                recommendations.append("Work on identifying more diverse relationship types")

        # Structural Integrity recommendations
        if 'structural_integrity' in results:
            si = results['structural_integrity']
            if si.get("singleton_ratio", 0) > 0.3:
                recommendations.append("High singleton ratio detected - consider improving entity linking")
            if si.get("largest_connected_component_ratio", 0) < 0.7:
                recommendations.append("Graph appears fragmented - work on connecting related entities")

        # Semantic Quality recommendations
        if 'semantic_quality' in results:
            sq = results['semantic_quality']
            if sq.get("entity_normalization_score", 1.0) < 0.8:
                recommendations.append("Entity normalization needs improvement - many potential aliases detected")
            factual_precision = sq.get("factual_precision")
            if factual_precision is not None and factual_precision < 0.8:
                recommendations.append("Factual precision is low - review knowledge extraction accuracy")

        # Efficiency recommendations
        if 'efficiency' in results:
            eff = results['efficiency']
            if eff.get("productive_source_ratio", 0) < 0.7:
                recommendations.append("Many source texts are unproductive - improve text filtering or processing")

        if not recommendations:
            recommendations.append("Overall performance looks good across evaluated dimensions")

        return recommendations 