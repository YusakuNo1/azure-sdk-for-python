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
    EvaluatorConfig,
    InputType,
    create_coherence_evaluator,
    create_fluency_evaluator,
    create_relevance_evaluator,
    create_similarity_evaluator,
    create_retrieval_evaluator,
    create_response_completeness_evaluator
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
    
    # 1. Create evaluators using factory methods (maintains backward compatibility)
    print("1. Creating evaluators using factory methods:")
    
    try:
        coherence_eval = create_coherence_evaluator(mock_model_config, threshold=4)
        print(f"   ✓ Coherence evaluator: {coherence_eval.config.name}")
        print(f"     - Result key: {coherence_eval.config.result_key}")
        print(f"     - Supported inputs: {[t.value for t in coherence_eval.config.input_types]}")
        
        fluency_eval = create_fluency_evaluator(mock_model_config)
        print(f"   ✓ Fluency evaluator: {fluency_eval.config.name}")
        
        relevance_eval = create_relevance_evaluator(mock_model_config)
        print(f"   ✓ Relevance evaluator: {relevance_eval.config.name}")
        print(f"     - Has legacy GPT key: {relevance_eval.config.legacy_gpt_key}")
        
        similarity_eval = create_similarity_evaluator(mock_model_config)
        print(f"   ✓ Similarity evaluator: {similarity_eval.config.name}")
        print(f"     - Supports conversation: {similarity_eval.config.supports_conversation}")
        
    except Exception as e:
        print(f"   Note: Evaluator creation failed (expected without real model): {e}")
    
    print("\n2. Creating evaluators directly with UnifiedEvaluator:")
    
    # 2. Create evaluators using the class methods
    try:
        direct_coherence = UnifiedEvaluator.create_coherence_evaluator(mock_model_config)
        print(f"   ✓ Direct coherence evaluator created")
        
        direct_fluency = UnifiedEvaluator.create_fluency_evaluator(mock_model_config)
        print(f"   ✓ Direct fluency evaluator created")
        
    except Exception as e:
        print(f"   Note: Direct creation failed (expected without real model): {e}")
    
    print("\n3. Creating custom evaluator configurations:")
    
    # 3. Show how to create a custom evaluator
    custom_config = EvaluatorConfig(
        name="custom_quality",
        prompty_file="custom_quality.prompty",
        result_key="quality",
        evaluator_id="custom://evaluators/quality",
        default_threshold=4,
        input_types=[InputType.QUERY_RESPONSE, InputType.CONVERSATION],
        score_range=(1, 10),
        legacy_gpt_key=False,
        include_details=True
    )
    
    print(f"   ✓ Custom config created: {custom_config.name}")
    print(f"     - Score range: {custom_config.score_range}")
    print(f"     - Include details: {custom_config.include_details}")
    
    print("\n4. Showing input type detection:")
    
    # 4. Demonstrate input type detection
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
        temp_eval = UnifiedEvaluator(mock_model_config, config=custom_config)
        
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
    print("   Original evaluators vs Unified approach:")
    print("   - CoherenceEvaluator      -> UnifiedEvaluator with coherence config")
    print("   - FluencyEvaluator        -> UnifiedEvaluator with fluency config")
    print("   - RelevanceEvaluator      -> UnifiedEvaluator with relevance config")
    print("   - SimilarityEvaluator     -> UnifiedEvaluator with similarity config")
    print("   - RetrievalEvaluator      -> UnifiedEvaluator with retrieval config")
    print("   - ResponseCompletenessEvaluator -> UnifiedEvaluator with response_completeness config")
    
    print("\n6. Benefits of the unified approach:")
    print("   ✓ Reduced code duplication")
    print("   ✓ Consistent API across evaluators")
    print("   ✓ Easy to add new evaluators through configuration")
    print("   ✓ Centralized output formatting")
    print("   ✓ Unified error handling")
    print("   ✓ Maintains backward compatibility")
    
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
