#!/usr/bin/env python3
"""
Demonstration script showing how the UnifiedEvaluator can replace individual evaluator classes.

This script shows:
1. How to create evaluators using the unified approach
2. How the same API is maintained for backward compatibility
3. How new evaluators can be easily added through configuration
"""

import sys
import os

# Add the path to make imports work
sys.path.insert(0, '/Users/weiwu/Workspaces/Microsoft/azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation')

from azure.ai.evaluation._evaluators._unified._unified_evaluator import (
    UnifiedEvaluator,
    # EvaluatorConfig,
    InputType
)

def demonstrate_unified_evaluator():
    """Demonstrate how the unified evaluator works."""
    
    # Mock model config for demonstration
    mock_model_config = {
        "azure_endpoint": "https://example.openai.azure.com/",
        "api_key": "mock_key",
        "azure_deployment": "gpt-4",
        "api_version": "2024-02-15-preview"
    }
    
    print("=== UnifiedEvaluator Demonstration ===\n")
    
    # 1. Create evaluators using direct parameter initialization
    print("1. Creating evaluators with direct parameters:")
    
    try:
        coherence_eval = UnifiedEvaluator(
            mock_model_config,
            name="coherence",
            prompty_file="coherence.prompty",
            evaluator_id="azureai://built-in/evaluators/coherence",
            threshold=4,
            input_types=[InputType.QUERY_RESPONSE, InputType.CONVERSATION]
        )
        print(f"   ✓ Coherence evaluator: {coherence_eval.config.name}")
        print(f"     - Name: {coherence_eval.config.name}")
        print(f"     - Supported inputs: {[t.value for t in coherence_eval.config.input_types]}")
        
        fluency_eval = UnifiedEvaluator(
            mock_model_config,
            name="fluency",
            prompty_file="fluency.prompty",
            evaluator_id="azureai://built-in/evaluators/fluency",
            input_types=[InputType.RESPONSE_ONLY, InputType.CONVERSATION]
        )
        print(f"   ✓ Fluency evaluator: {fluency_eval.config.name}")
        
        relevance_eval = UnifiedEvaluator(
            mock_model_config,
            name="relevance",
            prompty_file="relevance.prompty",
            evaluator_id="azureai://built-in/evaluators/relevance",
            input_types=[InputType.QUERY_RESPONSE, InputType.CONVERSATION],
            legacy_gpt_key=True
        )
        print(f"   ✓ Relevance evaluator: {relevance_eval.config.name}")
        print(f"     - Has legacy GPT key: {relevance_eval.config.legacy_gpt_key}")
        
        similarity_eval = UnifiedEvaluator(
            mock_model_config,
            name="similarity",
            prompty_file="similarity.prompty",
            evaluator_id="azureai://built-in/evaluators/similarity",
            input_types=[InputType.QUERY_RESPONSE_GROUND_TRUTH],
            supports_conversation=False
        )
        print(f"   ✓ Similarity evaluator: {similarity_eval.config.name}")
        print(f"     - Supports conversation: {similarity_eval.config.supports_conversation}")
        
    except Exception as e:
        print(f"   Note: Evaluator creation failed (expected without real model): {e}")
    
    print("\n2. Creating evaluators using predefined configurations:")
    
    # 2. Create evaluators using the predefined configurations
    try:
        coherence_config = UnifiedEvaluator.EVALUATOR_CONFIGS["coherence"]
        direct_coherence = UnifiedEvaluator(
            mock_model_config,
            name=coherence_config.name,
            prompty_file=coherence_config.prompty_file,
            evaluator_id=coherence_config.evaluator_id,
            threshold=4,
            input_types=coherence_config.input_types,
            legacy_gpt_key=coherence_config.legacy_gpt_key
        )
        print(f"   ✓ Coherence evaluator from config created")
        
        fluency_config = UnifiedEvaluator.EVALUATOR_CONFIGS["fluency"]
        direct_fluency = UnifiedEvaluator(
            mock_model_config,
            name=fluency_config.name,
            prompty_file=fluency_config.prompty_file,
            evaluator_id=fluency_config.evaluator_id,
            input_types=fluency_config.input_types
        )
        print(f"   ✓ Fluency evaluator from config created")
        
    except Exception as e:
        print(f"   Note: Config-based creation failed (expected without real model): {e}")
    
    print("\n3. Creating custom evaluator configurations:")
    
    # 3. Demonstrate input type detection
    test_inputs = [
        {"query": "test", "response": "test"},
        {"response": "test"},
        {"query": "test", "response": "test", "context": "test"},
        {"query": "test", "response": "test", "ground_truth": "test"},
        {"ground_truth": "test", "response": "test"},
        {"conversation": {"messages": []}},
    ]
    
    # Create a temporary evaluator instance to test input detection
    try:
        temp_eval = UnifiedEvaluator(
            mock_model_config,
            name="test",
            prompty_file="test.prompty",
            evaluator_id="test://evaluator"
        )
        
        for test_input in test_inputs:
            try:
                input_type = temp_eval._supports_input_type(**test_input)
                input_keys = ", ".join(test_input.keys())
                print(f"   ✓ Input [{input_keys}] -> {input_type.value}")
            except Exception as e:
                print(f"   ✗ Input {test_input.keys()} failed: {e}")
    except Exception as e:
        print(f"   Note: Input type detection test failed (expected): {e}")
    
    print("\n5. Configuration comparison:")
    print("   Original approach vs Unified approach:")
    print("   - CoherenceEvaluator      -> UnifiedEvaluator with coherence parameters")
    print("   - FluencyEvaluator        -> UnifiedEvaluator with fluency parameters")
    print("   - RelevanceEvaluator      -> UnifiedEvaluator with relevance parameters")
    print("   - SimilarityEvaluator     -> UnifiedEvaluator with similarity parameters")
    print("   - RetrievalEvaluator      -> UnifiedEvaluator with retrieval parameters")
    print("   - ResponseCompletenessEvaluator -> UnifiedEvaluator with response_completeness parameters")
    
    print("\n6. Benefits of the unified approach:")
    print("   ✓ Single class for all evaluator types")
    print("   ✓ Direct parameter specification")
    print("   ✓ No redundant factory methods")
    print("   ✓ Simplified API")
    print("   ✓ Easy to add new evaluators")
    print("   ✓ Centralized logic and error handling")
    
    print("\n=== Demonstration Complete ===")

def show_code_reduction():
    """Show how much code is reduced by using the unified approach."""
    
    print("\n=== Code Reduction Analysis ===")
    
    original_files = [
        "_coherence/_coherence.py",
        "_fluency/_fluency.py", 
        "_relevance/_relevance.py",
        "_similarity/_similarity.py",
        "_retrieval/_retrieval.py",
        "_response_completeness/_response_completeness.py"
    ]
    
    print("Original approach:")
    print(f"   - {len(original_files)} separate evaluator files")
    print("   - Each with ~100-200 lines of code")
    print("   - Duplicated patterns across files")
    print("   - Total: ~600-1200 lines of code")
    
    print("\nUnified approach:")
    print("   - 1 unified evaluator file (~400 lines)")
    print("   - Configuration-driven behavior")
    print("   - Shared common logic")
    print("   - Easy to extend")
    
    print("\nCode reduction: ~50-75% fewer lines")
    print("Maintenance effort: Significantly reduced")

if __name__ == "__main__":
    demonstrate_unified_evaluator()
    show_code_reduction()
