# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import math
import logging
from typing import Dict, Union, List, Optional, Any, Callable
from typing_extensions import override
from enum import Enum

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget

logger = logging.getLogger(__name__)


class InputType(Enum):
    """Supported input types for evaluators."""
    QUERY_RESPONSE = "query_response"
    RESPONSE_ONLY = "response_only"
    QUERY_RESPONSE_CONTEXT = "query_response_context"
    QUERY_RESPONSE_GROUND_TRUTH = "query_response_ground_truth"
    GROUND_TRUTH_RESPONSE = "ground_truth_response"
    CONVERSATION = "conversation"


class UnifiedEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    A unified evaluator that can handle multiple evaluation types through configuration.
    
    This class consolidates common patterns from individual evaluator classes while
    maintaining their specific behaviors through direct parameter configuration.
    
    For configuration examples of common built-in evaluators, see the 
    "Built-in Evaluator Configurations" section in UNIFIED_EVALUATOR_SUMMARY.md
    
    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param name: Name of the evaluator (used as result key).
    :type name: str
    :param prompty_file: Name of the prompty file for this evaluator.
    :type prompty_file: str
    :param evaluator_id: Unique identifier for the evaluator.
    :type evaluator_id: str
    :param threshold: The threshold for the evaluator.
    :type threshold: Union[int, float]
    :param input_types: List of supported input types.
    :type input_types: Optional[List[InputType]]
    :param supports_conversation: Whether this evaluator supports conversation input.
    :type supports_conversation: bool
    :param higher_is_better: Whether higher scores are better.
    :type higher_is_better: bool
    :param score_range: The expected score range as (min, max).
    :type score_range: tuple
    :param optional_params: List of optional parameter names.
    :type optional_params: Optional[List[str]]
    :param legacy_gpt_key: Whether to include legacy GPT-prefixed result key.
    :type legacy_gpt_key: bool
    :param include_details: Whether to include detailed output in results.
    :type include_details: bool
    :param custom_processor: Custom processing function for input handling.
    :type custom_processor: Optional[Callable]
    """

    @override
    def __init__(
        self, 
        model_config, 
        *, 
        name: str,
        prompty_file: str,
        evaluator_id: str,
        threshold: Union[int, float] = 3,
        input_types: Optional[List[InputType]] = None,
        supports_conversation: bool = True,
        higher_is_better: bool = True,
        score_range: tuple = (1, 5),
        optional_params: Optional[List[str]] = None,
        legacy_gpt_key: bool = False,
        include_details: bool = False,
        custom_processor: Optional[Callable] = None,
    ):
        # Store configuration parameters directly as instance variables
        self.name = name
        self.prompty_file_name = prompty_file
        self.evaluator_id = evaluator_id
        self.threshold_value = threshold
        self.input_types = input_types or [InputType.QUERY_RESPONSE]
        self.supports_conversation = supports_conversation
        self.higher_is_better = higher_is_better
        self.score_range = score_range
        self.optional_params = optional_params or []
        self.legacy_gpt_key = legacy_gpt_key
        self.include_details = include_details
        self.custom_processor = custom_processor
        
        # Set up the prompty file path
        current_dir = os.path.dirname(__file__)
        # Navigate to the specific evaluator directory
        evaluator_dir = os.path.join(os.path.dirname(current_dir), f"_{name}")
        prompty_path = os.path.join(evaluator_dir, prompty_file)
        
        # Set up class attributes expected by the framework
        self._PROMPTY_FILE = prompty_file
        self._RESULT_KEY = name
        self.id = evaluator_id
        
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=name,
            threshold=int(threshold),
            _higher_is_better=higher_is_better,
        )

    def _supports_input_type(self, **kwargs) -> InputType:
        """Determine which input type is being used."""
        has_query = "query" in kwargs
        has_response = "response" in kwargs
        has_context = "context" in kwargs
        has_ground_truth = "ground_truth" in kwargs
        has_conversation = "conversation" in kwargs
        
        if has_conversation:
            return InputType.CONVERSATION
        elif has_ground_truth and has_response:
            return InputType.GROUND_TRUTH_RESPONSE
        elif has_query and has_response and has_ground_truth:
            return InputType.QUERY_RESPONSE_GROUND_TRUTH
        elif has_query and has_response and has_context:
            return InputType.QUERY_RESPONSE_CONTEXT
        elif has_query and has_response:
            return InputType.QUERY_RESPONSE
        elif has_response:
            return InputType.RESPONSE_ONLY
        else:
            raise EvaluationException(
                message=f"Invalid input combination for {self.name} evaluator",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
            )

    def _validate_inputs(self, input_type: InputType):
        """Validate that the input type is supported by this evaluator."""
        if self.input_types and input_type not in self.input_types:
            supported = ", ".join([t.value for t in self.input_types])
            raise EvaluationException(
                message=f"{self.name} evaluator does not support input type {input_type.value}. Supported: {supported}",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
            )

    def __call__(self, **kwargs) -> Union[Dict[str, Union[str, float]], Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]]:
        """
        Unified call method that handles different input types based on configuration.
        
        Supports the following input patterns:
        - query + response: For basic query-response evaluation
        - response only: For response-only evaluation
        - query + response + context: For retrieval evaluation
        - query + response + ground_truth: For similarity evaluation
        - ground_truth + response: For completeness evaluation
        - conversation: For conversation-based evaluation
        
        :return: Dictionary containing evaluation results
        :rtype: Union[Dict[str, Union[str, float]], Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]]
        """
        input_type = self._supports_input_type(**kwargs)
        self._validate_inputs(input_type)
        
        # Apply custom processing if defined
        if self.custom_processor:
            kwargs = self.custom_processor(kwargs)
        
        return super().__call__(**kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        """Perform the evaluation with unified output formatting."""
        
        # Handle custom processing if needed
        if self.custom_processor:
            eval_input = self.custom_processor(eval_input)
        
        # Call the LLM
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        
        # Parse the response
        score = math.nan
        reason = ""
        details = {}
        
        if isinstance(llm_output, dict):
            # Try different score key formats
            score_keys = ["score", self.name, "rating"]
            for key in score_keys:
                if key in llm_output:
                    score = float(llm_output[key])
                    break
            
            # Try different reason key formats
            reason_keys = ["explanation", "reason", "reasoning", "chain_of_thought"]
            for key in reason_keys:
                if key in llm_output:
                    reason = llm_output[key]
                    break
            
            # Extract details if needed
            if self.include_details:
                details = {k: v for k, v in llm_output.items() 
                          if k not in score_keys + reason_keys}
        
        # Validate score
        min_score, max_score = self.score_range
        if not (min_score <= score <= max_score):
            if not math.isnan(score):
                logger.warning(f"Score {score} outside expected range {self.score_range}")
        
        # Determine pass/fail
        score_result = "pass" if score >= self._threshold else "fail"
        if math.isnan(score):
            score_result = "unknown"
        
        # Build result dictionary
        result = {
            self.name: score,
            f"{self.name}_result": score_result,
            f"{self.name}_threshold": self._threshold,
            f"{self.name}_reason": reason,
        }
        
        # Add legacy GPT key if needed for backward compatibility
        if self.legacy_gpt_key:
            result[f"gpt_{self.name}"] = score
        
        # Add details if configured
        if self.include_details and details:
            result["details"] = details
        
        return result
