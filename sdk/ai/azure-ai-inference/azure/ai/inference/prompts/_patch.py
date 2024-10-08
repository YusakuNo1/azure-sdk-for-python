# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import azure.ai.inference.prompts as prompts
from ._prompt_config import PromptConfig


class PromptyTemplate:
    @staticmethod
    def load(
        file_path: str | None = None,
        prompty_uri: str | None = None,
        promtpy_name: str | None = None,
        version: str | None = None,
        api: str | None = None,
        model_name: str | None = None,
        prompt_template: str | None = None,
    ) -> PromptConfig:
        if file_path:
            prompty = prompts.load(file_path)
            return PromptConfig(prompty=prompty)
        elif prompty_uri:
            pass
        elif promtpy_name and version:
            pass
        elif api and model_name and prompt_template:
            pass
        
        raise ValueError("Please set at least one input")


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
