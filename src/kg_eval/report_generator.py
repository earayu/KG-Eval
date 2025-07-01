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
            title_x=0.5,  # Center the title
            width=600,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),  # Add margins for better centering
            autosize=False
        )

        if output_path:
            # Generate custom HTML with centering styles
            chart_html = fig.to_html(include_plotlyjs=True, div_id="radar-chart")
            
            # Create complete HTML page with centering styles
            full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KG-Eval Radar Chart</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            background-color: #f5f5f5; 
        }}
        .chart-container {{ 
            text-align: center; 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            flex-direction: column; 
        }}
        .chart-container > div {{ 
            margin: 0 auto; 
            display: inline-block; 
        }}
        h1 {{ 
            color: #333; 
            margin-bottom: 20px; 
            text-align: center; 
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <h1>KG-Eval Radar Chart</h1>
        {chart_html}
    </div>
</body>
</html>
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            print(f"Radar chart saved to: {output_path}")

        # Generate HTML with custom styling for centering
        chart_html = fig.to_html(include_plotlyjs=True, div_id="radar-chart")
        
        # Wrap in a centered div with additional styling
        centered_html = f'''
        <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin: 20px 0;">
            <div style="display: inline-block; text-align: center;">
                {chart_html}
            </div>
        </div>
        '''
        
        return centered_html

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
        metadata = results.get("evaluation_metadata", {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KG-Eval Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{ 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="25" cy="75" r="1" fill="rgba(255,255,255,0.05)"/><circle cx="75" cy="25" r="1" fill="rgba(255,255,255,0.05)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        }}
        
        .header h1 {{ 
            font-size: 3em; 
            margin-bottom: 10px;
            font-weight: 300;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
            position: relative;
            z-index: 1;
        }}
        
        .metadata {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            position: relative;
            z-index: 1;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .metadata-item {{
            text-align: left;
        }}
        
        .metadata-label {{
            font-weight: bold;
            opacity: 0.8;
            font-size: 0.9em;
        }}
        
        .metadata-value {{
            font-size: 1.1em;
            margin-top: 5px;
        }}
        
        .chart-container {{ 
            text-align: center; 
            margin: 40px 0; 
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            margin: 30px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{ 
            margin: 40px 0; 
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 1px solid #e9ecef;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .section-icon {{
            font-size: 2em;
            margin-right: 15px;
        }}
        
        .section h2 {{ 
            font-size: 1.8em;
            color: #2c3e50;
            margin: 0;
            font-weight: 600;
        }}
        
        .section-description {{
            color: #6c757d;
            font-style: italic;
            margin-bottom: 20px;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .metric {{ 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #007acc;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .metric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .metric-name {{
            font-weight: bold;
            color: #495057;
            font-size: 1em;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            font-size: 1.4em;
            font-weight: bold;
            color: #007acc;
        }}
        
        .metric-description {{
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: linear-gradient(135deg, #495057 0%, #6c757d 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .data-table tr:hover {{
            background: #e3f2fd;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #007acc 0%, #0056b3 100%);
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .status-excellent {{ background: #d4edda; color: #155724; }}
        .status-good {{ background: #d1ecf1; color: #0c5460; }}
        .status-fair {{ background: #fff3cd; color: #856404; }}
        .status-poor {{ background: #f8d7da; color: #721c24; }}
        
        .recommendations {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            border-left: 5px solid #ff9800;
        }}
        
        .recommendations h3 {{
            color: #e65100;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .recommendations ul {{
            list-style: none;
            padding: 0;
        }}
        
        .recommendations li {{
            padding: 8px 0;
            position: relative;
            padding-left: 25px;
        }}
        
        .recommendations li::before {{
            content: '💡';
            position: absolute;
            left: 0;
            top: 8px;
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ padding: 20px; }}
            .header h1 {{ font-size: 2em; }}
            .content {{ padding: 15px; }}
            .section {{ margin: 20px 0; padding: 20px; }}
            .metrics-grid {{ grid-template-columns: 1fr; }}
            .metadata-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
                            <h1>📊 KG-Eval Report</h1>
            <div class="subtitle">Multi-Dimensional Knowledge Graph Evaluation</div>
            
            <div class="metadata">
                <strong>📊 Evaluation Summary</strong>
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <div class="metadata-label">Generated</div>
                        <div class="metadata-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Knowledge Graph</div>
                        <div class="metadata-value">{metadata.get('kg_summary', 'N/A')}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">LLM Referee</div>
                        <div class="metadata-value">{'✅ Available' if metadata.get('llm_referee_available', False) else '❌ Not Available'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Dimensions Evaluated</div>
                        <div class="metadata-value">{len(metadata.get('included_dimensions', []))}/4</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="content">
            <div class="chart-container">
                <h2 style="margin-bottom: 20px; color: #495057;">📈 Performance Overview</h2>
                {radar_chart_html}
            </div>

            {self._create_html_sections(results)}
        </div>
    </div>
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
            property_fill_rate = sr.get('overall_property_fill_rate', 0.0)
            fill_rate_percentage = property_fill_rate * 100
            fill_rate_status = self._get_status_class(property_fill_rate, thresholds=[0.8, 0.6, 0.4])
            
            html += f"""
    <div class="section">
        <div class="section-header">
            <div class="section-icon">🔢</div>
            <div>
                <h2>Scale & Richness</h2>
                <div class="section-description">Measures the breadth and depth of extracted information</div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-name">Entity Count</div>
                <div class="metric-value">{sr.get('entity_count', 0):,}</div>
                <div class="metric-description">Total number of unique entities identified</div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Relationship Count</div>
                <div class="metric-value">{sr.get('relationship_count', 0):,}</div>
                <div class="metric-description">Total number of relationships extracted</div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Property Fill Rate</div>
                <div class="metric-value">{fill_rate_percentage:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {fill_rate_percentage}%"></div>
                </div>
                <div class="metric-description">
                    <span class="status-badge {fill_rate_status}">{self._get_status_text(property_fill_rate, thresholds=[0.8, 0.6, 0.4])}</span>
                    Completeness of entity properties
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Relationship Types</div>
                <div class="metric-value">{sr.get('unique_relationship_types', 0)}</div>
                <div class="metric-description">Diversity of relationship types used</div>
            </div>
        </div>
        
        {self._create_entity_type_breakdown(sr)}
    </div>
"""

        # Structural Integrity
        if "structural_integrity" in results:
            si = results["structural_integrity"]
            graph_density = si.get('graph_density', 0.0)
            lcc_ratio = si.get('largest_connected_component_ratio', 0.0)
            singleton_ratio = si.get('singleton_ratio', 0.0)
            
            density_status = self._get_status_class(graph_density, thresholds=[0.3, 0.15, 0.05])
            connectivity_status = self._get_status_class(lcc_ratio, thresholds=[0.8, 0.6, 0.4])
            
            html += f"""
    <div class="section">
        <div class="section-header">
            <div class="section-icon">🕸️</div>
            <div>
                <h2>Structural Integrity</h2>
                <div class="section-description">Evaluates graph connectivity and topological health</div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-name">Graph Density</div>
                <div class="metric-value">{graph_density:.4f}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(graph_density * 333, 100)}%"></div>
                </div>
                <div class="metric-description">
                    <span class="status-badge {density_status}">{self._get_status_text(graph_density, thresholds=[0.3, 0.15, 0.05])}</span>
                    Ratio of actual edges to possible edges
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Largest Connected Component</div>
                <div class="metric-value">{lcc_ratio * 100:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {lcc_ratio * 100}%"></div>
                </div>
                <div class="metric-description">
                    <span class="status-badge {connectivity_status}">{self._get_status_text(lcc_ratio, thresholds=[0.8, 0.6, 0.4])}</span>
                    Percentage of nodes in main connected component
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Connected Components</div>
                <div class="metric-value">{si.get('connected_components_count', 0)}</div>
                <div class="metric-description">Number of disconnected graph components</div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Singleton Nodes</div>
                <div class="metric-value">{singleton_ratio * 100:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {singleton_ratio * 100}%; background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);"></div>
                </div>
                <div class="metric-description">Percentage of isolated nodes (lower is better)</div>
            </div>
        </div>
        
        {self._create_centrality_analysis(si)}
    </div>
"""

        # Semantic Quality
        if "semantic_quality" in results:
            sq = results["semantic_quality"]
            entity_norm_score = sq.get('entity_normalization_score', 0.0)
            factual_precision = sq.get('factual_precision')
            
            norm_status = self._get_status_class(entity_norm_score, thresholds=[0.9, 0.7, 0.5])
            
            html += f"""
    <div class="section">
        <div class="section-header">
            <div class="section-icon">✅</div>
            <div>
                <h2>Semantic Quality</h2>
                <div class="section-description">Assesses accuracy, consistency, and relevance of extracted knowledge</div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-name">Entity Normalization Score</div>
                <div class="metric-value">{entity_norm_score * 100:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {entity_norm_score * 100}%"></div>
                </div>
                <div class="metric-description">
                    <span class="status-badge {norm_status}">{self._get_status_text(entity_norm_score, thresholds=[0.9, 0.7, 0.5])}</span>
                    Consistency in entity naming and representation
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Factual Precision</div>
                <div class="metric-value">
                    {'🤖 ' + f'{factual_precision * 100:.1f}%' if factual_precision is not None else '❌ N/A'}
                </div>
                {f'<div class="progress-bar"><div class="progress-fill" style="width: {factual_precision * 100}%"></div></div>' if factual_precision is not None else ''}
                <div class="metric-description">
                    {'LLM-evaluated factual accuracy of extracted information' if factual_precision is not None else 'Requires LLM referee for evaluation'}
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Potential Alias Pairs</div>
                <div class="metric-value">{sq.get('alias_pairs_count', 0)}</div>
                <div class="metric-description">Entity names that might refer to the same concept</div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Contextual Relevance</div>
                <div class="metric-value">
                    {f'🤖 {sq.get("contextual_relevance", 0) * 100:.1f}%' if sq.get("contextual_relevance") is not None else '❌ N/A'}
                </div>
                <div class="metric-description">
                    {'LLM-evaluated relevance to source context' if sq.get("contextual_relevance") is not None else 'Requires LLM referee for evaluation'}
                </div>
            </div>
        </div>
        
        {self._create_alias_analysis(sq)}
    </div>
"""

        # Efficiency
        if "efficiency" in results:
            eff = results["efficiency"]
            knowledge_density = eff.get('knowledge_density_per_chunk', 0.0)
            productive_ratio = eff.get('productive_source_ratio', 0.0)
            
            density_status = self._get_status_class(knowledge_density, thresholds=[3.0, 2.0, 1.0])
            productive_status = self._get_status_class(productive_ratio, thresholds=[0.8, 0.6, 0.4])
            
            html += f"""
    <div class="section">
        <div class="section-header">
            <div class="section-icon">⚡</div>
            <div>
                <h2>Efficiency</h2>
                <div class="section-description">Measures effectiveness of text-to-knowledge transformation</div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-name">Knowledge Density</div>
                <div class="metric-value">{knowledge_density:.2f}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(knowledge_density * 20, 100)}%"></div>
                </div>
                <div class="metric-description">
                    <span class="status-badge {density_status}">{self._get_status_text(knowledge_density, thresholds=[3.0, 2.0, 1.0])}</span>
                    Average knowledge elements per text chunk
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Productive Source Ratio</div>
                <div class="metric-value">{productive_ratio * 100:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {productive_ratio * 100}%"></div>
                </div>
                <div class="metric-description">
                    <span class="status-badge {productive_status}">{self._get_status_text(productive_ratio, thresholds=[0.8, 0.6, 0.4])}</span>
                    Percentage of source texts that contributed to KG
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Average Text Length</div>
                <div class="metric-value">{eff.get('average_source_text_length', 0.0):.0f}</div>
                <div class="metric-description">Average length of source text chunks</div>
            </div>
            
            <div class="metric">
                <div class="metric-name">Source Coverage</div>
                <div class="metric-value">{eff.get('source_coverage_ratio', 0.0) * 100:.1f}%</div>
                <div class="metric-description">Percentage of source content linked to KG elements</div>
            </div>
        </div>
    </div>
"""

        # Add recommendations section
        html += self._create_recommendations_section(results)
        
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
        .chart-container {{ 
            text-align: center; 
            margin: 30px 0; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            flex-direction: column; 
        }}
        .chart-container > div {{ 
            margin: 0 auto; 
            display: inline-block; 
        }}
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

    def _get_status_class(self, value: float, thresholds: list) -> str:
        """Get CSS status class based on value and thresholds."""
        if value >= thresholds[0]:
            return "status-excellent"
        elif value >= thresholds[1]:
            return "status-good"
        elif value >= thresholds[2]:
            return "status-fair"
        else:
            return "status-poor"
    
    def _get_status_text(self, value: float, thresholds: list) -> str:
        """Get status text based on value and thresholds."""
        if value >= thresholds[0]:
            return "Excellent"
        elif value >= thresholds[1]:
            return "Good"
        elif value >= thresholds[2]:
            return "Fair"
        else:
            return "Poor"
    
    def _create_entity_type_breakdown(self, sr_results: Dict[str, Any]) -> str:
        """Create entity type breakdown table."""
        entity_types = sr_results.get('entity_type_counts', {})
        if not entity_types:
            return ""
        
        html = """
        <h3 style="margin-top: 30px; color: #495057;">📋 Entity Type Breakdown</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Entity Type</th>
                    <th>Count</th>
                    <th>Percentage</th>
                    <th>Distribution</th>
                </tr>
            </thead>
            <tbody>
        """
        
        total_entities = sum(entity_types.values())
        for entity_type, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_entities) * 100 if total_entities > 0 else 0
            html += f"""
                <tr>
                    <td><strong>{entity_type}</strong></td>
                    <td>{count:,}</td>
                    <td>{percentage:.1f}%</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {percentage}%"></div>
                        </div>
                    </td>
                </tr>
            """
        
        html += "</tbody></table>"
        return html
    
    def _create_centrality_analysis(self, si_results: Dict[str, Any]) -> str:
        """Create centrality analysis section."""
        centrality_stats = si_results.get('centrality_distribution', {})
        if not centrality_stats:
            return ""
        
        html = """
        <h3 style="margin-top: 30px; color: #495057;">🎯 Network Centrality Analysis</h3>
        <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
        """
        
        # Degree centrality
        if 'degree' in centrality_stats:
            degree_stats = centrality_stats['degree']
            html += f"""
            <div class="metric">
                <div class="metric-name">Avg Degree Centrality</div>
                <div class="metric-value">{degree_stats.get('mean', 0):.3f}</div>
                <div class="metric-description">Average node connectivity</div>
            </div>
            """
        
        # Betweenness centrality
        if 'betweenness' in centrality_stats:
            between_stats = centrality_stats['betweenness']
            html += f"""
            <div class="metric">
                <div class="metric-name">Avg Betweenness</div>
                <div class="metric-value">{between_stats.get('mean', 0):.3f}</div>
                <div class="metric-description">Average bridging capability</div>
            </div>
            """
        
        # Closeness centrality
        if 'closeness' in centrality_stats:
            close_stats = centrality_stats['closeness']
            html += f"""
            <div class="metric">
                <div class="metric-name">Avg Closeness</div>
                <div class="metric-value">{close_stats.get('mean', 0):.3f}</div>
                <div class="metric-description">Average path efficiency</div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _create_alias_analysis(self, sq_results: Dict[str, Any]) -> str:
        """Create alias analysis section."""
        alias_pairs = sq_results.get('alias_pairs', [])
        if not alias_pairs:
            return ""
        
        html = """
        <h3 style="margin-top: 30px; color: #495057;">🔍 Potential Entity Aliases</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Entity 1</th>
                    <th>Entity 2</th>
                    <th>Similarity Score</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # Show top 10 alias pairs
        for pair in alias_pairs[:10]:
            entity1, entity2 = pair.get('entities', ['', ''])
            similarity = pair.get('similarity_score', 0.0)
            status_class = self._get_status_class(similarity, [0.9, 0.7, 0.5])
            status_text = self._get_status_text(similarity, [0.9, 0.7, 0.5])
            
            html += f"""
                <tr>
                    <td><strong>{entity1}</strong></td>
                    <td><strong>{entity2}</strong></td>
                    <td>{similarity:.3f}</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                </tr>
            """
        
        html += "</tbody></table>"
        
        if len(alias_pairs) > 10:
            html += f"<p style='margin-top: 10px; color: #6c757d; font-style: italic;'>Showing top 10 of {len(alias_pairs)} potential aliases</p>"
        
        return html
    
    def _create_recommendations_section(self, results: Dict[str, Any]) -> str:
        """Create recommendations section."""
        recommendations = []
        
        # Scale & Richness recommendations
        if "scale_richness" in results:
            sr = results["scale_richness"]
            fill_rate = sr.get('overall_property_fill_rate', 0.0)
            if fill_rate < 0.5:
                recommendations.append("Consider improving entity property extraction to capture more detailed information")
            
            unique_rel_types = sr.get('unique_relationship_types', 0)
            total_rels = sr.get('relationship_count', 0)
            if total_rels > 0 and unique_rel_types / total_rels < 0.3:
                recommendations.append("Diversify relationship types to capture richer semantic connections")
        
        # Structural Integrity recommendations
        if "structural_integrity" in results:
            si = results["structural_integrity"]
            lcc_ratio = si.get('largest_connected_component_ratio', 0.0)
            if lcc_ratio < 0.6:
                recommendations.append("Improve entity linking to create a more connected knowledge graph")
            
            singleton_ratio = si.get('singleton_ratio', 0.0)
            if singleton_ratio > 0.3:
                recommendations.append("Reduce isolated entities by finding more relationship connections")
        
        # Semantic Quality recommendations
        if "semantic_quality" in results:
            sq = results["semantic_quality"]
            norm_score = sq.get('entity_normalization_score', 0.0)
            if norm_score < 0.7:
                recommendations.append("Implement entity normalization to resolve duplicate entities")
            
            alias_count = sq.get('alias_pairs_count', 0)
            if alias_count > 10:
                recommendations.append("Review and merge potential entity aliases to improve consistency")
        
        # Efficiency recommendations
        if "efficiency" in results:
            eff = results["efficiency"]
            density = eff.get('knowledge_density_per_chunk', 0.0)
            if density < 1.5:
                recommendations.append("Optimize text chunking strategy to improve knowledge extraction density")
            
            productive_ratio = eff.get('productive_source_ratio', 0.0)
            if productive_ratio < 0.5:
                recommendations.append("Improve text preprocessing to extract knowledge from more source texts")
        
        # LLM Referee recommendations
        metadata = results.get("evaluation_metadata", {})
        if not metadata.get('llm_referee_available', False):
            recommendations.append("Configure LLM referee to enable advanced semantic quality evaluation")
        
        if not recommendations:
            recommendations.append("Knowledge graph shows good overall quality across evaluated dimensions")
        
        html = """
        <div class="recommendations">
            <h3>💡 Recommendations for Improvement</h3>
            <ul>
        """
        
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        
        html += """
            </ul>
        </div>
        """
        
        return html 