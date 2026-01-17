# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and eval runs.

USAGE:
    python sample_evaluations_endpoint_grader.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b2" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.

How to setup your test endpoint:
    1) Install dependencies `pip install "fastapi[standard]" uvicorn ngrok`
    2) Create a file named `main.py` with the following file content
    3) Run the FastAPI app with `uvicorn main:app`
    4) Expose your local server to the internet using ngrok: `ngrok http 8000`
    5) Update `test_endpoint` below with the generated ngrok URL (e.g., https://479161d6fc22.ngrok-free.app)

# main.py
from fastapi import FastAPI

app = FastAPI()

# Root endpoint
@app.get("/")
def handle_root():
    return {"message": "Welcome to your FastAPI mini API!"}

# Test endpoint
@app.post("/evaluate/")
def handle_evaluate_payload(payload: dict):
    print(f"* * * Received arbitrary JSON payload: {payload}")
    return {"score": 0.9234}
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import time
from pprint import pprint
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
)
from openai.types.evals.create_eval_completions_run_data_source_param import (
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom
from dotenv import load_dotenv


load_dotenv()
file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)

project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
test_endpoint = "https://2258c4949892.ngrok-free.app/evaluate"  # only for testing

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):

    data_source_config = DataSourceConfigCustom(
        {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                    "context": {"type": "string"},
                    "ground_truth": {"type": "string"},
                },
                "required": [
                    "query",
                    "response",
                    "context",
                    "ground_truth",
                ],
            },
            "include_sample_schema": False,
        }
    )

    testing_criteria = [
        {
            "type": "endpoint",
            "name": "endpoint",
            "url": test_endpoint,
            "pass_threshold": 0.5,
        },
    ]

    print("Creating evaluation")
    eval_object = client.evals.create(
        name="OpenAI graders test - Endpoint Grader",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    print("Get evaluation by Id")
    eval_object_response = client.evals.retrieve(eval_object.id)
    print("Evaluation Response:")
    pprint(eval_object_response)

    source_file_content_content = SourceFileContentContent(
        item={
            "query": "sample-query",
            "response": "sample-response",
            "context": "sample-context",
            "ground_truth": "sample-ground-truth",
        },
    )
    source_file_content = SourceFileContent(
        type="file_content",
        content=[source_file_content_content],
    )

    print("Creating Eval Run")
    eval_run_object = client.evals.runs.create(
        eval_id=eval_object.id,
        name="Eval",
        metadata={"team": "eval-exp", "scenario": "notifications-v1"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=source_file_content,
        ),
    )
    print(f"Eval Run created (id: {eval_run_object.id}, name: {eval_run_object.name})")
    pprint(eval_run_object)

    print("Get Eval Run by Id")
    eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
    print("Eval Run Response:")
    pprint(eval_run_response)

    while True:
        run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
        if run.status == "completed" or run.status == "failed":
            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
            pprint(output_items)
            print(f"Eval Run Report URL: {run.report_url}")

            break
        time.sleep(5)
        print("Waiting for eval run to complete...")

    client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
