# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import azure.ai.inference as sdk
import azure.ai.prompty as Prompty

from model_inference_test_base import (
    ModelClientTestBase,
    ServicePreparerChatCompletions,
    ServicePreparerAOAIChatCompletions,
    ServicePreparerEmbeddings,
)
from azure.core.pipeline.transport import RequestsTransport
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential


class TestModelClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    def test_prompty(self, **kwargs):
        assert True
