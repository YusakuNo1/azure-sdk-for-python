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
    from azure.ai.inference.prompts import get_prompt_config
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()


    path = "./sample1.prompty"
    prompt_config = get_prompt_config(file_path=path)

    inputs = {
        "input": "my first question",
    }

    messages = prompt_config.render(inputs)

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # [START chat_completions]
    response = client.complete(
        {
            "messages": messages,
            # "messages": [
            #     {
            #         "role": "system",
            #         "content": "You are an AI assistant that helps people find information. Your replies are short, no more than two sentences.",
            #     },
            #     {
            #         "role": "user",
            #         "content": "What year was construction of the International Space Station mostly done?",
            #     },
            #     {
            #         "role": "assistant",
            #         "content": "The main construction of the International Space Station (ISS) was completed between 1998 and 2011. During this period, more than 30 flights by US space shuttles and 40 by Russian rockets were conducted to transport components and modules to the station.",
            #     },
            #     {
            #         "role": "user",
            #         "content": "And what was the estimated cost to build it?"
            #     },
            # ]
        }
    )
    # [END chat_completions]

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_from_input_prompty()
