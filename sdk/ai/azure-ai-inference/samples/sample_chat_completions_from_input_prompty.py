# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    TBD

USAGE:
    python sample_chat_completions_from_input_prompty.py
"""
# mypy: disable-error-code="union-attr"
# pyright: reportAttributeAccessIssue=false


def sample_chat_completions_from_input_prompty():
    import os
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.prompts import PromptyTemplate
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
        version = os.environ["AZURE_AI_CHAT_VERSION"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT', 'AZURE_AI_CHAT_KEY' or 'AZURE_AI_CHAT_VERSION'")
        print("Set them before running this sample.")
        exit()


    path = "./sample1.prompty"
    prompt_config = PromptyTemplate.load(file_path=path)

    input_variables = {
        # "input": "my first question",
        "input": "please tell me a joke about cats",
    }

    messages = prompt_config.render(input_variables=input_variables)

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        headers={"api-key": key},
        api_version=version,
    )

    # [START chat_completions]
    response = client.complete(
        {
            "messages": messages,
        }
    )
    # [END chat_completions]

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_from_input_prompty()
