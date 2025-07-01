"""
Example: Using KG-Eval with Custom Base URLs

This example demonstrates how to configure LLM referees with custom base URLs,
which is useful for:
- Using API proxies
- Self-hosted model deployments  
- Custom OpenAI-compatible endpoints
- Enterprise API gateways
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from kg_eval import OpenAIReferee, AnthropicReferee, KGEvaluator
from kg_eval import Entity, Relationship, SourceText, KnowledgeGraph


def create_simple_kg():
    """Create a simple knowledge graph for testing."""
    entities = [
        Entity(entity_name="Apple", entity_type="Company"),
        Entity(entity_name="iPhone", entity_type="Product"),
    ]
    
    relationships = [
        Relationship(
            source_entity_name="Apple",
            target_entity_name="iPhone",
            description="manufactures"
        )
    ]
    
    source_texts = [
        SourceText(
            content="Apple manufactures the iPhone.",
            linked_entity_names=["Apple", "iPhone"],
            linked_edges=[("Apple", "iPhone")]
        )
    ]
    
    return KnowledgeGraph(entities=entities, relationships=relationships, source_texts=source_texts)


def example_openai_configurations():
    """Show different OpenAI configuration examples."""
    print("OpenAI Configuration Examples:")
    print("=" * 40)
    
    # Example 1: Standard OpenAI API
    print("\n1. Standard OpenAI API:")
    print("   referee = OpenAIReferee(api_key='your-key')")
    
    # Example 2: OpenAI with proxy
    print("\n2. OpenAI via Proxy:")
    print("   referee = OpenAIReferee(")
    print("       api_key='your-key',")
    print("       base_url='https://your-proxy.com/v1'")
    print("   )")
    
    # Example 3: Azure OpenAI
    print("\n3. Azure OpenAI:")
    print("   referee = OpenAIReferee(")
    print("       api_key='your-azure-key',")
    print("       base_url='https://your-resource.openai.azure.com/',")
    print("       model='gpt-4'")
    print("   )")
    
    # Example 4: Custom OpenAI-compatible API
    print("\n4. Custom OpenAI-compatible API (e.g., LocalAI, Ollama):")
    print("   referee = OpenAIReferee(")
    print("       api_key='not-needed',  # Some local APIs don't need keys")
    print("       base_url='http://localhost:8080/v1',")
    print("       model='llama2'")
    print("   )")


def example_anthropic_configurations():
    """Show different Anthropic configuration examples."""
    print("\n\nAnthropic Configuration Examples:")
    print("=" * 40)
    
    # Example 1: Standard Anthropic API
    print("\n1. Standard Anthropic API:")
    print("   referee = AnthropicReferee(api_key='your-key')")
    
    # Example 2: Anthropic via proxy
    print("\n2. Anthropic via Proxy:")
    print("   referee = AnthropicReferee(")
    print("       api_key='your-key',")
    print("       base_url='https://your-anthropic-proxy.com'")
    print("   )")
    
    # Example 3: Custom model selection
    print("\n3. Custom Model Selection:")
    print("   referee = AnthropicReferee(")
    print("       api_key='your-key',")
    print("       model='claude-3-opus-20240229',")
    print("       max_tokens=100")
    print("   )")


def example_environment_variables():
    """Show how to use environment variables."""
    print("\n\nEnvironment Variables:")
    print("=" * 40)
    
    print("\n1. Set environment variables:")
    print("   export OPENAI_API_KEY='your-openai-key'")
    print("   export OPENAI_BASE_URL='https://your-proxy.com/v1'")
    print("   export ANTHROPIC_API_KEY='your-anthropic-key'")
    print("   export ANTHROPIC_BASE_URL='https://your-proxy.com'")
    
    print("\n2. Use in Python:")
    print("   # These will automatically use environment variables")
    print("   openai_key = os.getenv('OPENAI_API_KEY')")
    print("   openai_base_url = os.getenv('OPENAI_BASE_URL')")
    print("   ")
    print("   if openai_key:")
    print("       referee = OpenAIReferee(")
    print("           api_key=openai_key,")
    print("           base_url=openai_base_url")
    print("       )")
    
    print("\n3. Use in CLI:")
    print("   # Environment variables are automatically picked up")
    print("   kg-eval evaluate my_kg.json --output report.json")
    print("   ")
    print("   # Or override with command line options")
    print("   kg-eval evaluate my_kg.json \\")
    print("     --openai-model gpt-3.5-turbo \\")
    print("     --openai-base-url https://different-proxy.com/v1 \\")
    print("     --output report.json")


def example_real_usage():
    """Show a real usage example (without actual API calls)."""
    print("\n\nReal Usage Example:")
    print("=" * 40)
    
    kg = create_simple_kg()
    print(f"\nCreated sample KG: {kg}")
    
    # Example configuration (won't actually call API without valid keys)
    print("\nExample referee configuration:")
    print("# referee = OpenAIReferee(")
    print("#     api_key=os.getenv('OPENAI_API_KEY'),")
    print("#     base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),")
    print("#     model='gpt-4'")
    print("# )")
    print("# evaluator = KGEvaluator(llm_referee=referee)")
    
    # Use basic evaluator (no LLM referee)
    evaluator = KGEvaluator()
    results = evaluator.evaluate(kg, include_dimensions=['scale_richness', 'efficiency'])
    
    print(f"\nBasic evaluation results:")
    if 'scale_richness' in results:
        sr = results['scale_richness']
        print(f"  Entities: {sr.get('entity_count', 0)}")
        print(f"  Relationships: {sr.get('relationship_count', 0)}")
    
    print("\nNote: For semantic quality evaluation with factual precision")
    print("and contextual relevance, configure an LLM referee with valid API credentials.")


def main():
    """Main function demonstrating base_url configuration."""
    print("KG-Eval Base URL Configuration Examples")
    print("=" * 50)
    
    # Show different configuration examples
    example_openai_configurations()
    example_anthropic_configurations()
    example_environment_variables()
    example_real_usage()
    
    print("\n" + "=" * 50)
    print("Base URL Configuration Complete!")
    print("\nKey Benefits of Custom Base URLs:")
    print("• Use API proxies for better reliability")
    print("• Connect to self-hosted model deployments")
    print("• Work with OpenAI-compatible APIs (LocalAI, Ollama)")
    print("• Route through enterprise API gateways")
    print("• Use Azure OpenAI or other cloud providers")


if __name__ == "__main__":
    main() 