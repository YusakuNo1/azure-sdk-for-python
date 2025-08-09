# coding: utf-8
# type: ignore

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    These samples demonstrate usage of various classes and methods used to perform evaluation in the azure-ai-evaluation library.
    
USAGE:
    python evaluation_samples_evaluate.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_OPENAI_ENDPOINT
    2) AZURE_OPENAI_KEY
    3) AZURE_OPENAI_DEPLOYMENT
    4) AZURE_SUBSCRIPTION_ID
    5) AZURE_RESOURCE_GROUP_NAME
    6) AZURE_PROJECT_NAME

"""


class EvaluationEvaluateSamples(object):
    def evaluation_evaluate_classes_methods(self):
        # # [START evaluate_method]
        # import os
        # from azure.ai.evaluation import evaluate, RelevanceEvaluator, CoherenceEvaluator, IntentResolutionEvaluator

        # model_config = {
        #     "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        #     "api_key": os.environ.get("AZURE_OPENAI_KEY"),
        #     "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        # }

        # print(os.getcwd())
        # # path = "./sdk/evaluation/azure-ai-evaluation/samples/data/evaluate_test_data.jsonl"
        # path = "./data/evaluate_test_data.jsonl"

        # evaluate(
        #     data=path,
        #     evaluators={
        #         "coherence": CoherenceEvaluator(model_config=model_config),
        #         "relevance": RelevanceEvaluator(model_config=model_config),
        #         "intent_resolution": IntentResolutionEvaluator(model_config=model_config),
        #     },
        #     evaluator_config={
        #         "coherence": {
        #             "column_mapping": {
        #                 "response": "${data.response}",
        #                 "query": "${data.query}",
        #             },
        #         },
        #         "relevance": {
        #             "column_mapping": {
        #                 "response": "${data.response}",
        #                 "context": "${data.context}",
        #                 "query": "${data.query}",
        #             },
        #         },
        #     },
        #     # Example of using tags for tracking and organization
        #     tags={
        #         "experiment": "basic_evaluation",
        #         "model": "gpt-4",
        #         "dataset": "sample_qa_data",
        #         "environment": "development",
        #     },
        # )

        # # [END evaluate_method]

        # [START coherence_evaluator]
        import os
        from azure.ai.evaluation import CoherenceEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }
        coherence_evaluator = CoherenceEvaluator(model_config=model_config)
        response = coherence_evaluator(query="What is the capital of France?", response="Paris is the capital of France.")
        print(f"* * * {response}")
        # [END coherence_evaluator]

        # # [START intent_resolution_evaluator]
        # import os
        # from azure.ai.evaluation import CoherenceEvaluator

        # model_config = {
        #     "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        #     "api_key": os.environ.get("AZURE_OPENAI_KEY"),
        #     "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        # }
        # intent_resolution_evaluator = IntentResolutionEvaluator(model_config=model_config)
        # intent_resolution_evaluator(
        #     query="What is the opening hours of the Eiffel Tower?",
        #     response="Opening hours of the Eiffel Tower are 9:00 AM to 11:00 PM.",
        # )
        # # [END intent_resolution_evaluator]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    print("Loading samples in evaluation_samples_evaluate.py")
    sample = EvaluationEvaluateSamples()
    print("Samples loaded successfully!")
    print("Running samples in evaluation_samples_evaluate.py")
    sample.evaluation_evaluate_classes_methods()
    print("Samples ran successfully!")
