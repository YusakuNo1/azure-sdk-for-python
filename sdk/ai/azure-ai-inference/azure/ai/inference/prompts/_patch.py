# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import azure.ai.inference.prompts as prompts
from ._prompt_config import PromptConfig


def get_prompt_config(
    file_path: str | None = None,
    template: str | None = None,
) -> PromptConfig:
    if not file_path and not template:
        raise ValueError("Please set at least one input")
    prompty = prompts.load(file_path)
    return PromptConfig(prompty=prompty)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
