# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Optional, Union
from typing_extensions import Literal

from openai._models import BaseModel

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration

from .aoai_grader import AzureOpenAIGrader


# TODO: Update to the definition from OpenAI's SDK when available
class EndpointGrader(BaseModel):
    headers: Optional[Dict[str, str]] = None
    """Optional HTTP headers to include in requests to the endpoint."""

    name: str
    """The name of the grader."""

    pass_threshold: Optional[float] = None
    """Optional threshold score above which the grade is considered passing."""

    rate_limit: Optional[int] = None
    """Optional rate limit for requests per second to the endpoint (Must be a positive integer)."""

    type: Literal["endpoint"]
    """The object type, which is always `endpoint`."""

    url: str
    """The HTTPS URL of the endpoint to call for grading."""


@experimental
class AzureOpenAIEndpointGrader(AzureOpenAIGrader):
    """Wrapper class for OpenAI's endpoint graders.

    :param model_config: The model configuration to use for the grader.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param name: The name of the grader.
    :type name: str
    :param url: The HTTPS URL of the endpoint to call for grading.
    :type url: str
    :param headers: Optional HTTP headers to include in requests to the endpoint.
    :type headers: Optional[Dict[str, str]]
    :param pass_threshold: Score threshold for pass/fail classification.
        Defaults to midpoint of range.
    :type pass_threshold: Optional[float]
    :param rate_limit: The rate limit for requests to the endpoint.
    :type rate_limit: Optional[int]
    :param kwargs: Additional keyword arguments to pass to the grader.
    :type kwargs: Any
    """

    id = "azureai://built-in/evaluators/azure-openai/endpoint_grader"
    _type = "endpoint"

    def __init__(
        self,
        *,
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        name: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        pass_threshold: Optional[float] = None,
        rate_limit: Optional[int] = None,
        **kwargs: Any,
    ):
        # Store pass_threshold as instance attribute
        self.pass_threshold = pass_threshold

        # Create OpenAI EndpointGrader instance
        grader_kwargs = {
            "name": name,
            "url": url,
            "headers": headers,
            "pass_threshold": pass_threshold,
            "rate_limit": rate_limit,
            "type": AzureOpenAIEndpointGrader._type,
        }

        grader = EndpointGrader(**grader_kwargs)

        super().__init__(model_config=model_config, grader_config=grader, **kwargs)
