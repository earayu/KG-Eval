"""
Report generator for KG-Eval framework.

This module provides functionality to generate evaluation reports in various formats
including JSON, HTML, and Markdown. It also supports radar charts for visualization.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np


class ReportGenerator:
    """Generator for KG-Eval evaluation reports."""

    def __init__(self):
        """Initialize the report generator."""
        pass

    def generate_json_report(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Generate a JSON report of evaluation results.
        
        Args:
            results: Evaluation results dictionary
            output_path: Path to save the JSON report
        """
        report_data = {
            "kg_eval_report": {
                "generated_at": datetime.now().isoformat(),
                "results": results
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"JSON report saved to: {output_path}")

    def generate_markdown_report(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Generate a Markdown report of evaluation results.
        
        Args:
            results: Evaluation results dictionary
            output_path: Path to save the Markdown report
        """
        md_content = self._create_markdown_content(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Markdown report saved to: {output_path}")

    def generate_html_report(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Generate an HTML report with interactive visualizations.
        
        Args:
            results: Evaluation results dictionary
            output_path: Path to save the HTML report
        """
        html_content = self._create_html_content(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report saved to: {output_path}")

    def generate_comparison_report(self, comparison_results: Dict[str, Any], output_path: str) -> None:
        """
        Generate a comparison report for multiple knowledge graphs.
        
        Args:
            comparison_results: Results from compare_knowledge_graphs()
            output_path: Path to save the comparison report
        """
        html_content = self._create_comparison_html(comparison_results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Comparison report saved to: {output_path}")

    def generate_radar_chart(self, results: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Generate a radar chart visualization of evaluation results.
        
        Args:
            results: Evaluation results dictionary
            output_path: Path to save the chart (optional)
            
        Returns:
            HTML string of the radar chart
        """
        # Extract key metrics for radar chart
        metrics = self._extract_radar_metrics(results)
        
        if not metrics:
            return "<p>No data available for radar chart</p>"

        # Create radar chart using Plotly
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=list(metrics.values()),
            theta=list(metrics.keys()),
            fill='toself',
            name='KG Evaluation Scores',
            line_color='rgb(0,100,200)',
            fillcolor='rgba(0,100,200,0.3)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True,
            title="KG-Eval Radar Chart",
            width=600,
            height=600
        )

        if output_path:
            fig.write_html(output_path)
            print(f"Radar chart saved to: {output_path}")

        return fig.to_html(include_plotlyjs=True, div_id="radar-chart")

    def generate_comparative_analysis(self, individual_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comparative analysis between multiple knowledge graphs.
        
        Args:
            individual_results: Dictionary of {kg_name: evaluation_results}
            
        Returns:
            Comparative analysis results
        """
        analysis = {
            "metric_comparison": {},
            "rankings": {},
            "summary": {}
        }

        # Extract metrics for comparison
        all_metrics = {}
        for kg_name, results in individual_results.items():
            metrics = self._extract_comparison_metrics(results)
            all_metrics[kg_name] = metrics

        # Compare metrics
        for metric_name in set().union(*[metrics.keys() for metrics in all_metrics.values()]):
            metric_values = {}
            for kg_name, metrics in all_metrics.items():
                if metric_name in metrics and metrics[metric_name] is not None:
                    metric_values[kg_name] = metrics[metric_name]
            
            if metric_values:
                analysis["metric_comparison"][metric_name] = {
                    "values": metric_values,
                    "best": max(metric_values.items(), key=lambda x: x[1]),
                    "worst": min(metric_values.items(), key=lambda x: x[1]),
                    "average": sum(metric_values.values()) / len(metric_values)
                }

        # Generate rankings
        analysis["rankings"] = self._generate_rankings(all_metrics)

        # Generate summary
        analysis["summary"] = self._generate_comparison_summary(analysis)

        return analysis

    def _create_markdown_content(self, results: Dict[str, Any]) -> str:
        """Create Markdown content for the report."""
        md = "# KG-Eval Evaluation Report\n\n"
        md += f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Metadata
        if "evaluation_metadata" in results:
            metadata = results["evaluation_metadata"]
            md += "## Evaluation Metadata\n\n"
            md += f"- **Knowledge Graph:** {metadata.get('kg_summary', 'N/A')}\n"
            md += f"- **LLM Referee Available:** {metadata.get('llm_referee_available', False)}\n"
            md += f"- **Sample Size:** {metadata.get('sample_size', 'N/A')}\n"
            md += f"- **Included Dimensions:** {', '.join(metadata.get('included_dimensions', []))}\n\n"

        # Scale & Richness
        if "scale_richness" in results:
            md += "## Scale & Richness\n\n"
            sr = results["scale_richness"]
            md += f"- **Entity Count:** {sr.get('entity_count', 0)}\n"
            md += f"- **Relationship Count:** {sr.get('relationship_count', 0)}\n"
            md += f"- **Property Fill Rate:** {sr.get('overall_property_fill_rate', 0.0):.4f}\n"
            md += f"- **Unique Relationship Types:** {sr.get('unique_relationship_types', 0)}\n\n"

        # Structural Integrity
        if "structural_integrity" in results:
            md += "## Structural Integrity\n\n"
            si = results["structural_integrity"]
            md += f"- **Graph Density:** {si.get('graph_density', 0.0):.4f}\n"
            md += f"- **LCC Ratio:** {si.get('largest_connected_component_ratio', 0.0):.4f}\n"
            md += f"- **Singleton Ratio:** {si.get('singleton_ratio', 0.0):.4f}\n"
            md += f"- **Connected Components:** {si.get('connected_components_count', 0)}\n\n"

        # Semantic Quality
        if "semantic_quality" in results:
            md += "## Semantic Quality\n\n"
            sq = results["semantic_quality"]
            md += f"- **Entity Normalization Score:** {sq.get('entity_normalization_score', 0.0):.4f}\n"
            factual_precision = sq.get('factual_precision')
            if factual_precision is not None:
                md += f"- **Factual Precision:** {factual_precision:.4f}\n"
            else:
                md += "- **Factual Precision:** Not evaluated (LLM referee required)\n"
            md += f"- **Alias Pairs Count:** {sq.get('alias_pairs_count', 0)}\n\n"

        # Efficiency
        if "efficiency" in results:
            md += "## Efficiency\n\n"
            eff = results["efficiency"]
            md += f"- **Knowledge Density per Chunk:** {eff.get('knowledge_density_per_chunk', 0.0):.4f}\n"
            md += f"- **Productive Source Ratio:** {eff.get('productive_source_ratio', 0.0):.4f}\n"
            md += f"- **Average Source Text Length:** {eff.get('average_source_text_length', 0.0):.2f}\n\n"

        return md

    def _create_html_content(self, results: Dict[str, Any]) -> str:
        """Create HTML content for the report."""
        radar_chart_html = self.generate_radar_chart(results)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KG-Eval Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 30px 0; }}
        .metric {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #007acc; }}
        .chart-container {{ text-align: center; margin: 30px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>KG-Eval Evaluation Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="chart-container">
        {radar_chart_html}
    </div>

    {self._create_html_sections(results)}

</body>
</html>
"""
        return html

    def _create_html_sections(self, results: Dict[str, Any]) -> str:
        """Create HTML sections for each evaluation dimension."""
        html = ""
        
        # Scale & Richness
        if "scale_richness" in results:
            sr = results["scale_richness"]
            html += f"""
    <div class="section">
        <h2>Scale & Richness</h2>
        <div class="metric">
            <strong>Entity Count:</strong> {sr.get('entity_count', 0)}
        </div>
        <div class="metric">
            <strong>Relationship Count:</strong> {sr.get('relationship_count', 0)}
        </div>
        <div class="metric">
            <strong>Overall Property Fill Rate:</strong> {sr.get('overall_property_fill_rate', 0.0):.4f}
        </div>
        <div class="metric">
            <strong>Unique Relationship Types:</strong> {sr.get('unique_relationship_types', 0)}
        </div>
    </div>
"""

        # Add other sections similarly...
        return html

    def _create_comparison_html(self, comparison_results: Dict[str, Any]) -> str:
        """Create HTML content for comparison report."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KG-Eval Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .best {{ background-color: #d4edda; }}
        .worst {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>KG-Eval Comparison Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Knowledge Graphs:</strong> {', '.join(comparison_results['comparison_metadata']['graph_names'])}</p>
    </div>

    {self._create_comparison_table(comparison_results)}

</body>
</html>
"""
        return html

    def _create_comparison_table(self, comparison_results: Dict[str, Any]) -> str:
        """Create comparison table HTML."""
        if "comparative_analysis" not in comparison_results:
            return "<p>No comparative analysis available</p>"
        
        analysis = comparison_results["comparative_analysis"]
        metric_comparison = analysis.get("metric_comparison", {})
        
        if not metric_comparison:
            return "<p>No metrics available for comparison</p>"

        html = "<h2>Metric Comparison</h2>\n<table>\n<tr><th>Metric</th>"
        
        # Get all KG names
        kg_names = comparison_results["comparison_metadata"]["graph_names"]
        for name in kg_names:
            html += f"<th>{name}</th>"
        html += "</tr>\n"

        # Add rows for each metric
        for metric_name, metric_data in metric_comparison.items():
            html += f"<tr><td><strong>{metric_name.replace('_', ' ').title()}</strong></td>"
            
            values = metric_data["values"]
            best_kg = metric_data["best"][0]
            worst_kg = metric_data["worst"][0]
            
            for kg_name in kg_names:
                value = values.get(kg_name, "N/A")
                css_class = ""
                if kg_name == best_kg:
                    css_class = "best"
                elif kg_name == worst_kg:
                    css_class = "worst"
                
                if isinstance(value, float):
                    html += f'<td class="{css_class}">{value:.4f}</td>'
                else:
                    html += f'<td class="{css_class}">{value}</td>'
            
            html += "</tr>\n"

        html += "</table>\n"
        return html

    def _extract_radar_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics for radar chart (normalized to 0-10 scale)."""
        metrics = {}

        if "scale_richness" in results:
            sr = results["scale_richness"]
            # Normalize property fill rate to 0-10 scale
            fill_rate = sr.get("overall_property_fill_rate", 0.0)
            metrics["Richness"] = fill_rate * 10

        if "structural_integrity" in results:
            si = results["structural_integrity"]
            # Use LCC ratio as connectivity score
            lcc_ratio = si.get("largest_connected_component_ratio", 0.0)
            metrics["Connectivity"] = lcc_ratio * 10

        if "semantic_quality" in results:
            sq = results["semantic_quality"]
            # Normalization score
            norm_score = sq.get("entity_normalization_score", 0.0)
            metrics["Normalization"] = norm_score * 10
            
            # Factual precision
            factual_precision = sq.get("factual_precision")
            if factual_precision is not None:
                metrics["Faithfulness"] = factual_precision * 10

        if "efficiency" in results:
            eff = results["efficiency"]
            # Normalize knowledge density (assume max of 5.0 for scaling)
            density = min(eff.get("knowledge_density_per_chunk", 0.0), 5.0)
            metrics["Efficiency"] = (density / 5.0) * 10

        return metrics

    def _extract_comparison_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics for comparison."""
        metrics = {}

        if "scale_richness" in results:
            sr = results["scale_richness"]
            metrics["entity_count"] = sr.get("entity_count", 0)
            metrics["relationship_count"] = sr.get("relationship_count", 0)
            metrics["property_fill_rate"] = sr.get("overall_property_fill_rate", 0.0)

        if "structural_integrity" in results:
            si = results["structural_integrity"]
            metrics["graph_density"] = si.get("graph_density", 0.0)
            metrics["lcc_ratio"] = si.get("largest_connected_component_ratio", 0.0)
            metrics["singleton_ratio"] = si.get("singleton_ratio", 0.0)

        if "semantic_quality" in results:
            sq = results["semantic_quality"]
            metrics["entity_normalization_score"] = sq.get("entity_normalization_score", 0.0)
            metrics["factual_precision"] = sq.get("factual_precision")

        if "efficiency" in results:
            eff = results["efficiency"]
            metrics["knowledge_density"] = eff.get("knowledge_density_per_chunk", 0.0)

        return metrics

    def _generate_rankings(self, all_metrics: Dict[str, Dict[str, float]]) -> Dict[str, List[str]]:
        """Generate rankings for each metric."""
        rankings = {}
        
        # Get all metric names
        all_metric_names = set()
        for metrics in all_metrics.values():
            all_metric_names.update(metrics.keys())

        # Rank each metric
        for metric_name in all_metric_names:
            metric_values = []
            for kg_name, metrics in all_metrics.items():
                if metric_name in metrics and metrics[metric_name] is not None:
                    metric_values.append((kg_name, metrics[metric_name]))
            
            if metric_values:
                # Sort by value (descending for most metrics)
                if metric_name == "singleton_ratio":  # Lower is better
                    metric_values.sort(key=lambda x: x[1])
                else:  # Higher is better
                    metric_values.sort(key=lambda x: x[1], reverse=True)
                
                rankings[metric_name] = [kg_name for kg_name, _ in metric_values]

        return rankings

    def _generate_comparison_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of comparison analysis."""
        rankings = analysis.get("rankings", {})
        
        if not rankings:
            return {"message": "No rankings available"}

        # Count wins for each KG
        kg_wins = {}
        for metric_rankings in rankings.values():
            if metric_rankings:
                winner = metric_rankings[0]
                kg_wins[winner] = kg_wins.get(winner, 0) + 1

        if kg_wins:
            overall_winner = max(kg_wins.items(), key=lambda x: x[1])
        else:
            overall_winner = ("N/A", 0)

        return {
            "overall_winner": overall_winner[0],
            "wins_count": kg_wins,
            "total_metrics_compared": len(rankings)
        } 