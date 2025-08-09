# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import math
import logging
from typing import Dict, Union, List, Optional, Any, Callable
from typing_extensions import overload, override
from dataclasses import dataclass
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


@dataclass
class EvaluatorConfig:
    """Configuration for a unified evaluator."""
    name: str
    prompty_file: str
    result_key: str
    evaluator_id: str
    default_threshold: Union[int, float] = 3
    input_types: Optional[List[InputType]] = None
    supports_conversation: bool = True
    higher_is_better: bool = True
    score_range: tuple = (1, 5)
    optional_params: Optional[List[str]] = None
    legacy_gpt_key: bool = False
    include_details: bool = False
    custom_processor: Optional[Callable] = None
    
    def __post_init__(self):
        if self.input_types is None:
            self.input_types = [InputType.QUERY_RESPONSE]
        if self.optional_params is None:
            self.optional_params = []


class UnifiedEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    A unified evaluator that can handle multiple evaluation types through configuration.
    
    This class consolidates common patterns from individual evaluator classes while
    maintaining their specific behaviors through configuration.
    
    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param config: Configuration object defining evaluator behavior.
    :type config: EvaluatorConfig
    :param threshold: The threshold for the evaluator. Uses config default if not provided.
    :type threshold: Union[int, float]
    """
    
    # Predefined configurations for common evaluators
    EVALUATOR_CONFIGS = {
        "coherence": EvaluatorConfig(
            name="coherence",
            prompty_file="coherence.prompty",
            result_key="coherence",
            evaluator_id="azureai://built-in/evaluators/coherence",
            input_types=[InputType.QUERY_RESPONSE, InputType.CONVERSATION]
        ),
        "fluency": EvaluatorConfig(
            name="fluency",
            prompty_file="fluency.prompty",
            result_key="fluency",
            evaluator_id="azureai://built-in/evaluators/fluency",
            input_types=[InputType.RESPONSE_ONLY, InputType.CONVERSATION]
        ),
        "relevance": EvaluatorConfig(
            name="relevance",
            prompty_file="relevance.prompty",
            result_key="relevance",
            evaluator_id="azureai://built-in/evaluators/relevance",
            input_types=[InputType.QUERY_RESPONSE, InputType.CONVERSATION],
            legacy_gpt_key=True
        ),
        "similarity": EvaluatorConfig(
            name="similarity",
            prompty_file="similarity.prompty",
            result_key="similarity",
            evaluator_id="azureai://built-in/evaluators/similarity",
            input_types=[InputType.QUERY_RESPONSE_GROUND_TRUTH],
            supports_conversation=False
        ),
        "retrieval": EvaluatorConfig(
            name="retrieval",
            prompty_file="retrieval.prompty",
            result_key="retrieval",
            evaluator_id="azureai://built-in/evaluators/retrieval",
            input_types=[InputType.QUERY_RESPONSE_CONTEXT, InputType.CONVERSATION]
        ),
        "response_completeness": EvaluatorConfig(
            name="response_completeness",
            prompty_file="response_completeness.prompty",
            result_key="response_completeness",
            evaluator_id="azureai://built-in/evaluators/response_completeness",
            input_types=[InputType.GROUND_TRUTH_RESPONSE, InputType.CONVERSATION]
        )
    }

    @classmethod
    def create_coherence_evaluator(cls, model_config, *, threshold=3):
        """Create a coherence evaluator instance."""
        return cls(model_config, config=cls.EVALUATOR_CONFIGS["coherence"], threshold=threshold)
    
    @classmethod
    def create_fluency_evaluator(cls, model_config, *, threshold=3):
        """Create a fluency evaluator instance."""
        return cls(model_config, config=cls.EVALUATOR_CONFIGS["fluency"], threshold=threshold)
    
    @classmethod
    def create_relevance_evaluator(cls, model_config, *, threshold=3):
        """Create a relevance evaluator instance."""
        return cls(model_config, config=cls.EVALUATOR_CONFIGS["relevance"], threshold=threshold)
    
    @classmethod
    def create_similarity_evaluator(cls, model_config, *, threshold=3):
        """Create a similarity evaluator instance."""
        return cls(model_config, config=cls.EVALUATOR_CONFIGS["similarity"], threshold=threshold)
    
    @classmethod
    def create_retrieval_evaluator(cls, model_config, *, threshold=3):
        """Create a retrieval evaluator instance."""
        return cls(model_config, config=cls.EVALUATOR_CONFIGS["retrieval"], threshold=threshold)
    
    @classmethod
    def create_response_completeness_evaluator(cls, model_config, *, threshold=3):
        """Create a response completeness evaluator instance."""
        return cls(model_config, config=cls.EVALUATOR_CONFIGS["response_completeness"], threshold=threshold)

    @override
    def __init__(self, model_config, *, config: EvaluatorConfig, threshold: Optional[Union[int, float]] = None):
        self.config = config
        if threshold is None:
            threshold = config.default_threshold
        
        # Set up the prompty file path
        current_dir = os.path.dirname(__file__)
        # Navigate to the specific evaluator directory
        evaluator_dir = os.path.join(os.path.dirname(current_dir), f"_{config.name}")
        prompty_path = os.path.join(evaluator_dir, config.prompty_file)
        
        # Set up class attributes expected by the framework
        self._PROMPTY_FILE = config.prompty_file
        self._RESULT_KEY = config.result_key
        self.id = config.evaluator_id
        
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=config.result_key,
            threshold=int(threshold),
            _higher_is_better=config.higher_is_better,
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
                message=f"Invalid input combination for {self.config.name} evaluator",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
            )

    def _validate_inputs(self, input_type: InputType):
        """Validate that the input type is supported by this evaluator."""
        if self.config.input_types and input_type not in self.config.input_types:
            supported = ", ".join([t.value for t in self.config.input_types])
            raise EvaluationException(
                message=f"{self.config.name} evaluator does not support input type {input_type.value}. Supported: {supported}",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
            )

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate for query and response input."""

    @overload
    def __call__(
        self,
        *,
        response: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate for response-only input."""

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
        context: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate for query, response, and context input."""

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
        ground_truth: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate for query, response, and ground truth input."""

    @overload
    def __call__(
        self,
        *,
        ground_truth: str,
        response: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate for ground truth and response input."""

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate for conversation input."""

    @override
    def __call__(self, *args, **kwargs):
        """
        Unified call method that handles different input types based on configuration.
        """
        input_type = self._supports_input_type(**kwargs)
        self._validate_inputs(input_type)
        
        # Apply custom processing if defined
        if self.config.custom_processor:
            kwargs = self.config.custom_processor(kwargs)
        
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        """Perform the evaluation with unified output formatting."""
        
        # Handle custom processing if needed
        if self.config.custom_processor:
            eval_input = self.config.custom_processor(eval_input)
        
        # Call the LLM
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        
        # Parse the response
        score = math.nan
        reason = ""
        details = {}
        
        if isinstance(llm_output, dict):
            # Try different score key formats
            score_keys = ["score", self.config.result_key, "rating"]
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
            if self.config.include_details:
                details = {k: v for k, v in llm_output.items() 
                          if k not in score_keys + reason_keys}
        
        # Validate score
        min_score, max_score = self.config.score_range
        if not (min_score <= score <= max_score):
            if not math.isnan(score):
                logger.warning(f"Score {score} outside expected range {self.config.score_range}")
        
        # Determine pass/fail
        score_result = "pass" if score >= self._threshold else "fail"
        if math.isnan(score):
            score_result = "unknown"
        
        # Build result dictionary
        result = {
            self.config.result_key: score,
            f"{self.config.result_key}_result": score_result,
            f"{self.config.result_key}_threshold": self._threshold,
            f"{self.config.result_key}_reason": reason,
        }
        
        # Add legacy GPT key if needed for backward compatibility
        if self.config.legacy_gpt_key:
            result[f"gpt_{self.config.result_key}"] = score
        
        # Add details if configured
        if self.config.include_details and details:
            result["details"] = details
        
        return result


# Create factory functions for backward compatibility
def create_coherence_evaluator(model_config, *, threshold=3):
    """Create a CoherenceEvaluator using the unified evaluator."""
    return UnifiedEvaluator.create_coherence_evaluator(model_config, threshold=threshold)

def create_fluency_evaluator(model_config, *, threshold=3):
    """Create a FluencyEvaluator using the unified evaluator."""
    return UnifiedEvaluator.create_fluency_evaluator(model_config, threshold=threshold)

def create_relevance_evaluator(model_config, *, threshold=3):
    """Create a RelevanceEvaluator using the unified evaluator."""
    return UnifiedEvaluator.create_relevance_evaluator(model_config, threshold=threshold)

def create_similarity_evaluator(model_config, *, threshold=3):
    """Create a SimilarityEvaluator using the unified evaluator."""
    return UnifiedEvaluator.create_similarity_evaluator(model_config, threshold=threshold)

def create_retrieval_evaluator(model_config, *, threshold=3):
    """Create a RetrievalEvaluator using the unified evaluator."""
    return UnifiedEvaluator.create_retrieval_evaluator(model_config, threshold=threshold)

def create_response_completeness_evaluator(model_config, *, threshold=3):
    """Create a ResponseCompletenessEvaluator using the unified evaluator."""
    return UnifiedEvaluator.create_response_completeness_evaluator(model_config, threshold=threshold)
