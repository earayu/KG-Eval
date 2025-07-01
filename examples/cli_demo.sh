#!/bin/bash

# KG-Eval CLI Demo Script
# This script demonstrates how to use the command line interface to evaluate knowledge graphs

set -e  # Exit on any error

echo "======================================"
echo "    KG-Eval CLI Demo"  
echo "======================================"
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' is not installed or not in PATH"
    echo "Please install uv first: https://github.com/astral-sh/uv"
    exit 1
fi

# Check if sample data exists
if [ ! -f "examples/sample_kg.json" ]; then
    echo "❌ Error: examples/sample_kg.json not found"
    echo "Please run this script from the KG-Eval root directory"
    exit 1
fi

echo "1. Evaluating sample knowledge graph with CLI..."
echo "🔍 Input: examples/sample_kg.json"
echo "📊 Auto-generating JSON + HTML reports..."
echo ""

# Run KG-Eval CLI command
uv run kg-eval evaluate examples/sample_kg.json

echo ""
echo "2. Reports generated:"
echo "  - sample_kg_evaluation_report.json (structured data)"
echo "  - sample_kg_evaluation_report.html (visualization)"
echo ""

# Auto-open HTML report in browser
echo "🌐 Opening HTML report in browser..."

# Detect OS and open accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open sample_kg_evaluation_report.html
    echo "HTML report opened in default browser (macOS)!"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open sample_kg_evaluation_report.html
    echo "HTML report opened in default browser (Linux)!"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start sample_kg_evaluation_report.html
    echo "HTML report opened in default browser (Windows)!"
else
    echo "⚠️  Could not auto-open browser (unknown OS: $OSTYPE)"
    echo "Please manually open: sample_kg_evaluation_report.html"
fi

echo ""
echo "======================================"
echo "CLI Demo completed! 🎉"
echo ""
echo "Try more CLI commands:"
echo "  # Compare multiple graphs:"
echo "  uv run kg-eval compare examples/sample_kg.json examples/sample_kg.json --output comparison.html"
echo ""
echo "  # Evaluate specific dimensions:"
echo "  uv run kg-eval evaluate examples/sample_kg.json --dimensions scale_richness structural_integrity"
echo ""
echo "  # Use custom output format:"
echo "  uv run kg-eval evaluate examples/sample_kg.json --output my_report.json --format json"
echo "======================================" 