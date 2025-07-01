"""
Sample usage of the KG-Eval framework.

This script demonstrates how to:
1. Create a knowledge graph using the KG-Eval data objects
2. Evaluate the knowledge graph using the KGEvaluator
3. Generate reports and visualizations
4. Configure LLM referees with custom base URLs
"""

import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from kg_eval import (
    Entity, Relationship, SourceText, KnowledgeGraph,
    KGEvaluator, OpenAIReferee, AnthropicReferee
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


def setup_llm_referee_examples():
    """Show examples of setting up LLM referees with various configurations."""
    print("\n7. LLM Referee Configuration Examples:")
    print("-" * 40)
    
    # Example 1: Standard OpenAI
    print("\n  Standard OpenAI Configuration:")
    print("    openai_key = os.getenv('OPENAI_API_KEY')")
    print("    referee = OpenAIReferee(api_key=openai_key)")
    
    # Example 2: OpenAI with custom base URL (for proxies)
    print("\n  OpenAI with Custom Base URL (proxy/custom deployment):")
    print("    openai_key = os.getenv('OPENAI_API_KEY')")
    print("    custom_base_url = 'https://your-proxy.com/v1'")
    print("    referee = OpenAIReferee(")
    print("        api_key=openai_key,")
    print("        base_url=custom_base_url,")
    print("        model='gpt-4'")
    print("    )")
    
    # Example 3: Anthropic with custom configuration
    print("\n  Anthropic with Custom Configuration:")
    print("    anthropic_key = os.getenv('ANTHROPIC_API_KEY')")
    print("    referee = AnthropicReferee(")
    print("        api_key=anthropic_key,")
    print("        model='claude-3-sonnet-20240229',")
    print("        base_url='https://your-anthropic-proxy.com'")
    print("    )")
    
    # Example 4: Using evaluator with custom referee
    print("\n  Using Evaluator with Custom Referee:")
    print("    evaluator = KGEvaluator(")
    print("        llm_referee=referee,")
    print("        sample_size=30,")
    print("        similarity_threshold=0.8")
    print("    )")


def main():
    """Main function demonstrating KG-Eval usage."""
    print("KG-Eval Framework Sample Usage")
    print("=" * 40)
    
    # 1. Create sample knowledge graph
    print("\n1. Creating sample knowledge graph...")
    kg = create_sample_knowledge_graph()
    print(f"Created: {kg}")
    
    # Save the sample KG to file for CLI usage
    kg_data = kg.model_dump()
    with open("examples/sample_kg.json", "w", encoding="utf-8") as f:
        json.dump(kg_data, f, indent=2, ensure_ascii=False)
    print("Sample KG saved to: examples/sample_kg.json")
    
    # 2. Set up evaluator (without LLM referee for this demo)
    print("\n2. Setting up evaluator...")
    evaluator = KGEvaluator()
    print("Evaluator initialized (without LLM referee)")
    
    # If you have API keys, you can uncomment and modify the following:
    # print("\n  Advanced LLM Referee Setup:")
    # openai_key = os.getenv("OPENAI_API_KEY")
    # openai_base_url = os.getenv("OPENAI_BASE_URL")  # Optional proxy URL
    # if openai_key:
    #     llm_referee = OpenAIReferee(
    #         api_key=openai_key,
    #         model="gpt-4",
    #         base_url=openai_base_url  # Can be None for standard API
    #     )
    #     evaluator = KGEvaluator(llm_referee=llm_referee)
    #     print(f"Evaluator initialized with OpenAI referee")
    #     if openai_base_url:
    #         print(f"  Using custom base URL: {openai_base_url}")
    
    # 3. Perform evaluation
    print("\n3. Performing evaluation...")
    results = evaluator.evaluate(kg)
    
    # 4. Display results
    print("\n4. Evaluation Results:")
    print("-" * 30)
    
    # Scale & Richness
    if 'scale_richness' in results:
        sr = results['scale_richness']
        print(f"\nScale & Richness:")
        print(f"  Entities: {sr.get('entity_count', 0)}")
        print(f"  Relationships: {sr.get('relationship_count', 0)}")
        print(f"  Property Fill Rate: {sr.get('overall_property_fill_rate', 0.0):.4f}")
        print(f"  Unique Relationship Types: {sr.get('unique_relationship_types', 0)}")
    
    # Structural Integrity
    if 'structural_integrity' in results:
        si = results['structural_integrity']
        print(f"\nStructural Integrity:")
        print(f"  Graph Density: {si.get('graph_density', 0.0):.4f}")
        print(f"  LCC Ratio: {si.get('largest_connected_component_ratio', 0.0):.4f}")
        print(f"  Singleton Ratio: {si.get('singleton_ratio', 0.0):.4f}")
        print(f"  Connected Components: {si.get('connected_components_count', 0)}")
    
    # Semantic Quality
    if 'semantic_quality' in results:
        sq = results['semantic_quality']
        print(f"\nSemantic Quality:")
        print(f"  Entity Normalization Score: {sq.get('entity_normalization_score', 0.0):.4f}")
        factual_precision = sq.get('factual_precision')
        if factual_precision is not None:
            print(f"  Factual Precision: {factual_precision:.4f}")
        else:
            print(f"  Factual Precision: Not evaluated (requires LLM referee)")
    
    # Efficiency
    if 'efficiency' in results:
        eff = results['efficiency']
        print(f"\nEfficiency:")
        print(f"  Knowledge Density: {eff.get('knowledge_density_per_chunk', 0.0):.4f}")
        print(f"  Productive Source Ratio: {eff.get('productive_source_ratio', 0.0):.4f}")
    
    # 5. Generate summary and recommendations
    print("\n5. Summary and Recommendations:")
    print("-" * 30)
    summary = evaluator.get_evaluation_summary(results)
    
    for i, recommendation in enumerate(summary["recommendations"], 1):
        print(f"  {i}. {recommendation}")
    
    # 6. Save detailed report
    print("\n6. Generating reports...")
    evaluator.evaluate_and_report(
        kg=kg,
        output_path="examples/sample_report.json",
        report_format="json"
    )
    
    evaluator.evaluate_and_report(
        kg=kg,
        output_path="examples/sample_report.html",
        report_format="html"
    )
    
    print("Reports saved to:")
    print("  - examples/sample_report.json")
    print("  - examples/sample_report.html")
    
    # 7. Show LLM referee configuration examples
    setup_llm_referee_examples()
    
    print("\n" + "=" * 40)
    print("Sample usage completed!")
    print("\nTo try the CLI:")
    print("  # Basic evaluation")
    print("  uv run kg-eval evaluate examples/sample_kg.json --output examples/cli_report.json")
    print("\n  # With custom OpenAI configuration")
    print("  export OPENAI_API_KEY='your-key'")
    print("  export OPENAI_BASE_URL='https://your-proxy.com/v1'  # Optional")
    print("  uv run kg-eval evaluate examples/sample_kg.json \\")
    print("    --openai-model gpt-3.5-turbo \\")
    print("    --output examples/full_report.json")
    print("\n  # Generate radar chart")
    print("  uv run kg-eval radar examples/sample_kg.json --output examples/radar_chart.html")


if __name__ == "__main__":
    main() 