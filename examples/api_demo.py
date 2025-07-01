"""
Python API Demo for KG-Eval framework.

This script demonstrates how to use the Python API to:
1. Load a knowledge graph from JSON file
2. Evaluate the knowledge graph using the KGEvaluator class
3. Generate both JSON and HTML reports programmatically
4. Auto-open results in browser
"""

import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from kg_eval import (
    Entity, Relationship, SourceText, KnowledgeGraph,
    KGEvaluator
)


def create_sample_knowledge_graph() -> KnowledgeGraph:
    """Create a sample knowledge graph about the Three Kingdoms period."""
    
    # Create entities
    entities = [
        Entity(
            entity_name="曹操",
            entity_type="Person",
            description="魏国的建立者，东汉末年著名政治家、军事家"
        ),
        Entity(
            entity_name="刘备",
            entity_type="Person", 
            description="蜀汉的建立者，东汉末年政治家"
        ),
        Entity(
            entity_name="孙权",
            entity_type="Person",
            description="东吴的建立者，东汉末年政治家"
        ),
        Entity(
            entity_name="赤壁之战",
            entity_type="Event",
            description="东汉末年的重要战役"
        ),
        Entity(
            entity_name="魏国",
            entity_type="Kingdom"
        ),
        Entity(
            entity_name="蜀汉",
            entity_type="Kingdom"
        ),
        Entity(
            entity_name="东吴",
            entity_type="Kingdom"
        ),
    ]
    
    # Create relationships
    relationships = [
        Relationship(
            source_entity_name="曹操",
            target_entity_name="魏国",
            description="建立了魏国",
            keywords=["创建", "统治"],
            weight=0.9
        ),
        Relationship(
            source_entity_name="刘备",
            target_entity_name="蜀汉", 
            description="建立了蜀汉",
            keywords=["创建", "统治"],
            weight=0.9
        ),
        Relationship(
            source_entity_name="孙权",
            target_entity_name="东吴",
            description="建立了东吴",
            keywords=["创建", "统治"],
            weight=0.9
        ),
        Relationship(
            source_entity_name="刘备",
            target_entity_name="曹操",
            description="在赤壁之战中联合孙权对抗曹操",
            keywords=["对抗", "军事"],
            weight=0.8
        ),
        Relationship(
            source_entity_name="孙权",
            target_entity_name="曹操",
            description="在赤壁之战中联合刘备对抗曹操",
            keywords=["对抗", "军事"],
            weight=0.8
        ),
        Relationship(
            source_entity_name="赤壁之战",
            target_entity_name="曹操",
            description="曹操在此战役中失败",
            keywords=["战败", "军事"],
            weight=0.7
        ),
    ]
    
    # Create source texts
    source_texts = [
        SourceText(
            content="曹操是东汉末年著名的政治家、军事家，他统一了北方，建立了魏国政权。",
            linked_entity_names=["曹操", "魏国"],
            linked_edges=[("曹操", "魏国")]
        ),
        SourceText(
            content="刘备建立了蜀汉政权，与曹操、孙权形成三足鼎立的局面。",
            linked_entity_names=["刘备", "蜀汉", "曹操", "孙权"],
            linked_edges=[("刘备", "蜀汉")]
        ),
        SourceText(
            content="孙权建立东吴，统治江东地区，是三国时期的重要势力。",
            linked_entity_names=["孙权", "东吴"],
            linked_edges=[("孙权", "东吴")]
        ),
        SourceText(
            content="赤壁之战是三国时期的重要战役，刘备和孙权联合对抗曹操，最终曹操战败。",
            linked_entity_names=["赤壁之战", "刘备", "孙权", "曹操"],
            linked_edges=[("刘备", "曹操"), ("孙权", "曹操"), ("赤壁之战", "曹操")]
        ),
    ]
    
    return KnowledgeGraph(
        entities=entities,
        relationships=relationships,
        source_texts=source_texts
    )


def show_next_steps():
    """Show what users can do next."""
    print("\n6. Next Steps:")
    print("🔧 Try CLI: uv run kg-eval evaluate examples/sample_kg.json --output custom.html --format html")
    print("⚖️ Compare graphs: uv run kg-eval compare examples/sample_kg.json examples/sample_kg.json --output comparison.html")
    print("🔑 Add API key to .env for advanced semantic evaluation")
    print("📖 Check examples/README.md for more usage examples")


def main():
    """Main function demonstrating KG-Eval Python API usage."""
    print("KG-Eval Python API Demo")
    print("=" * 40)
    
    # 1. Load sample knowledge graph from file (same as CLI)
    print("\n1. Loading sample knowledge graph...")
    print("Loading knowledge graph from: examples/sample_kg.json")
    
    try:
        with open("examples/sample_kg.json", "r", encoding="utf-8") as f:
            kg_data = json.load(f)
        kg = KnowledgeGraph(**kg_data)
        print(f"Loaded: {kg}")
    except FileNotFoundError:
        print("❌ sample_kg.json not found!")
        print("💡 Creating sample data...")
        kg = create_sample_knowledge_graph()
        kg_data = kg.model_dump()
        with open("examples/sample_kg.json", "w", encoding="utf-8") as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)
        print("✅ Sample KG created and saved to: examples/sample_kg.json")
        print(f"Created: {kg}")
    
    # 2. Set up evaluator and perform evaluation
    print("\n2. Setting up evaluator...")
    evaluator = KGEvaluator()
    print("Evaluator initialized (without LLM referee)")
    
    # 3. Perform evaluation
    print("Starting evaluation...")
    results = evaluator.evaluate(kg)
    
    # 4. Generate reports (both formats)
    print("📄 Generating JSON report...")
    evaluator.report_generator.generate_json_report(results, "examples/sample_report.json")
    print("JSON report saved to: examples/sample_report.json")
    
    print("🌐 Generating HTML report...")
    evaluator.report_generator.generate_html_report(results, "examples/sample_report.html")
    print("HTML report saved to: examples/sample_report.html")
    
    # 5. Display summary (CLI-style output)
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    
    print("\nKey Metrics:")
    sr = results.get('scale_richness', {})
    si = results.get('structural_integrity', {})
    sq = results.get('semantic_quality', {})
    eff = results.get('efficiency', {})
    
    print(f"  Total Entities: {sr.get('entity_count', 0)}")
    print(f"  Total Relationships: {sr.get('relationship_count', 0)}")
    print(f"  Property Fill Rate: {sr.get('overall_property_fill_rate', 0.0):.4f}")
    print(f"  Graph Density: {si.get('graph_density', 0.0):.4f}")
    print(f"  Lcc Ratio: {si.get('largest_connected_component_ratio', 0.0):.4f}")
    print(f"  Singleton Ratio: {si.get('singleton_ratio', 0.0):.4f}")
    print(f"  Entity Normalization Score: {sq.get('entity_normalization_score', 0.0):.4f}")
    factual_precision = sq.get('factual_precision')
    if factual_precision is not None:
        print(f"  Factual Precision: {factual_precision:.4f}")
    else:
        print(f"  Factual Precision: Not evaluated (requires LLM referee)")
    print(f"  Knowledge Density: {eff.get('knowledge_density_per_chunk', 0.0):.4f}")
    
    print("\nRecommendations:")
    summary = evaluator.get_evaluation_summary(results)
    for i, recommendation in enumerate(summary["recommendations"], 1):
        print(f"  {i}. {recommendation}")
    
    print("\nDetailed reports saved to:")
    print("  - examples/sample_report.json")
    print("  - examples/sample_report.html")
    print("Evaluation completed successfully!")
    
    # 6. Show next steps
    show_next_steps()
    
    # 7. Auto-open HTML report in browser
    print("\n🌐 Opening HTML report in browser...")
    import subprocess
    import sys
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", "examples/sample_report.html"])
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.run(["xdg-open", "examples/sample_report.html"])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", "examples/sample_report.html"], shell=True)
        print("HTML report opened in default browser!")
    except Exception as e:
        print(f"Could not auto-open browser: {e}")
        print("Please manually open: examples/sample_report.html")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main() 