# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import azure.ai.inference as sdk
import azure.ai.inference.prompty as Prompty

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



# from langchain_prompty.core import InvokerFactory
# # from langchain_prompty.langchain import create_chat_prompt
# # from langchain_prompty.parsers import PromptyChatParser
# # from langchain_prompty.renderers import MustacheRenderer
# # from .renderers import MustacheRenderer

# InvokerFactory().register_renderer("mustache", Prompty.MustacheRenderer)



class TestModelClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    def test_prompty(self, **kwargs):
        path = "/Users/weiwu/Workspace/1_Testing/TestAI/test-prompty/test.prompty"
        p = Prompty.load(path)

        inputs = {
            "input": "my first question",
        }

        print(p)

        parsed = Prompty.prepare(p, inputs)

        lc_messages = [] # TODO: will be removed
        for message in parsed:
            message_class = Prompty.RoleMap.get_message_class(message["role"])
            lc_messages.append(message_class(content=message["content"]))

        print(lc_messages)

        assert True
